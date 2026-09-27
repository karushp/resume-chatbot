import os
import time
from collections import defaultdict, deque

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
load_dotenv()

import config

# Load API keys from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Please set the GROQ_API_KEY environment variable.")
if not COHERE_API_KEY:
    raise ValueError("Please set the COHERE_API_KEY environment variable.")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def build_resume_chunks(
    resume_text,
    chunk_size=config.CHUNK_SIZE,
    chunk_overlap=config.CHUNK_OVERLAP,
    min_chunk_chars=config.MIN_CHUNK_CHARS,
):
    """Split markdown by headers so role titles stay with their bullets."""
    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("##", "section"),
            ("###", "role"),
        ]
    )
    header_docs = md_splitter.split_text(resume_text)

    chunks = []
    for doc in header_docs:
        header_parts = [doc.metadata[k] for k in ("section", "role") if k in doc.metadata]
        prefix = (" — ".join(header_parts) + "\n\n") if header_parts else ""
        body = doc.page_content.strip()
        combined = prefix + body

        if len(combined) <= chunk_size:
            chunks.append(combined)
            continue

        # Keep the section/role label on every sub-chunk if a section is still large
        body_limit = max(300, chunk_size - len(prefix))
        sub_splitter = RecursiveCharacterTextSplitter(
            chunk_size=body_limit,
            chunk_overlap=chunk_overlap,
        )
        for part in sub_splitter.split_text(body):
            chunks.append(prefix + part)

    # Merge any leftover tiny fragments into the following chunk
    merged = []
    for chunk in chunks:
        if merged and len(merged[-1]) < min_chunk_chars:
            merged[-1] = merged[-1].rstrip() + "\n\n" + chunk
        else:
            merged.append(chunk)
    if len(merged) >= 2 and len(merged[-1]) < min_chunk_chars:
        merged[-2] = merged[-2].rstrip() + "\n\n" + merged[-1]
        merged.pop()

    return merged

# --- Step 1: Load resume text ---
with open(config.RESUME_FILE, "r", encoding="utf-8") as f:
    text = f.read()

# --- Step 2: Split into chunks ---
chunks = build_resume_chunks(text)

# --- Step 3: Embed chunks and store in FAISS ---
embeddings = CohereEmbeddings(
    cohere_api_key=COHERE_API_KEY,
    model=config.COHERE_EMBED_MODEL,
)

# Check if we need to rebuild the FAISS index
resume_mtime = os.path.getmtime(config.RESUME_FILE)
index_exists = os.path.exists(config.FAISS_INDEX_PATH)

if index_exists:
    index_mtime = os.path.getmtime(config.FAISS_INDEX_PATH)
    if resume_mtime > index_mtime:
        print("📄 Resume file updated, rebuilding FAISS index...")
        db = FAISS.from_texts(chunks, embeddings)
        db.save_local(config.FAISS_INDEX_PATH)
        print("✅ FAISS index rebuilt and saved")
    else:
        print("📂 Loading existing FAISS index...")
        try:
            db = FAISS.load_local(
                config.FAISS_INDEX_PATH,
                embeddings,
                allow_dangerous_deserialization=True,
            )
            print("✅ FAISS index loaded successfully")
        except Exception as e:
            print(f"⚠️ Error loading FAISS index: {e}")
            print("🔄 Rebuilding FAISS index...")
            db = FAISS.from_texts(chunks, embeddings)
            db.save_local(config.FAISS_INDEX_PATH)
            print("✅ FAISS index rebuilt and saved")
else:
    print("🆕 Creating new FAISS index...")
    db = FAISS.from_texts(chunks, embeddings)
    db.save_local(config.FAISS_INDEX_PATH)
    print("✅ FAISS index created and saved")

_rate_hits = defaultdict(deque)

def client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"

def is_rate_limited(ip):
    now = time.time()
    window_start = now - config.RATE_LIMIT_WINDOW_SECONDS
    hits = _rate_hits[ip]
    while hits and hits[0] < window_start:
        hits.popleft()
    if len(hits) >= config.RATE_LIMIT_REQUESTS:
        return True
    hits.append(now)
    return False

def sanitize_history(history):
    """Keep only valid user/assistant turns, capped at HISTORY_LIMIT."""
    if not isinstance(history, list):
        return []
    cleaned = []
    for turn in history:
        if not isinstance(turn, dict):
            continue
        role = turn.get("role")
        content = (turn.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            cleaned.append({
                "role": role,
                "content": content[:config.MAX_HISTORY_MESSAGE_CHARS],
            })
    return cleaned[-config.HISTORY_LIMIT:]

def friendly_llm_error(status_code=None):
    """User-facing message for upstream LLM failures (no raw provider payloads)."""
    if status_code == 401:
        return "The chat service is misconfigured. Please try again later."
    if status_code == 403:
        return "The AI service is temporarily unavailable from this network. Please try again later."
    if status_code == 429:
        return "The AI service is busy right now. Please wait a moment and try again."
    if status_code is not None and status_code >= 500:
        return "The AI service had a problem. Please try again in a moment."
    return "Something went wrong generating a reply. Please try again."

# --- Step 4: Helper function to call Groq API ---
def groq_generate(query, context, history=None):
    """Returns (answer, None) on success, or (None, user_facing_error) on failure."""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_prompt = f"""
{config.BASE_SYSTEM_INSTRUCTION}

Resume context:
{context}
""".strip()

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(sanitize_history(history))
        messages.append({"role": "user", "content": query})
        
        data = {
            "messages": messages,
            "model": config.GROQ_MODEL,
            "temperature": config.GROQ_TEMPERATURE,
            "max_tokens": config.GROQ_MAX_TOKENS,
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=config.GROQ_TIMEOUT_SECONDS,
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            if isinstance(content, str) and content.strip():
                return content.strip(), None
            return None, friendly_llm_error()

        print(f"Groq API error {response.status_code}: {response.text[:500]}")
        return None, friendly_llm_error(response.status_code)
            
    except requests.Timeout:
        return None, "The AI service took too long to respond. Please try again."
    except Exception as e:
        print(f"Groq API exception: {e}")
        return None, friendly_llm_error()

# --- Step 5: API Endpoint ---
@app.route("/ask", methods=["POST"])
def ask():
    if is_rate_limited(client_ip()):
        return jsonify({"error": "Too many requests. Please wait a moment and try again."}), 429

    body = request.json or {}
    query = body.get("query")
    if not isinstance(query, str):
        return jsonify({"error": "Missing or invalid query"}), 400

    query = query.strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400
    if len(query) > config.MAX_QUERY_CHARS:
        return jsonify({"error": f"Query too long (max {config.MAX_QUERY_CHARS} characters)"}), 400

    history = sanitize_history(body.get("history", []))
    docs = db.similarity_search(query, k=config.RETRIEVAL_K)
    context = "\n\n".join([d.page_content for d in docs])
    answer, error = groq_generate(query, context, history)
    if error:
        return jsonify({"error": error}), 502
    return jsonify({"answer": answer})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)

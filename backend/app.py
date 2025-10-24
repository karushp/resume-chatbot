import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
from langchain.text_splitter import CharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
load_dotenv()

# Load API keys from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Please set the GROQ_API_KEY environment variable.")
if not COHERE_API_KEY:
    raise ValueError("Please set the COHERE_API_KEY environment variable.")

# Configuration
PERSON_NAME = "Karush Pradhan"  # Change this to the person's name
RESUME_FILE = "data/karush_resume.pdf"  # Change this to your resume file

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- Step 1: Load resume text ---
text = ""
with open(RESUME_FILE, "rb") as f:
    reader = PyPDF2.PdfReader(f)
    for page in reader.pages:
        text += page.extract_text()

# --- Step 2: Split into chunks ---
splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=30)
chunks = splitter.split_text(text)

# --- Step 3: Embed chunks and store in FAISS ---
embeddings = CohereEmbeddings(
    cohere_api_key=COHERE_API_KEY,
    model="embed-english-v3.0"
)

# Check if we need to rebuild the FAISS index
FAISS_INDEX_PATH = "faiss_index"
resume_mtime = os.path.getmtime(RESUME_FILE)
index_exists = os.path.exists(FAISS_INDEX_PATH)

if index_exists:
    index_mtime = os.path.getmtime(FAISS_INDEX_PATH)
    if resume_mtime > index_mtime:
        print("📄 Resume file updated, rebuilding FAISS index...")
        db = FAISS.from_texts(chunks, embeddings)
        db.save_local(FAISS_INDEX_PATH)
        print("✅ FAISS index rebuilt and saved")
    else:
        print("📂 Loading existing FAISS index...")
        try:
            db = FAISS.load_local(FAISS_INDEX_PATH, embeddings)
            print("✅ FAISS index loaded successfully")
        except Exception as e:
            print(f"⚠️ Error loading FAISS index: {e}")
            print("🔄 Rebuilding FAISS index...")
            db = FAISS.from_texts(chunks, embeddings)
            db.save_local(FAISS_INDEX_PATH)
            print("✅ FAISS index rebuilt and saved")
else:
    print("🆕 Creating new FAISS index...")
    db = FAISS.from_texts(chunks, embeddings)
    db.save_local(FAISS_INDEX_PATH)
    print("✅ FAISS index created and saved")

# --- Step 4: Helper function to call Groq API ---
def groq_generate(query, context):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": f"You are Karush's friendly chatbot assistant. Be conversational, engaging, and helpful when answering questions about Karush based on this resume information: {context}. \n\nGuidelines:\n- Keep responses concise and natural, like you're chatting with a friend\n- Use bullet points or short paragraphs to break up information\n- Ask follow-up questions when appropriate\n- Be enthusiastic but not overly formal\n- If someone asks about hiring, be humble but confident\n- Use casual language like 'I've got', 'I'm really into', 'I love working with'\n- Don't start responses with 'Karush' unless specifically asked about him by name\n- Make it feel like a real conversation, not a formal interview"
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "model": "llama-3.1-8b-instant",
            "temperature": 0.8,
            "max_tokens": 800
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Error from Groq API: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"⚠️ Error from Groq API: {str(e)}"

# --- Step 5: API Endpoint ---
@app.route("/ask", methods=["POST"])
def ask():
    query = request.json["query"]
    docs = db.similarity_search(query, k=2)
    context = " ".join([d.page_content for d in docs])
    answer = groq_generate(query, context)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
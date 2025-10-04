import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
load_dotenv()

# Load Groq API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Please set the GROQ_API_KEY environment variable.")

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
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(text)

# --- Step 3: Embed chunks and store in FAISS ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_texts(chunks, embeddings)

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
                    "content": f"You are Karush's personal assistant. Answer questions naturally and conversationally about Karush based on this resume information: {context}. Respond as if you're speaking directly to the person asking, without starting with 'KP' or 'Karush' unless specifically asked about him by name."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "model": "llama-3.1-8b-instant",
            "temperature": 0.7,
            "max_tokens": 1000
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
    app.run(host="0.0.0.0", port=5001)
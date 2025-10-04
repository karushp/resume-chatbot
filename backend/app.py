import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from huggingface_hub import InferenceClient

from dotenv import load_dotenv
load_dotenv()

# Load Hugging Face API token from environment
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("Please set the HF_API_TOKEN environment variable.")

# Configuration
PERSON_NAME = "Karush Pradhan"  # Change this to the person's name
RESUME_FILE = "data/karush_resume.pdf"  # Change this to your resume file

# Initialize Hugging Face client with featherless-ai provider
client = InferenceClient(
    provider="featherless-ai",
    api_key=HF_API_TOKEN,
)

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

# --- Step 4: Helper function to call Hugging Face API ---
def hf_generate(query, context):
    try:
        completion = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=[
                {
                    "role": "system",
                    "content": f"You are Karush's personal assistant. Answer questions naturally and conversationally about Karush based on this resume information: {context}. Respond as if you're speaking directly to the person asking, without starting with 'KP' or 'Karush' unless specifically asked about him by name."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error from Hugging Face API: {str(e)}"

# --- Step 5: API Endpoint ---
@app.route("/ask", methods=["POST"])
def ask():
    query = request.json["query"]
    docs = db.similarity_search(query, k=2)
    context = " ".join([d.page_content for d in docs])
    answer = hf_generate(query, context)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
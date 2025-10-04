from flask import Flask, request, jsonify
import PyPDF2
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from openai import OpenAI

client = OpenAI()
app = Flask(__name__)

# --- Load resume + build FAISS DB ---
text = ""
with open("resume.pdf", "rb") as f:
    reader = PyPDF2.PdfReader(f)
    for page in reader.pages:
        text += page.extract_text()

splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(text)
db = FAISS.from_texts(chunks, OpenAIEmbeddings())

@app.route("/ask", methods=["POST"])
def ask():
    query = request.json["query"]
    docs = db.similarity_search(query, k=2)
    context = " ".join([d.page_content for d in docs])
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You are a chatbot about KP's resume. Use this context: {context}"},
            {"role": "user", "content": query}
        ]
    )
    return jsonify({"answer": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
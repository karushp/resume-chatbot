# Resume Chatbot Backend

Flask-based backend for the resume chatbot, powered by **Groq** and **LangChain**.

---

## 🏗️ Architecture

### RAG (Retrieval-Augmented Generation) Pipeline
1. **PDF Processing**: Extract text from resume PDF using PyPDF2
2. **Text Chunking**: Split resume into manageable chunks using LangChain
3. **Embeddings**: Convert chunks to vectors using Hugging Face Sentence Transformers
4. **Vector Storage**: Store embeddings in FAISS for fast similarity search
5. **Query Processing**: Find relevant chunks and generate responses with Groq

### Tech Stack
- **Framework**: Flask with CORS support
- **AI Model**: Groq Llama 3.1 8B Instant
- **Embeddings**: Hugging Face `sentence-transformers/all-MiniLM-L6-v2`
- **Vector DB**: FAISS (Facebook AI Similarity Search)
- **PDF Processing**: PyPDF2
- **Text Processing**: LangChain CharacterTextSplitter

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Groq API key

### Installation

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Set up environment**
   ```bash
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   ```

3. **Run the server**
   ```bash
   uv run python app.py
   ```

The server will start on `http://localhost:5001`

---

## 🔧 Configuration

### Environment Variables
- `GROQ_API_KEY`: Your Groq API key (required)

### App Configuration
Edit `app.py` to customize:
```python
PERSON_NAME = "Karush Pradhan"  # Person's name
RESUME_FILE = "data/karush_resume.pdf"  # Resume PDF path
```

### Model Configuration
```python
# In groq_generate() function
"model": "llama-3.1-8b-instant",  # Groq model
"temperature": 0.7,               # Response creativity
"max_tokens": 1000                # Max response length
```

---

## 📡 API Endpoints

### POST `/ask`
Query the chatbot about the resume.

**Request:**
```json
{
  "query": "What is Karush's experience?"
}
```

**Response:**
```json
{
  "answer": "Karush has diverse experience spanning..."
}
```

---

## 🧠 How It Works

### 1. Resume Processing
```python
# Extract text from PDF
text = ""
with open(RESUME_FILE, "rb") as f:
    reader = PyPDF2.PdfReader(f)
    for page in reader.pages:
        text += page.extract_text()
```

### 2. Text Chunking
```python
# Split into manageable chunks
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(text)
```

### 3. Embeddings & Vector Storage
```python
# Create embeddings and FAISS index
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_texts(chunks, embeddings)
```

### 4. Query Processing
```python
# Find relevant chunks
docs = db.similarity_search(query, k=2)
context = " ".join([d.page_content for d in docs])

# Generate response with Groq
answer = groq_generate(query, context)
```

---

## 🔍 Dependencies

### Core Dependencies
- `flask>=3.1.2` - Web framework
- `flask-cors>=4.0.0` - CORS support
- `langchain>=0.3.27` - LLM framework
- `langchain-community>=0.3.0` - Community integrations
- `faiss-cpu>=1.12.0` - Vector similarity search
- `pypdf2>=3.0.1` - PDF processing
- `requests>=2.31.0` - HTTP requests
- `sentence-transformers>=2.2.2` - Embeddings
- `torch>=2.0.0` - PyTorch for transformers
- `dotenv>=0.9.9` - Environment variables

### Why These Choices?
- **FAISS**: Fast, efficient vector search
- **Hugging Face Embeddings**: Free, local, no API limits
- **Groq**: Fast inference, generous free tier
- **LangChain**: Robust text processing and chunking

---

## 🚀 Deployment

### Local Development
```bash
uv run python app.py
```

### Production (Render)
1. **Build Command**: `cd backend && uv sync`
2. **Start Command**: `cd backend && uv run python app.py`
3. **Environment Variables**: `GROQ_API_KEY`

### Docker (Optional)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY backend/ .
RUN pip install uv && uv sync
CMD ["uv", "run", "python", "app.py"]
```

---

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'langchain_community'"**
   ```bash
   uv sync  # Reinstall dependencies
   ```

2. **"Please set the GROQ_API_KEY environment variable"**
   ```bash
   echo "GROQ_API_KEY=your_key" > .env
   ```

3. **"Model not found" errors**
   - Check available models at [console.groq.com](https://console.groq.com/)
   - Update model name in `app.py`

4. **Port already in use**
   ```bash
   lsof -ti:5001 | xargs kill -9
   ```

### Debug Mode
Add debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 Performance

### Benchmarks
- **Startup Time**: ~5-10 seconds (model loading)
- **Query Response**: ~1-3 seconds (Groq inference)
- **Memory Usage**: ~500MB (embeddings + model)
- **Concurrent Users**: Limited by Groq API rate limits

### Optimization Tips
- Use smaller chunk sizes for faster search
- Cache embeddings (already done at startup)
- Consider model quantization for lower memory

---

## 🔒 Security

- **API Key**: Store in environment variables, never commit
- **CORS**: Configured for frontend domain
- **Input Validation**: Basic query validation
- **Rate Limiting**: Handled by Groq API

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

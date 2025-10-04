# Resume Chatbot

A chatbot that can answer questions about Karush's resume, powered by **Groq** + LangChain.  
Frontend is hosted on **GitHub Pages**, backend runs on **Render**.

---

## Demo
🔗 [Live Chatbot Demo](https://karushp.github.io/resume-chatbot)

---

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript (GitHub Pages)
- **Backend**: Python, Flask, LangChain, FAISS (Render)
- **AI Model**: Groq Llama 3.1 8B Instant
- **Embeddings**: Hugging Face Sentence Transformers (local)
- **Package Manager**: uv (for Python dependencies)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Groq API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/karushp/resume-chatbot.git
   cd resume-chatbot
   ```

2. **Set up environment variables**
   ```bash
   cd backend
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Run the backend**
   ```bash
   uv run python app.py
   ```

5. **Open the frontend**
   ```bash
   open frontend/index.html
   ```

### Getting a Groq API Key
1. Sign up at [console.groq.com](https://console.groq.com/)
2. Create an API key
3. Add it to your `.env` file

---

```
resume-chatbot/
├── backend/                 # Python Flask backend
│   ├── app.py              # Main Flask application
│   ├── data/               # Resume PDF files
│   ├── pyproject.toml      # Python dependencies
│   └── README.md           # Backend documentation
├── frontend/               # Static frontend files
│   ├── index.html          # Main HTML page
│   ├── style.css           # Styling
│   ├── script.js           # Frontend JavaScript
│   └── photo.jpeg          # Avatar image
└── README.md               # This file
```

---

## 🔧 Configuration

### Customizing for Different People
Edit `backend/app.py` to change:
- `PERSON_NAME`: The person's name
- `RESUME_FILE`: Path to the resume PDF

### Available Models
The chatbot uses Groq's `llama-3.1-8b-instant` model by default. Other available models:
- `mixtral-8x7b-32768`
- `gemma2-9b-it`
- `llama-3-8b-8192`

---

## 🚀 Deployment

### Frontend (GitHub Pages)
1. Push changes to the `frontend/` directory
2. Enable GitHub Pages in repository settings
3. Set source to `/` (root directory)

### Backend (Render)
1. Connect your GitHub repository to Render
2. Set build command: `cd backend && uv sync`
3. Set start command: `cd backend && uv run python app.py`
4. Add environment variable: `GROQ_API_KEY`

---

## 📝 Features

- **RAG Architecture**: Uses FAISS vector search with resume embeddings
- **Natural Responses**: Conversational AI that answers naturally
- **Modern UI**: Clean, responsive design with chat bubbles
- **Fast Performance**: Groq's lightning-fast inference
- **Local Embeddings**: Free Hugging Face embeddings (no API limits)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
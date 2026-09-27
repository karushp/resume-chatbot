# Backend

Flask RAG API for the resume chatbot.

## Setup

```bash
cp .env.example .env   # fill in API keys
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
KMP_DUPLICATE_LIB_OK=TRUE python app.py
```

Runs on `http://127.0.0.1:5001` (`PORT` env overrides).

## Configure

Edit [`config.py`](config.py) for prompt, model, chunking, history, and rate limits.  
Resume content: [`data/karush_resume.md`](data/karush_resume.md).

The FAISS index is built automatically on startup (and rebuilt when the resume file is newer).

## API

`POST /ask`

```json
{
  "query": "What projects has Karush worked on?",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

Success: `{ "answer": "..." }`  
Errors: `{ "error": "..." }` with `400` / `429` / `502`

## Notes

- On macOS, set `KMP_DUPLICATE_LIB_OK=TRUE` if FAISS hits an OpenMP conflict.
- Secrets stay in `.env` (never commit). Use `.env.example` as a template.

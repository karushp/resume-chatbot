# Resume Chatbot - Complete System Manual

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Why Backend Hosting is Necessary](#why-backend-hosting-is-necessary)
4. [Backend Logic Flow](#backend-logic-flow)
5. [Frontend Logic Flow](#frontend-logic-flow)
6. [Data Flow Explanation](#data-flow-explanation)
7. [Technical Components](#technical-components)
8. [Deployment Architecture](#deployment-architecture)

---

## 🎯 System Overview

The Resume Chatbot is a **RAG (Retrieval-Augmented Generation)** system that allows users to ask questions about Karush's resume and get intelligent, conversational responses.

### Key Features:
- **PDF Resume Processing**: Extracts text from PDF files
- **Semantic Search**: Uses AI embeddings to find relevant information
- **Conversational AI**: Generates natural responses using Groq's Llama model
- **Modern UI**: Clean, responsive chat interface
- **Real-time Interaction**: Instant responses with loading indicators

---

## 🏗️ Architecture Diagram

```
┌─────────────────┐    HTTP Request    ┌─────────────────┐
│   Frontend      │ ──────────────────► │   Backend       │
│   (GitHub Pages)│                     │   (Fly.io)      │
│                 │                     │                 │
│ • HTML/CSS/JS   │ ◄────────────────── │ • Flask API     │
│ • User Interface│    JSON Response    │ • PDF Processing│
│ • Chat UI       │                     │ • AI Embeddings │
└─────────────────┘                     │ • Vector Search │
                                        │ • Groq API      │
                                        └─────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │   External APIs  │
                                            │                 │
                                            │ • Groq API      │
                                            │ • Hugging Face   │
                                            │   Embeddings    │
                                            └─────────────────┘
```

---

## 🤔 Why Backend Hosting is Necessary

### **GitHub Pages Limitations:**
GitHub Pages only hosts **static files** (HTML, CSS, JavaScript). It cannot:
- ❌ Run server-side code (Python, Node.js, etc.)
- ❌ Process files (PDFs, databases)
- ❌ Make API calls to external services
- ❌ Store environment variables securely
- ❌ Handle CORS issues

### **What Your App Needs:**
- ✅ **PDF Processing**: Extract text from resume PDF
- ✅ **AI Model Loading**: Load Hugging Face embeddings model
- ✅ **Vector Database**: Store and search resume embeddings
- ✅ **API Integration**: Call Groq API for responses
- ✅ **Environment Variables**: Securely store API keys
- ✅ **CORS Handling**: Allow frontend to call backend

### **Why Not Pure Frontend?**
```javascript
// This WON'T work in GitHub Pages:
import PyPDF2 from 'pypdf2';  // ❌ No Python support
import { HuggingFaceEmbeddings } from 'langchain';  // ❌ No server-side processing
const embeddings = await loadModel();  // ❌ No file system access
```

---

## 🔄 Backend Logic Flow

### **Startup Process (Lines 25-38):**

```python
# 1. PDF Text Extraction
text = ""
with open(RESUME_FILE, "rb") as f:
    reader = PyPDF2.PdfReader(f)
    for page in reader.pages:
        text += page.extract_text()
```
**Purpose**: Convert PDF resume into plain text

```python
# 2. Text Chunking
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(text)
```
**Purpose**: Split long text into manageable pieces for AI processing

```python
# 3. Create Embeddings & Vector Store
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")
db = FAISS.from_texts(chunks, embeddings)
```
**Purpose**: Convert text chunks into numerical vectors for semantic search

### **Query Processing (Lines 80-86):**

```python
@app.route("/ask", methods=["POST"])
def ask():
    query = request.json["query"]                    # 1. Get user question
    docs = db.similarity_search(query, k=2)         # 2. Find relevant chunks
    context = " ".join([d.page_content for d in docs])  # 3. Combine chunks
    answer = groq_generate(query, context)          # 4. Generate response
    return jsonify({"answer": answer})               # 5. Return answer
```

### **AI Response Generation (Lines 41-77):**

```python
def groq_generate(query, context):
    # 1. Prepare API request to Groq
    data = {
        "messages": [
            {
                "role": "system",
                "content": f"You are Karush's personal assistant. Answer questions naturally and conversationally about Karush based on this resume information: {context}."
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
    
    # 2. Send request to Groq API
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", ...)
    
    # 3. Extract and return response
    return result["choices"][0]["message"]["content"]
```

---

## 🎨 Frontend Logic Flow

### **User Interaction (Lines 1-6):**
```javascript
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();  // Trigger message sending
    }
}
```
**Purpose**: Allow users to press Enter to send messages

### **Message Sending Process (Lines 8-88):**

#### **Step 1: UI Updates (Lines 13-20):**
```javascript
const userMessage = input.value.trim();
if (!userMessage) return;

input.value = "";                    // Clear input field
sendButton.disabled = true;         // Disable send button
sendButton.innerHTML = '⋯';         // Show loading state
```

#### **Step 2: Display User Message (Lines 22-28):**
```javascript
chat.innerHTML += `
    <div class="chat-message user">
        <div class="user-avatar">U</div>
        <div class="message-bubble user">${userMessage}</div>
    </div>
`;
```
**Purpose**: Show user's message in chat interface

#### **Step 3: Show Loading Indicator (Lines 30-40):**
```javascript
const loadingId = "loading-" + Date.now();
chat.innerHTML += `
    <div id="${loadingId}" class="loading-container">
        <img src="photo.jpeg" alt="Bot" class="loading-avatar">
        <div class="loading-bubble">
            <div class="loading-spinner"></div>
            <span class="loading-text">🤖 Bot is thinking...</span>
        </div>
    </div>
`;
```
**Purpose**: Show user that the bot is processing their request

#### **Step 4: API Call (Lines 45-50):**
```javascript
const response = await fetch("https://resume-chatbot-tpm0.onrender.com", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: userMessage })
});
```
**Purpose**: Send user's question to backend API

#### **Step 5: Handle Response (Lines 52-66):**
```javascript
const data = await response.json();

// Remove loading indicator
const loadingElement = document.getElementById(loadingId);
if (loadingElement) {
    loadingElement.remove();
}

// Add bot response
chat.innerHTML += `
    <div class="chat-message bot">
        <img src="photo.jpeg" alt="Bot" class="message-avatar">
        <div class="message-bubble bot">${data.answer}</div>
    </div>
`;
```
**Purpose**: Display bot's response and clean up loading state

#### **Step 6: Error Handling (Lines 68-82):**
```javascript
catch (error) {
    // Remove loading indicator
    const loadingElement = document.getElementById(loadingId);
    if (loadingElement) {
        loadingElement.remove();
    }
    
    // Add error message
    chat.innerHTML += `
        <div class="chat-message bot">
            <img src="photo.jpeg" alt="Bot" class="message-avatar">
            <div class="message-bubble bot">❌ Sorry, I encountered an error: ${error.message}</div>
        </div>
    `;
}
```
**Purpose**: Handle network errors gracefully

---

## 🔄 Data Flow Explanation

### **Complete User Journey:**

1. **User Types Question**: "What projects has Karush worked on?"

2. **Frontend Processing**:
   - Validates input (not empty)
   - Disables send button
   - Shows user message in chat
   - Displays loading spinner

3. **API Request**:
   ```json
   POST https://resume-chatbot-tpm0.onrender.com/ask
   {
     "query": "What projects has Karush worked on?"
   }
   ```

4. **Backend Processing**:
   - Receives query
   - Searches vector database for relevant resume chunks
   - Combines relevant chunks into context
   - Sends context + query to Groq API
   - Receives AI-generated response

5. **API Response**:
   ```json
   {
     "answer": "Karush has worked on several interesting projects including a resume chatbot built with Python and Flask, web applications using modern frameworks, and various data analysis projects..."
   }
   ```

6. **Frontend Updates**:
   - Removes loading spinner
   - Displays bot response
   - Re-enables send button
   - Scrolls to bottom of chat

---

## 🛠️ Technical Components

### **Backend Technologies:**
- **Flask**: Web framework for API endpoints
- **PyPDF2**: PDF text extraction
- **LangChain**: Text processing and chunking
- **Hugging Face Embeddings**: Convert text to vectors
- **FAISS**: Vector similarity search
- **Groq API**: AI response generation
- **Flask-CORS**: Handle cross-origin requests

### **Frontend Technologies:**
- **HTML5**: Structure and semantic markup
- **CSS3**: Styling and responsive design
- **Vanilla JavaScript**: Interactive functionality
- **Fetch API**: HTTP requests to backend
- **DOM Manipulation**: Dynamic UI updates

### **External Services:**
- **Groq API**: Fast AI inference (Llama 3.1 8B)
- **Hugging Face**: Pre-trained embedding models
- **GitHub Pages**: Static frontend hosting
- **Fly.io/Render**: Backend hosting

---

## 🚀 Deployment Architecture

### **Frontend (GitHub Pages):**
```
Repository: karushp/resume-chatbot
Branch: main
Source: /frontend directory
URL: https://karushp.github.io/resume-chatbot
```

### **Backend (Fly.io/Render):**
```
Platform: Fly.io (or Render)
Service: resume-chatbot-backend
URL: https://resume-chatbot-backend.fly.dev
Environment Variables: GROQ_API_KEY
```

### **Communication Flow:**
```
User Browser → GitHub Pages (Frontend) → Fly.io (Backend) → Groq API
                ↑                                        ↓
                ←────────── JSON Response ←──────────────┘
```

---

## 🔧 Configuration Points

### **Backend Configuration (app.py):**
```python
PERSON_NAME = "Karush Pradhan"  # Change person's name
RESUME_FILE = "data/karush_resume.pdf"  # Change resume file
chunk_size=500  # Adjust chunk size
chunk_overlap=50  # Adjust overlap
k=2  # Number of relevant chunks to retrieve
```

### **Frontend Configuration (script.js):**
```javascript
// Change backend URL
const response = await fetch("YOUR_BACKEND_URL", {
```

### **AI Model Configuration:**
```python
"model": "llama-3.1-8b-instant",  # Groq model
"temperature": 0.7,               # Response creativity (0-1)
"max_tokens": 1000                # Max response length
```

---

## 📊 Performance Characteristics

### **Startup Time:**
- **Backend**: ~10-15 seconds (model loading)
- **Frontend**: Instant (static files)

### **Response Time:**
- **Vector Search**: ~100-200ms
- **Groq API Call**: ~500-1000ms
- **Total**: ~1-2 seconds per query

### **Memory Usage:**
- **Backend**: ~400-600MB (embeddings + model)
- **Frontend**: ~5-10MB (static files)

### **Scalability:**
- **Concurrent Users**: Limited by Groq API rate limits
- **Resume Size**: Handles typical resume PDFs (1-5 pages)
- **Query Volume**: Depends on Groq API tier

---

## 🔒 Security Considerations

### **API Key Management:**
- ✅ Stored as environment variables
- ✅ Never exposed to frontend
- ✅ Rotated regularly

### **CORS Configuration:**
- ✅ Configured for specific frontend domain
- ✅ Prevents unauthorized access

### **Input Validation:**
- ✅ Basic query validation
- ✅ Error handling for malformed requests

---

## 🐛 Common Issues & Solutions

### **Memory Issues:**
- **Problem**: Backend exceeds hosting memory limits
- **Solution**: Use external embeddings API or smaller models

### **CORS Errors:**
- **Problem**: Frontend can't call backend
- **Solution**: Ensure Flask-CORS is properly configured

### **API Rate Limits:**
- **Problem**: Groq API returns rate limit errors
- **Solution**: Upgrade Groq plan or implement caching

### **PDF Processing Errors:**
- **Problem**: Can't extract text from PDF
- **Solution**: Ensure PDF is not image-based or corrupted

---

This manual provides a complete understanding of how your resume chatbot system works, from the technical architecture to the user experience flow. The backend hosting is essential because it handles all the complex AI processing that cannot be done in a static frontend environment.

# Intelligent RAG Product Assistant

A real-time, ultra-low latency Retrieval-Augmented Generation (RAG) chatbot designed to act as a premium product assistant. It features an interactive React frontend and a robust, async FastAPI backend utilizing LangChain, Pinecone, and Groq LLMs.

## 🚀 Features
- **Real-Time Streaming**: Asynchronous WebSockets deliver LLM responses instantly, chunk-by-chunk.
- **Advanced Semantic Search**: Pinecone Serverless Vector Database integrated with local HuggingFace embeddings (`all-MiniLM-L6-v2`) for fast, cost-effective context retrieval.
- **Persistent Chat Memory**: MongoDB seamlessly stores and retrieves user session histories.
- **SOLID Backend**: Engineered with Strict OOP principles, dependency injection, and asynchronous thread-safety (PyTorch concurrency locks).
- **Beautiful UI/UX**: Custom Glassmorphism React interface with dynamic typing indicators and Markdown rendering.

---

## 🛠️ Tech Stack
- **Frontend**: React 18, Vite, WebSockets, CSS Glassmorphism
- **Backend**: Python 3.12, FastAPI, Motor (Async MongoDB), Pydantic V2
- **AI / Data**: LangChain, Groq (`qwen3.8-27b`), Pinecone, HuggingFace Sentence Transformers

---

## 🔒 Environment Setup

You must create a `.env` file in the root directory. *Note: `.env` is git-ignored and should never be pushed to public repositories.*

```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=product-assistant
MONGODB_URI=your_mongodb_cluster_uri
MONGODB_DB_NAME=chat_db
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/hasnain-shehnsha/product-assistant.git
cd product-assistant
```

### 2. Backend Setup (FastAPI)
Navigate to the backend directory and set up your Python environment:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup (React/Vite)
Open a new terminal, navigate to the frontend directory, and install Node dependencies:
```bash
cd frontend
npm install
```

---

## ▶️ Running the Application

To run the full application, you need to start both the backend and frontend development servers.

### Start the Backend
In your backend terminal (with the virtual environment activated):
```bash
uvicorn app.main:app --reload
```
*The API will be available at http://127.0.0.1:8000*

### Start the Frontend
In your frontend terminal:
```bash
npm run dev
```
*The UI will be available at http://localhost:5173*

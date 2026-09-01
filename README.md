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

## 🚀 GitHub Push Instructions

Follow these exact terminal commands to push this project to a new GitHub repository:

### 1. Initialize Git and add files
```bash
# Initialize a fresh git repository
git init

# Add all files (the .gitignore will automatically prevent .env and venv from being added)
git add .

# Commit the files
git commit -m "Initial commit: Production-ready RAG chatbot"
```

### 2. Connect to GitHub and Push
*Before running this, go to GitHub.com, click "New Repository", give it a name (e.g., `rag-product-assistant`), and DO NOT initialize it with a README or gitignore.*

```bash
# Link your local code to your new GitHub repository (replace URL with your actual repo URL)
git remote add origin https://github.com/your-username/your-repo-name.git

# Set the main branch
git branch -M main

# Push the code to GitHub
git push -u origin main
```

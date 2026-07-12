# RAG Assistant

A full-stack Retrieval-Augmented Generation (RAG) web application that lets users upload documents and ask questions answered directly from that content, with source citations.

## Features

- Document upload (PDF, DOCX, TXT) with automatic text extraction and chunking
- Vector embeddings via `sentence-transformers`, stored and searched using ChromaDB
- Chat interface with retrieval-augmented answers generated via OpenRouter (Claude models)
- Source citations shown under each answer
- Persistent chat history (MySQL), grouped and browsable in the sidebar
- Rename/delete past conversations
- Admin dashboard with usage stats (documents, sessions, questions, recent activity)
- Document management (upload, view status, delete)
- Modern dark-themed, responsive UI with markdown-rendered responses

## Tech Stack

- **Backend:** Python, Flask
- **Database:** MySQL (via SQLAlchemy + PyMySQL)
- **Vector Store:** ChromaDB
- **Embeddings:** sentence-transformers (`all-MiniLM-L6-v2`, local, free)
- **LLM:** OpenRouter API (Claude models)
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5

## Project Structure
rag_project/
├── app.py                  # Flask app factory, DB init, blueprint registration
├── config.py                # Loads .env, sets up SQLAlchemy URI
├── .env                     # Secrets (DB credentials, API key) - not committed
├── requirements.txt
│
├── models/
│   └── db_models.py         # Document, ChatSession, Message tables
│
├── services/
│   ├── document_service.py  # Text extraction + chunking
│   ├── vector_store.py      # ChromaDB embedding storage/search
│   └── llm_service.py       # OpenRouter API calls
│
├── routes/
│   ├── document_routes.py   # /upload, /documents, /documents/<id>/delete
│   ├── chat_routes.py       # /chat, /chat/history, /chat/sessions
│   └── admin_routes.py      # /admin
│
├── static/
│   ├── css/style.css
│   ├── js/chat.js
│   ├── js/upload.js
│   └── uploads/             # Uploaded files stored here
│
├── templates/
│   ├── base.html
│   ├── index.html           # Chat interface
│   ├── documents.html       # Document management
│   └── admin_dashboard.html
│
└── chroma_db/                # ChromaDB local vector storage (auto-created)

## How It Works (RAG Pipeline)

1. User uploads a document → text is extracted and split into overlapping chunks.
2. Each chunk is converted into a vector embedding and stored in ChromaDB.
3. When a user asks a question, the question is embedded the same way.
4. ChromaDB retrieves the most semantically similar chunks.
5. Those chunks are passed as context to the LLM (via OpenRouter).
6. The LLM generates an answer grounded in the retrieved content, and the source chunks are shown as citations.

## Setup Instructions

### Prerequisites
- Python 3.10+
- MySQL Server (running, with a database created)

### 1. Clone/download the project and install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment variables
Create a `.env` file in the project root:
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
DB_NAME=rag_db
OPENROUTER_API_KEY=your-openrouter-key-here
SECRET_KEY=any-random-string

### 3. Create the database
In MySQL, create an empty database matching `DB_NAME`:
```sql
CREATE DATABASE rag_db;
```
Tables are created automatically on first run.

### 4. Run the app
```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

## Usage

1. Go to **Knowledge Base** and upload one or more documents.
2. Go to **Chat** and ask questions about the uploaded content.
3. View source citations under each answer.
4. Browse, rename, or delete past conversations from the sidebar.
5. Check **Admin Panel** for usage statistics.

## Notes

- Embeddings run locally and are free (no API cost).
- LLM generation uses OpenRouter, which requires API credits.
- This project does not include authentication/login by design (single-user/demo setup).

## Author

Built as part of an internship project to demonstrate a full-stack RAG implementation using Flask, MySQL, and vector search.
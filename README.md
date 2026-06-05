# AI Chatbot Application

A full-stack AI chatbot application similar to ChatGPT with RAG (Retrieval-Augmented Generation) support.

## Features

- 🤖 AI conversations with OpenAI GPT models
- 💾 Conversation history with MongoDB
- 📄 PDF document upload and RAG support
- 🎨 Modern React frontend with Tailwind CSS
- 🔐 Secure backend with FastAPI
- 🐳 Docker containerization
- 📱 Responsive design
- ⚡ Real-time chat interface

## Tech Stack

### Backend
- Python with FastAPI
- LangChain for LLM orchestration
- OpenAI API integration
- MongoDB for data persistence
- ChromaDB for vector embeddings
- PyPDF for document processing

### Frontend
- React 18 with Vite
- Tailwind CSS for styling
- Axios for API calls
- Zustand for state management

### DevOps
- Docker & Docker Compose
- MongoDB containerization

## Project Structure

```
AI-Chat-Bot/
│
├── 📁 backend/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application entry point
│   ├── requirements.txt                 # Python dependencies
│   │
│   ├── 📁 config/
│   │   ├── __init__.py
│   │   └── settings.py                  # Environment variables & configuration
│   │
│   ├── 📁 core/
│   │   ├── __init__.py
│   │   └── exceptions.py                # Custom exceptions
│   │
│   ├── 📁 models/
│   │   ├── __init__.py
│   │   ├── database_models.py           # MongoDB document models
│   │   └── schemas.py                   # Pydantic request/response schemas
│   │
│   ├── 📁 database/
│   │   ├── __init__.py
│   │   ├── mongodb.py                   # MongoDB connection & CRUD operations
│   │   └── queries.py                   # Database query helpers
│   │
│   ├── 📁 services/
│   │   ├── __init__.py
│   │   ├── chat_service.py              # Chat logic & conversation management
│   │   ├── llm_service.py               # OpenAI API integration & LLM calls
│   │   └── rag_service.py               # RAG document retrieval & augmentation
│   │
│   ├── 📁 routes/
│   │   ├── __init__.py
│   │   ├── health.py                    # Health check endpoints
│   │   ├── chat.py                      # Conversation endpoints
│   │   ├── messages.py                  # Message send/history endpoints
│   │   └── documents.py                 # Document upload/retrieval endpoints
│   │
│   ├── 📁 rag/
│   │   ├── __init__.py
│   │   ├── document_processor.py         # PDF chunking & processing
│   │   └── vector_store.py              # ChromaDB vector store management
│   │
│   └── 📁 utils/
│       ├── __init__.py
│       ├── helpers.py                   # Utility functions (ID generation, timestamps)
│       └── logging_config.py            # Logging configuration
│
├── 📁 frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.cjs
│   ├── index.html
│   │
│   └── 📁 src/
│       ├── main.jsx                     # React entry point
│       ├── App.jsx                      # Root component
│       ├── index.css
│       ├── App.css
│       │
│       ├── 📁 components/
│       │   ├── ChatMessage.jsx          # Individual message display
│       │   ├── ChatWindow.jsx           # Main chat interface
│       │   ├── MessageInput.jsx         # Message input form
│       │   ├── ConversationList.jsx     # Conversation sidebar
│       │   ├── ChatPage.jsx             # Chat page layout
│       │   ├── FileUpload.jsx           # Document upload component
│       │   └── Sidebar.jsx              # App sidebar
│       │
│       ├── 📁 services/
│       │   └── api.js                   # API client & HTTP requests
│       │
│       ├── 📁 store/
│       │   └── chatStore.js             # Zustand global state management
│       │
│       ├── 📁 context/
│       │   └── (placeholder for context API)
│       │
│       ├── 📁 pages/
│       │   └── (placeholder for additional pages)
│       │
│       └── 📁 styles/
│           └── (CSS modules & utilities)
│
├── 📁 docker/
│   ├── Dockerfile.backend               # Backend container image
│   └── Dockerfile.frontend              # Frontend container image
│
├── 📁 docs/
│   ├── API_DOCUMENTATION.md             # API endpoint reference
│   └── DATABASE_SETUP.md                # Database setup guide
│
├── 📁 scripts/
│   ├── init_db.py                       # Database initialization script
│   ├── test_api.py                      # API testing script
│   └── check_db_status.py               # Database health check
│
├── 📁 logs/
│   └── (application logs)
│
├── 📁 data/
│   ├── 📁 chroma_db/                    # ChromaDB vector store
│   │   └── chroma.sqlite3
│   └── (data files)
│
├── 📁 uploads/
│   └── (uploaded PDF documents)
│
├── docker-compose.yml                  # Docker Compose orchestration
├── .env                                 # Environment variables (local)
├── .env.example                         # Environment variables template
├── .gitignore
├── .git/
└── README.md                            # This file
```

### Directory Description

| Directory | Purpose |
|-----------|---------|
| `backend/` | FastAPI backend server with LLM integration |
| `frontend/` | React + Vite frontend application |
| `docker/` | Docker containerization configs |
| `docs/` | Documentation and setup guides |
| `scripts/` | Utility scripts for testing and initialization |
| `logs/` | Application runtime logs |
| `data/` | Vector database and cached data |
| `uploads/` | User-uploaded PDF files for RAG |

## Quick Start (Local Development)

This project is now ready for local development with a single setup path.

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB (local or Docker)
- OpenAI API Key (for AI responses)

### 2. Clone and set env
```bash
git clone <repo-url>
cd AI-Chat-Bot
cp .env.example .env
# On Windows use: copy .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY`.

### 3. Backend setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Frontend setup
```bash
cd ../frontend
npm install
```

### 5. Start MongoDB
Option A (Docker):
```bash
docker run -d --name ai_chatbot_mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=password -e MONGO_INITDB_DATABASE=ai_chatbot mongo:7.0
```
Option B (local): ensure MongoDB is running and listens on `mongodb://localhost:27017`

### 6. Launch backend + frontend
```bash
# terminal 1
cd backend
venv\Scripts\activate    # windows
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# terminal 2
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

### 7. Verify health
- Visit `http://localhost:8000/api/health`
- Visit `http://localhost:5173`

---

## ✅ Recent Updates & Fixes

### Checkpoint 3 Completion (Latest)
- **Backend Message Endpoint Fixed**: `/api/message/send` now returns 200 with proper `ChatResponse` schema
- **Schema Alignment**: All response fields properly validated (conversation_id, message, response, model, input_tokens, output_tokens, timestamp, rag_used)
- **Mock OpenAI Fallback**: Local development now works without valid OpenAI key - uses mock responses for testing
- **Database Integration**: Conversation creation and message storage working correctly
- **Frontend-Backend Communication**: No more crashes on message send
- **Memory Management**: Fixed duplicate message insertion in conversation memory
- **Configuration**: OpenAI API key is now optional with smart detection of placeholder values

### What works now:
✅ Backend startup without errors  
✅ Database connection and schema creation  
✅ Chat message sending and response generation (mock or real)  
✅ Conversation history storage  
✅ Frontend API communication  
✅ Local development without OpenAI key  

### To enable real AI responses:
Set a valid `OPENAI_API_KEY` in your `.env` file:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

---

## Optional: Docker Compose
```bash
docker-compose up -d
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Important fixes implemented

### Latest (Checkpoint 3)
- ✅ `backend/services/llm_service.py`: Added mock response fallback for local development
- ✅ `backend/config/settings.py`: Made OpenAI key optional with validation
- ✅ `backend/models/schemas.py`: Added use_rag field to ChatRequest
- ✅ `backend/routes/messages.py`: Fixed parameter passing to chat service
- ✅ `backend/services/chat_service.py`: Fixed conversation ID storage and memory handling
- ✅ `backend/database/mongodb.py`: Conversation creation using _id field correctly

### Previous checkpoints
- `backend/services/rag_service.py`: Fixed document processing to unpack `full_text, chunks` and to call `get_statistics(full_text, chunks)`
- `backend/config/settings.py`: `.env` loading is now robust from repo root to avoid path issues

---

## API Endpoints

### Health Check
- `GET /api/health` - Check API status
- `GET /api/health/db` - Check database connection

### Chat & Conversations
- `POST /api/message/send` - Send message and get AI response
  - Request: `{ message, conversation_id?, use_rag?, system_prompt?, model? }`
  - Response: `{ conversation_id, message, response, model, input_tokens, output_tokens, timestamp, rag_used }`
- `GET /api/message/history` - Get conversation message history
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations` - List all conversations
- `GET /api/conversations/{id}` - Get conversation details

### Documents (RAG)
- `POST /api/documents/upload` - Upload PDF file for RAG
- `GET /api/documents` - List uploaded documents

### Interactive API Docs
- `GET /docs` - Swagger UI (interactive API explorer)
- `GET /redoc` - ReDoc (alternative API documentation)

## Configuration

All configuration is managed through environment variables in `.env`:

### OpenAI Configuration
- `OPENAI_API_KEY` - Your OpenAI API key (optional - uses mock for local dev)
- `MODEL_NAME` - LLM model (default: `gpt-3.5-turbo`)
- `TEMPERATURE` - Model temperature (0.0-2.0, default: 0.7)
- `MAX_TOKENS` - Max response tokens (default: 2048)
- `TOP_P` - Top-p sampling (default: 0.9)
- `EMBEDDING_MODEL` - Embedding model for RAG (default: `text-embedding-3-small`)

### MongoDB Configuration
- `MONGO_URI` - MongoDB connection string (default: `mongodb://localhost:27017/ai_chatbot`)
- `MONGO_DB_NAME` - Database name (default: `ai_chatbot`)

### API Configuration
- `API_HOST` - Server host (default: `0.0.0.0`)
- `API_PORT` - Server port (default: `8000`)
- `API_DEBUG` - Debug mode (default: `False`)

### CORS Configuration
- `CORS_ORIGINS` - Comma-separated allowed origins (default: `http://localhost:5173,http://localhost:3000`)

### Vector Database Configuration
- `VECTOR_DB_TYPE` - Vector store type (default: `chroma`)
- `EMBED_DIM` - Embedding dimension (default: `1536`)
- `CHROMA_DB_PATH` - ChromaDB path (default: `./data/chroma_db`)

### RAG Configuration
- `RAG_CHUNK_SIZE` - PDF chunk size (default: `1024`)
- `RAG_CHUNK_OVERLAP` - Chunk overlap (default: `128`)
- `PDF_UPLOAD_DIR` - Upload directory (default: `./uploads`)

See `.env.example` for all available options.

## Testing

### Test Backend Endpoint
```bash
curl -X POST http://localhost:8000/api/message/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "conversation_id": null, "use_rag": false}'
```

### Expected Response
```json
{
  "conversation_id": "uuid-here",
  "message": "Hello, how are you?",
  "response": "(mock) Your response here or actual AI response",
  "model": "gpt-3.5-turbo",
  "input_tokens": 5,
  "output_tokens": 15,
  "timestamp": "2024-01-01T12:00:00",
  "rag_used": false
}
```

### API Test Script
```bash
cd scripts
python test_api.py
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "OpenAI API error: 401" | Set valid `OPENAI_API_KEY` in `.env` or use mock responses (default) |
| MongoDB connection refused | Start MongoDB: `docker run -d --name mongodb -p 27017:27017 mongo:7.0` |
| Frontend shows empty screen | Check browser console for API errors; ensure backend is running on port 8000 |
| CORS errors | Update `CORS_ORIGINS` in `.env` to include frontend URL |
| Port already in use | Change `API_PORT` or `npm run dev -- --port <new-port>` |

---

## Project Roadmap

| Checkpoint | Status | Description |
|-----------|--------|-------------|
| 1 | ✅ Done | Project setup & FastAPI scaffolding |
| 2 | ✅ Done | MongoDB integration |
| 3 | ✅ Done | Chat endpoint & mock responses (CURRENT) |
| 4-10 | 📋 Planned | Frontend UI, RAG pipeline, streaming, deployment |

---

**Project Status**: Checkpoint 3 of 10 completed ✅  
**Last Update**: June 2024  
**Maintainer**: AI Chatbot Team

# AI Chatbot Application

A full-stack AI chatbot application similar to ChatGPT with RAG (Retrieval-Augmented Generation) support.

## Features

- ≡ƒñû AI conversations with OpenAI GPT models
- ≡ƒÆ╛ Conversation history with MongoDB
- ≡ƒôä PDF document upload and RAG support
- ≡ƒÄ¿ Modern React frontend with Tailwind CSS
- ≡ƒöÉ Secure backend with FastAPI
- ≡ƒÉ│ Docker containerization
- ≡ƒô▒ Responsive design
- ΓÜí Real-time chat interface

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
ai-chatbot/
Γö£ΓöÇΓöÇ backend/
Γöé   Γö£ΓöÇΓöÇ config/          # Configuration management
Γöé   Γö£ΓöÇΓöÇ models/          # Pydantic schemas
Γöé   Γö£ΓöÇΓöÇ routes/          # API endpoints
Γöé   Γö£ΓöÇΓöÇ services/        # Business logic
Γöé   Γö£ΓöÇΓöÇ database/        # Database operations
Γöé   Γö£ΓöÇΓöÇ rag/             # RAG pipeline
Γöé   Γö£ΓöÇΓöÇ main.py          # FastAPI app
Γöé   ΓööΓöÇΓöÇ requirements.txt  # Python dependencies
Γö£ΓöÇΓöÇ frontend/
Γöé   Γö£ΓöÇΓöÇ src/
Γöé   Γöé   Γö£ΓöÇΓöÇ components/  # React components
Γöé   Γöé   Γö£ΓöÇΓöÇ pages/       # Page components
Γöé   Γöé   Γö£ΓöÇΓöÇ services/    # API services
Γöé   Γöé   Γö£ΓöÇΓöÇ context/     # React context
Γöé   Γöé   ΓööΓöÇΓöÇ styles/      # CSS files
Γöé   Γö£ΓöÇΓöÇ package.json
Γöé   ΓööΓöÇΓöÇ vite.config.js
Γö£ΓöÇΓöÇ docker/
Γöé   Γö£ΓöÇΓöÇ Dockerfile.backend
Γöé   ΓööΓöÇΓöÇ Dockerfile.frontend
Γö£ΓöÇΓöÇ docker-compose.yml
Γö£ΓöÇΓöÇ .env.example
ΓööΓöÇΓöÇ README.md
```

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

## Optional: Docker Compose
```bash
docker-compose up -d
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Important fixes implemented
- `backend/services/rag_service.py`: fixed document processing to unpack `full_text, chunks` and to call `get_statistics(full_text, chunks)`
- `backend/config/settings.py`: `.env` loading is now robust from repo root to avoid path issues

---

## API Endpoints

### Health Check
- `GET /api/health` - Check API status

### Chat
- `POST /api/chat` - Send message and get response
- `GET /api/history/:conversation_id` - Get conversation history

### Documents
- `POST /api/upload-document` - Upload PDF for RAG
- `GET /api/documents` - List uploaded documents

## Configuration

All configuration is managed through environment variables in `.env`:

- `OPENAI_API_KEY` - OpenAI API key
- `MONGO_URI` - MongoDB connection string
- `MODEL_NAME` - LLM model name (default: gpt-3.5-turbo)
- `TEMPERATURE` - LLM temperature parameter
- `CORS_ORIGINS` - Allowed CORS origins

See `.env.example` for all available options.

## Testing

Instructions for testing API endpoints will be provided in Checkpoint 10.

---

**Project Status**: Under development (Checkpoint 1 of 10 completed)

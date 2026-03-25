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
ai-chatbot/
├── backend/
│   ├── config/          # Configuration management
│   ├── models/          # Pydantic schemas
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── database/        # Database operations
│   ├── rag/             # RAG pipeline
│   ├── main.py          # FastAPI app
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── context/     # React context
│   │   └── styles/      # CSS files
│   ├── package.json
│   └── vite.config.js
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

See detailed instructions below. This README will be completed in Checkpoint 10.

## Setup Instructions

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB
- OpenAI API Key

### 2. Environment Setup
- Copy `.env.example` to `.env`
- Fill in required API keys and configuration

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Frontend Setup
```bash
cd frontend
npm install
```

### 5. Run Locally
- Backend: `uvicorn backend.main:app --reload`
- Frontend: `npm run dev`
- MongoDB: Use Docker or local installation

### 6. Docker Setup
```bash
docker-compose up -d
```

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

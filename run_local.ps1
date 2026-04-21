# Local run helper for AI-Chat-Bot (Windows PowerShell)
# Usage: .\run_local.ps1

# 1) Ensure .env exists
if (-not (Test-Path .env)) {
  Copy-Item .env.example .env
  Write-Host "Created .env from .env.example. Edit .env with your OPENAI_API_KEY and settings."
} else {
  Write-Host ".env already exists."
}

# 2) Start MongoDB via Docker if not running
if (-not (docker ps --format '{{.Names}}' | Select-String -Pattern 'ai_chatbot_mongodb')) {
  Write-Host "Starting MongoDB container..."
  docker run -d --name ai_chatbot_mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=password -e MONGO_INITDB_DATABASE=ai_chatbot mongo:7.0
} else {
  Write-Host "MongoDB container already running."
}

# 3) Start backend
Write-Host "Starting backend...";
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; if (-not (Test-Path .\\venv)) { python -m venv .\venv; }; .\\venv\\Scripts\\Activate.ps1; pip install -r requirements.txt; uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000";

# 4) Start frontend
Write-Host "Starting frontend...";
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm install; npm run dev -- --host 0.0.0.0 --port 5173";

Write-Host "Local dev setup started. Open http://localhost:5173 in browser."

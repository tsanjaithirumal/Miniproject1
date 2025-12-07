@echo off
echo Starting Medical Records RAG App...

start cmd /k "cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload"
start cmd /k "cd frontend && npm install && npm run dev"

echo Backend and Frontend are starting in separate windows.
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:5173
pause

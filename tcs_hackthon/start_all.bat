@echo off
echo Starting QuickAI Backend...
start cmd /k "cd backend && uvicorn main:app --port 8000 --reload"

echo Starting QuickAI Frontend...
start cmd /k "cd dashboard && npm run dev"

echo Both servers are starting in new windows!

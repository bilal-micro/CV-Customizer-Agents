#!/bin/bash
set -e

echo "=== ATS Agentic - Starting ==="

echo "[1/2] Starting Django backend on port 8000..."
cd backend
python3 manage.py runserver 8000 &
DJANGO_PID=$!

echo "[2/2] Starting React frontend on port 5173..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000/api/"
echo "Frontend: http://localhost:5173/"
echo ""
echo "Press Ctrl+C to stop both servers"

trap "kill $DJANGO_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait

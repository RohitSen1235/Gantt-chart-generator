#!/bin/bash

echo "Starting Gantt Chart Application servers..."

# Start backend server
echo "Starting backend server..."
cd backend
# source venv/bin/activate 2>/dev/null || {
#     echo "Creating Python virtual environment..."
#     python3 -m venv venv
#     source venv/bin/activate
#     echo "Installing backend dependencies..."
#     pip install -r requirements.txt
# }
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend server
echo "Starting frontend server..."
cd frontend
npm install 2>/dev/null
npm run dev &
FRONTEND_PID=$!

# Wait for servers to start
sleep 2

# Check if servers are running
if ps -p $BACKEND_PID > /dev/null && ps -p $FRONTEND_PID > /dev/null; then
    echo "✅ Both servers started successfully!"
    echo "Backend server running on http://localhost:8000"
    echo "Frontend server running on http://localhost:5173"
    echo ""
    echo "To stop the servers, press Ctrl+C"
    
    # Wait for Ctrl+C
    trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
    wait
else
    echo "❌ Error starting servers"
    # Cleanup any running processes
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

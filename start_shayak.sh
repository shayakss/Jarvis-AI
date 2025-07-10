#!/bin/bash

# 🚀 Shayak AI Assistant - Quick Start Script

echo "🤖 Starting Shayak AI Assistant..."
echo "======================================="

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "📦 Starting MongoDB..."
    sudo systemctl start mongodb
    sleep 2
fi

# Check if ports are available
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8001 is already in use. Stopping existing backend..."
    pkill -f "uvicorn.*server:app"
    sleep 2
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 3000 is already in use. Stopping existing frontend..."
    pkill -f "react-scripts"
    sleep 2
fi

echo "🚀 Starting Backend Server..."
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

echo "⏳ Waiting for backend to start..."
sleep 5

echo "🎨 Starting Frontend Server..."
cd ../frontend
yarn start &
FRONTEND_PID=$!

echo "⏳ Waiting for frontend to start..."
sleep 10

echo "✅ Shayak AI Assistant is now running!"
echo "======================================="
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"
echo "======================================="
echo "📝 Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped!"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Keep script running
wait
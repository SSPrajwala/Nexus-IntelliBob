#!/bin/bash

# Nexus-IntelliBob Startup Script
# This script starts both the backend and frontend services

set -e

echo "🚀 Starting Nexus-IntelliBob..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18 or higher.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Setup backend
echo -e "${YELLOW}📦 Setting up backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Initialize database
echo "Initializing database..."
python3 -c "from db import init_db; init_db()"

echo -e "${GREEN}✅ Backend setup complete${NC}"

# Start backend in background
echo -e "${YELLOW}🔧 Starting backend server on http://localhost:8000${NC}"
python3 main.py &
BACKEND_PID=$!

cd ..

# Setup frontend
echo -e "${YELLOW}📦 Setting up frontend...${NC}"
cd frontend

# Install frontend dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo -e "${GREEN}✅ Frontend setup complete${NC}"

# Start frontend
echo -e "${YELLOW}🎨 Starting frontend server on http://localhost:3000${NC}"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo -e "${GREEN}✅ Nexus-IntelliBob is running!${NC}"
echo ""
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Services stopped${NC}"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT TERM

# Wait for both processes
wait

# Made with Bob

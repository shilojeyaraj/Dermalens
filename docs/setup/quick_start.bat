@echo off
REM 🚀 Dermalens Quick Start Script for Windows
REM This script sets up the entire Dermalens application for development

setlocal enabledelayedexpansion

echo 🔬 Dermalens Quick Start
echo ========================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11+
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18+
    pause
    exit /b 1
)

echo ✅ Dependencies check completed
echo.

REM Setup backend
echo 📦 Setting up backend...
cd backend

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Set up environment
echo Setting up environment variables...
if not exist .env (
    copy .env.example .env
    echo ⚠️ Please edit backend\.env with your API keys
)

cd ..
echo ✅ Backend setup completed
echo.

REM Setup frontend
echo 🎨 Setting up frontend...
cd frontend

REM Install dependencies
echo Installing Node.js dependencies...
npm install

REM Set up environment
echo Setting up environment variables...
if not exist .env.local (
    copy .env.example .env.local
    echo ⚠️ Please edit frontend\.env.local with your API keys
)

cd ..
echo ✅ Frontend setup completed
echo.

REM Start Elasticsearch (if Docker is available)
echo 🔍 Starting Elasticsearch...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Docker not available. Please start Elasticsearch manually
) else (
    echo Starting Elasticsearch container...
    docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" elasticsearch:8.11.0
    
    echo Waiting for Elasticsearch to start...
    timeout /t 30 /nobreak >nul
    
    REM Test connection
    curl -s http://localhost:9200/ >nul 2>&1
    if errorlevel 1 (
        echo ❌ Failed to start Elasticsearch
    ) else (
        echo ✅ Elasticsearch is running
    )
)

echo.

REM Seed sample data
echo 🌱 Seeding sample data...
cd backend
call venv\Scripts\activate.bat

REM Check if Elasticsearch is running
curl -s http://localhost:9200/ >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Elasticsearch not running. Skipping data seeding.
) else (
    echo Seeding Elasticsearch with sample data...
    python seed_elasticsearch_data.py
)

cd ..
echo.

REM Test setup
echo 🧪 Testing setup...
cd backend
call venv\Scripts\activate.bat

echo Testing Gemini integration...
python test_gemini_integration.py

cd ..
echo.

REM Start services
echo 🚀 Starting services...
echo.

REM Start backend
echo Starting backend server...
cd backend
start "Dermalens Backend" cmd /k "call venv\Scripts\activate.bat && python main.py"
cd ..

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 10 /nobreak >nul

REM Start frontend
echo Starting frontend server...
cd frontend
start "Dermalens Frontend" cmd /k "npm run dev"
cd ..

REM Wait for frontend to start
echo Waiting for frontend to start...
timeout /t 10 /nobreak >nul

echo.
echo ✅ Services started successfully!
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 🔍 Elasticsearch: http://localhost:9200
echo.
echo Press any key to open the application...
pause >nul

REM Open browser
start http://localhost:3000

echo.
echo 🎉 Dermalens is now running!
echo.
echo To stop the services:
echo 1. Close the command windows
echo 2. Stop Elasticsearch: docker stop elasticsearch
echo.
pause

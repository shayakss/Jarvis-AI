@echo off
:: 🚀 Shayak AI Assistant - Windows Start Script

echo 🤖 Starting Shayak AI Assistant...
echo =======================================

:: Check if we're in the right directory
if not exist "backend\server.py" (
    echo ❌ Error: Please run this script from the project root directory
    echo    Make sure you can see the 'backend' and 'frontend' folders
    pause
    exit /b 1
)

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ first
    pause
    exit /b 1
)

:: Check if Node.js/npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js/npm not found. Please install Node.js first
    pause
    exit /b 1
)

:: Check if yarn is installed, if not install it
yarn --version >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing yarn...
    npm install -g yarn
)

echo 📦 Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)

echo 📦 Installing Frontend Dependencies...
cd ..\frontend
call yarn install
if errorlevel 1 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)

:: Create .env files if they don't exist
cd ..
if not exist "backend\.env" (
    echo 🔧 Creating backend .env file...
    echo MONGO_URL=mongodb://localhost:27017/ > backend\.env
)

if not exist "frontend\.env" (
    echo 🔧 Creating frontend .env file...
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env
)

echo 🚀 Starting Backend Server...
cd backend
start "Shayak Backend" cmd /k "python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo 🎨 Starting Frontend Server...
cd ..\frontend
start "Shayak Frontend" cmd /k "yarn start"

echo ⏳ Waiting for frontend to start...
timeout /t 10 /nobreak >nul

echo ✅ Shayak AI Assistant is starting!
echo =======================================
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8001
echo 📚 API Docs: http://localhost:8001/docs
echo =======================================
echo 📝 Two command windows will open for backend and frontend
echo 📝 Close those windows to stop the services
echo 📝 Press any key to exit this setup window

pause
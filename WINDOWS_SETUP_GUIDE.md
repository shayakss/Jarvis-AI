# 🪟 Shayak AI Assistant - Windows Setup Guide

## 🎯 Prerequisites for Windows

### 1. **Install Python 3.8+**
- Download from: https://www.python.org/downloads/
- ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
- Verify: Open Command Prompt and run `python --version`

### 2. **Install Node.js 16+**
- Download from: https://nodejs.org/
- Choose the LTS version
- Verify: Open Command Prompt and run `node --version`

### 3. **Install Git (Optional but Recommended)**
- Download from: https://git-scm.com/download/win
- Use for cloning the repository

### 4. **Install MongoDB (Optional)**
- Download MongoDB Community Server: https://www.mongodb.com/try/download/community
- Or use MongoDB Atlas (cloud): https://www.mongodb.com/atlas/database

## 🚀 Quick Start for Windows

### Method 1: Using Windows Batch Script (Recommended)

1. **Navigate to Project Directory**
   ```cmd
   cd path\to\your\shayak-ai-assistant
   ```

2. **Run the Windows Start Script**
   ```cmd
   start_shayak_windows.bat
   ```

### Method 2: Manual Setup

1. **Open Command Prompt as Administrator**
   - Press `Win + X` and select "Command Prompt (Admin)" or "PowerShell (Admin)"

2. **Navigate to Project Directory**
   ```cmd
   cd C:\path\to\your\shayak-ai-assistant
   ```

3. **Install Backend Dependencies**
   ```cmd
   cd backend
   pip install -r requirements.txt
   ```

4. **Install Frontend Dependencies**
   ```cmd
   cd ..\frontend
   npm install -g yarn
   yarn install
   ```

5. **Create Environment Files**
   
   Create `backend\.env`:
   ```
   MONGO_URL=mongodb://localhost:27017/
   ```
   
   Create `frontend\.env`:
   ```
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```

6. **Start the Application**
   
   **Terminal 1 - Backend:**
   ```cmd
   cd backend
   python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```
   
   **Terminal 2 - Frontend:**
   ```cmd
   cd frontend
   yarn start
   ```

## 🔧 MongoDB Setup for Windows

### Option 1: Local MongoDB Installation

1. **Download and Install MongoDB**
   - Go to: https://www.mongodb.com/try/download/community
   - Download the Windows MSI installer
   - Run the installer and follow the setup wizard

2. **Start MongoDB Service**
   ```cmd
   net start MongoDB
   ```

3. **Verify MongoDB is Running**
   ```cmd
   mongo --version
   ```

### Option 2: MongoDB Atlas (Cloud - Recommended)

1. **Create Free Account**
   - Go to: https://www.mongodb.com/atlas/database
   - Sign up for a free account

2. **Create a Cluster**
   - Choose the free tier
   - Select a region close to you

3. **Get Connection String**
   - Click "Connect" in your cluster
   - Choose "Connect your application"
   - Copy the connection string

4. **Update Environment File**
   ```
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/shayak_ai
   ```

## 🎯 Windows-Specific Commands

### PowerShell Commands
```powershell
# Check if Python is installed
python --version

# Check if Node.js is installed
node --version

# Install yarn globally
npm install -g yarn

# Check if ports are in use
netstat -an | findstr :3000
netstat -an | findstr :8001

# Kill processes on specific ports (if needed)
npx kill-port 3000
npx kill-port 8001
```

### Command Prompt Commands
```cmd
# Navigate to project
cd C:\path\to\shayak-ai-assistant

# Install dependencies
pip install -r backend\requirements.txt
cd frontend && yarn install

# Start services
start cmd /k "cd backend && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
start cmd /k "cd frontend && yarn start"
```

## 🚨 Common Windows Issues & Solutions

### Issue 1: "pip is not recognized"
**Solution:**
- Reinstall Python and check "Add Python to PATH"
- Or manually add Python to PATH:
  1. Search "Environment Variables" in Start Menu
  2. Add Python installation path to PATH variable

### Issue 2: "python is not recognized"
**Solution:**
- Same as Issue 1
- Alternative: Use `py` instead of `python`

### Issue 3: "Permission denied" errors
**Solution:**
- Run Command Prompt as Administrator
- Or use PowerShell with execution policy:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Issue 4: Port already in use
**Solution:**
```cmd
# Find what's using the port
netstat -ano | findstr :3000

# Kill the process (replace PID with actual process ID)
taskkill /PID 1234 /F
```

### Issue 5: MongoDB connection issues
**Solution:**
- Ensure MongoDB service is running: `net start MongoDB`
- Check Windows Firewall settings
- Use MongoDB Atlas instead of local installation

### Issue 6: Node.js/npm issues
**Solution:**
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: 
  ```cmd
  rmdir /s node_modules
  yarn install
  ```

## 🎨 Access Your Application

Once everything is running:

- **🌐 Main Interface**: http://localhost:3000
- **🔧 Backend API**: http://localhost:8001
- **📚 API Documentation**: http://localhost:8001/docs
- **🔍 API Health Check**: http://localhost:8001/api/

## 🛠️ Development Tools for Windows

### Recommended Code Editors
- **Visual Studio Code**: https://code.visualstudio.com/
- **PyCharm**: https://www.jetbrains.com/pycharm/
- **Sublime Text**: https://www.sublimetext.com/

### Useful Extensions for VS Code
- Python
- ES7+ React/Redux/React-Native snippets
- Prettier - Code formatter
- Auto Rename Tag
- MongoDB for VS Code

## 🔄 Stopping the Application

### Method 1: Close Command Windows
- Simply close the backend and frontend command windows

### Method 2: Use Ctrl+C
- In each command window, press `Ctrl + C` to stop the process

### Method 3: Kill Processes
```cmd
# Kill processes using specific ports
npx kill-port 3000 8001
```

## 📁 Windows File Structure

Your project should look like this:
```
C:\your\project\path\shayak-ai-assistant\
├── backend\
│   ├── server.py
│   ├── requirements.txt
│   └── .env
├── frontend\
│   ├── src\
│   ├── package.json
│   └── .env
├── start_shayak_windows.bat
└── README.md
```

## 🎉 You're Ready!

Your Shayak AI Assistant should now be running on Windows with the futuristic interface! 

If you encounter any issues, check the troubleshooting section above or ensure all prerequisites are properly installed.
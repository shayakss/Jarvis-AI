# 🤖 Shayak AI Assistant

> **A futuristic, AI-powered automation system with voice control and screen automation capabilities**

![Shayak AI Assistant](https://img.shields.io/badge/Shayak-AI%20Assistant-00d4ff?style=for-the-badge&logo=robot)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green?style=for-the-badge&logo=mongodb)

## ✨ Features

### 🎤 Voice & AI Control
- **Speech Recognition** - Convert speech to commands
- **Wake Word Detection** - Responds to "Shayak" 
- **Natural Language Processing** - Understands human language
- **Voice Level Monitoring** - Real-time audio feedback

### 🖥️ Screen Automation
- **Screenshot Capture** - Take screenshots programmatically
- **Mouse Control** - Automated clicking and movement
- **Keyboard Automation** - Text input and key combinations
- **OCR Text Extraction** - Read text from images
- **Window Management** - Control application windows

### ⚡ Advanced Features
- **Batch Processing** - Execute multiple commands
- **Automation Templates** - Save and reuse workflows
- **Command History** - Track all operations
- **Safe Commands** - Pre-approved command library
- **Real-time Status** - Live system monitoring

### 🎨 Futuristic UI
- **Neon Theme** - Cyan, green, purple color scheme
- **Glass Morphism** - Translucent interface elements
- **Smooth Animations** - 60fps transitions and effects
- **Responsive Design** - Works on all screen sizes

## 🚀 Quick Start

### Option 1: Using the Start Script
```bash
./start_shayak.sh
```

### Option 2: Manual Start
```bash
# Start Backend
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Start Frontend (in another terminal)
cd frontend
yarn start
```

### Option 3: Production Build
```bash
# Build Frontend
cd frontend
yarn build

# Serve with backend
cd ../backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB 4.4+
- Git

### Setup Steps
1. **Install Dependencies**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   yarn install
   ```

2. **Configure Environment**
   ```bash
   # Backend .env
   MONGO_URL=mongodb://localhost:27017/
   
   # Frontend .env
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```

3. **Start MongoDB**
   ```bash
   sudo systemctl start mongodb
   ```

4. **Run the Application**
   ```bash
   ./start_shayak.sh
   ```

## 🎯 Usage Guide

### Interface Navigation
- **VOICE & AI**: Voice control and speech commands
- **MANUAL**: Direct command line interface
- **BATCH**: Multi-command execution
- **TEMPLATES**: Automation workflows
- **SCREEN**: Screen automation tools
- **ADVANCED**: System controls and monitoring

### Voice Commands
Say "Shayak" followed by your command:
- "Shayak, take a screenshot"
- "Shayak, list files in current directory"
- "Shayak, open calculator"

### Screen Automation
1. **Take Screenshot** - Capture current screen
2. **Click Control** - Click at specific coordinates
3. **Type Text** - Automated keyboard input
4. **Extract Text** - OCR from images
5. **Window Management** - Control applications

## 🔧 API Reference

### Main Endpoints
- `GET /api/` - Health check
- `POST /api/voice/process` - Process voice commands
- `POST /api/automation/screenshot` - Take screenshot
- `POST /api/automation/click` - Mouse automation
- `POST /api/automation/type` - Keyboard automation
- `POST /api/automation/ocr` - OCR text extraction

### Documentation
Visit `http://localhost:8001/docs` for complete API documentation.

## 📁 Project Structure

```
shayak-ai-assistant/
├── backend/                 # FastAPI backend
│   ├── server.py           # Main server file
│   ├── automation.py       # Automation engine
│   ├── mock_automation.py  # Mock for testing
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Futuristic styling
│   │   └── index.js       # Entry point
│   └── package.json       # Node dependencies
├── start_shayak.sh        # Quick start script
└── SHAYAK_AI_GUIDE.md     # Complete documentation
```

## 🔐 Security

- **Safe Commands**: Pre-approved command whitelist
- **Input Validation**: All inputs are sanitized
- **Permission Control**: Limited system access
- **Error Handling**: Comprehensive error management

## 🎨 Customization

### Themes
The interface uses a futuristic neon theme with:
- Primary: Cyan (#00d4ff)
- Secondary: Green (#00ff7f)
- Accent: Purple (#8a2be2)
- Background: Dark gradients

### Fonts
- **Headers**: Orbitron (futuristic)
- **Body**: Rajdhani (modern)
- **Code**: Monospace

## 🐛 Troubleshooting

### Common Issues

1. **Voice Recognition Not Working**
   - Check microphone permissions
   - Ensure HTTPS or localhost
   - Test browser compatibility

2. **Screen Automation Fails**
   - Verify display permissions
   - Check for headless environment
   - Ensure proper resolution

3. **Database Connection Issues**
   - Verify MongoDB is running
   - Check connection string
   - Ensure proper permissions

## 📊 Performance

- **Voice Response**: < 1 second
- **Screen Automation**: < 2 seconds
- **Memory Usage**: ~200MB
- **CPU Usage**: 5-10% (idle)

## 🔄 Updates

### Version 1.0.0
- Initial release with futuristic UI
- Voice control implementation
- Screen automation features
- Batch processing capabilities

## 📞 Support

For issues or questions:
1. Check the troubleshooting guide
2. Review API documentation
3. Examine log files in `/logs/`
4. Test with safe commands first

## 🎉 Enjoy!

Your Shayak AI Assistant is ready to transform your workflow with futuristic automation capabilities!

---

*Made with ❤️ and powered by SHAYAK SIRAJ*

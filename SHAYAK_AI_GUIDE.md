# 🤖 Shayak AI Assistant - Complete Guide

## 🎯 Overview
Shayak AI Assistant is a comprehensive automation system with a futuristic interface that combines voice control, screen automation, and AI-powered command execution.

## 🚀 How to Run Locally

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB
- Git

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <your-repo-url>
   cd shayak-ai-assistant
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   yarn install
   # or
   npm install
   ```

4. **Database Setup**
   ```bash
   # Install MongoDB (Ubuntu/Debian)
   sudo apt update
   sudo apt install mongodb
   
   # Start MongoDB
   sudo systemctl start mongodb
   sudo systemctl enable mongodb
   ```

5. **Environment Variables**
   Create `.env` files:
   
   **Backend (.env)**
   ```
   MONGO_URL=mongodb://localhost:27017/
   ```
   
   **Frontend (.env)**
   ```
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```

6. **Run the Application**
   
   **Start Backend:**
   ```bash
   cd backend
   python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```
   
   **Start Frontend:**
   ```bash
   cd frontend
   yarn start
   # or
   npm start
   ```

7. **Access the Application**
   Open your browser and navigate to: `http://localhost:3000`

## 🎮 How It Works

### 🎯 Core Features

#### 1. **Voice Control & AI** 🎤
- **Speech Recognition**: Uses Web Speech API for voice commands
- **Natural Language Processing**: Converts speech to actionable commands
- **Voice Level Indicator**: Shows microphone input levels
- **Wake Word Detection**: Responds to "Shayak" wake word

#### 2. **Screen Automation** 🖥️
- **Screenshot Capture**: Take screenshots of your screen
- **Mouse Control**: Click at specific coordinates or on images
- **Keyboard Automation**: Type text or press specific keys
- **Window Management**: List and activate windows
- **OCR (Optical Character Recognition)**: Extract text from images
- **Scrolling**: Automated scrolling in all directions

#### 3. **Advanced Automation** ⚡
- **Automation Sequences**: Chain multiple actions together
- **Browser Control**: Automate web browser interactions
- **Desktop App Control**: Interact with desktop applications
- **System Status Monitoring**: Check automation system health

#### 4. **Batch Processing** 📦
- **Multi-Command Execution**: Run multiple commands in sequence
- **Command History**: Track execution history
- **Batch Templates**: Save and reuse command sequences

#### 5. **Manual Command Interface** 💻
- **Direct Command Input**: Execute shell commands directly
- **Safe Command Library**: Pre-approved safe commands
- **Real-time Output**: See command results immediately

### 🔧 Technical Architecture

#### Backend (FastAPI + Python)
- **API Endpoints**: RESTful API for all functionality
- **Automation Engine**: PyAutoGUI-based screen automation
- **Database**: MongoDB for storing commands and history
- **OCR Integration**: Tesseract for text extraction
- **Audio Processing**: Speech recognition and wake word detection

#### Frontend (React)
- **Futuristic UI**: Neon-themed interface with animations
- **Real-time Updates**: Live status indicators and feedback
- **Responsive Design**: Works on different screen sizes
- **Interactive Components**: Glowing buttons and form elements

#### Database Schema
```
Collections:
- commands: Safe command library
- command_history: Execution history
- batch_history: Batch execution records
- automation_templates: Saved automation sequences
```

## 🎨 Interface Guide

### 🎭 Tab Navigation
1. **VOICE & AI**: Voice control and speech recognition
2. **MANUAL**: Direct command input interface
3. **BATCH**: Multi-command batch processing
4. **TEMPLATES**: Automation template library
5. **SCREEN**: Screen automation controls
6. **ADVANCED**: Advanced automation features

### 🎯 Key Components

#### Voice Interface
- **Start/Stop Listening**: Toggle voice recognition
- **Voice Level Bar**: Shows microphone input
- **Transcript Display**: Shows recognized speech
- **Command Input**: Manual command entry

#### Screen Automation
- **Screenshot Section**: Capture screen images
- **Click Control**: Mouse automation with coordinates
- **Type Control**: Keyboard text input
- **Key Press**: Special key combinations
- **Scroll Control**: Directional scrolling
- **OCR Section**: Text extraction from images
- **Window Management**: Application window control

#### Sidebar Information
- **Safe Commands**: Pre-approved command library
- **Recent Commands**: Command execution history
- **Batch History**: Batch execution records

## 🔐 Security Features

### Safe Commands
- Pre-approved command whitelist
- Dangerous command filtering
- Execution validation
- History tracking

### System Protection
- Sandboxed execution environment
- Permission-based access control
- Command validation before execution
- Error handling and logging

## 🚦 Status Indicators

### Connection Status
- **🟢 CONNECTED**: System is online and ready
- **🔴 DISCONNECTED**: System offline or error

### Wake Word Status
- **🟢 ACTIVE**: Listening for wake word
- **🔴 INACTIVE**: Wake word detection disabled

### Processing Status
- **Animated Spinner**: Command/automation in progress
- **Success/Error Feedback**: Operation results

## 🎯 Use Cases

### For Developers
- Automated testing workflows
- Code deployment automation
- System monitoring and maintenance
- Repetitive task automation

### For General Users
- Voice-controlled computer operations
- Screen automation for productivity
- Batch processing of routine tasks
- Accessible computing interface

### For Power Users
- Complex automation sequences
- Cross-application workflows
- System administration tasks
- Custom command creation

## 🛠️ Troubleshooting

### Common Issues
1. **Voice Recognition Not Working**
   - Check microphone permissions
   - Ensure HTTPS or localhost access
   - Test microphone in browser settings

2. **Screen Automation Failing**
   - Verify display permissions
   - Check if running in headless environment
   - Ensure proper screen resolution

3. **Database Connection Issues**
   - Verify MongoDB is running
   - Check connection string in .env
   - Ensure proper permissions

### Performance Optimization
- Use batch commands for multiple operations
- Optimize screen automation delays
- Monitor memory usage during long operations
- Regular database cleanup

## 📈 Future Enhancements

### Planned Features
- Multi-language support
- Advanced AI integrations
- Cloud synchronization
- Mobile companion app
- Plugin system for extensions

### Customization Options
- Theme customization
- Custom wake words
- Personalized command shortcuts
- User-defined automation templates

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

### Code Style
- Follow PEP 8 for Python
- Use ESLint for JavaScript
- Include proper documentation
- Add unit tests for new features

## 📝 API Documentation

### Main Endpoints
- `GET /api/` - Health check
- `POST /api/voice/process` - Process voice commands
- `POST /api/automation/screenshot` - Take screenshot
- `POST /api/automation/click` - Mouse click automation
- `POST /api/automation/type` - Keyboard input automation
- `POST /api/automation/ocr` - OCR text extraction

### Response Format
```json
{
  "success": true,
  "message": "Operation completed",
  "data": { ... },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Backend
MONGO_URL=mongodb://localhost:27017/
DEBUG=true
LOG_LEVEL=INFO

# Frontend
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_THEME=futuristic
```

### Custom Commands
Add custom commands to the safe_commands collection:
```javascript
{
  "command_key": "custom_cmd",
  "command_value": "your custom command here",
  "description": "What this command does",
  "category": "custom"
}
```

---

## 🎉 Ready to Use!

Your Shayak AI Assistant is now ready to use with its futuristic interface and powerful automation capabilities. Enjoy the sci-fi experience while boosting your productivity!

For support or questions, refer to the troubleshooting section or check the API documentation.
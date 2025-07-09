import os
import json
import subprocess
import platform
import tempfile
import uuid
import time
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from pymongo import MongoClient
import uvicorn

# Import the automation module
from automation import automation

# Initialize FastAPI app
app = FastAPI(title="Jarvis AI Assistant", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
try:
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_url)
    db = client.jarvis_ai
    commands_collection = db.commands
    history_collection = db.command_history
    batch_collection = db.batch_commands
    automation_collection = db.automation_tasks
    print(f"Connected to MongoDB at {mongo_url}")
except Exception as e:
    print(f"MongoDB connection failed: {e}")

# Global task scheduler
scheduled_tasks = {}

# Pydantic models
class CommandRequest(BaseModel):
    command: str
    user_id: str = "default"

class BatchCommandRequest(BaseModel):
    commands: List[str]
    name: str = "Batch Command"
    user_id: str = "default"

class AutomationSequenceRequest(BaseModel):
    sequence: List[Dict]
    name: str = "Automation Sequence"
    user_id: str = "default"

class ScreenshotRequest(BaseModel):
    region: Optional[Dict] = None
    filename: Optional[str] = None

class ClickRequest(BaseModel):
    x: int
    y: int
    button: str = "left"
    double_click: bool = False

class ClickImageRequest(BaseModel):
    template_image: str  # Base64 encoded image or file path
    confidence: float = 0.8
    double_click: bool = False

class TypeTextRequest(BaseModel):
    text: str
    interval: float = 0.01

class KeyPressRequest(BaseModel):
    key_combination: str

class ScrollRequest(BaseModel):
    direction: str
    amount: int = 3
    x: Optional[int] = None
    y: Optional[int] = None

class OCRRequest(BaseModel):
    region: Optional[Dict] = None
    lang: str = "eng"

class WindowRequest(BaseModel):
    window_title: str

class WaitForImageRequest(BaseModel):
    template_image: str
    timeout: int = 10
    confidence: float = 0.8

class HotkeyRequest(BaseModel):
    key_combination: str
    action: str

class WakeWordRequest(BaseModel):
    wake_word: str = "jarvis"

class CommandExecutionRequest(BaseModel):
    natural_language: str
    user_id: str = "default"
    confirm: bool = False

# Safe command whitelist for Windows/Linux
SAFE_WINDOWS_COMMANDS = {
    # File management
    'dir': 'dir',
    'ls': 'ls -la',
    'list': 'ls -la',
    'mkdir': 'mkdir',
    'create_folder': 'mkdir',
    'copy': 'cp',
    'move': 'mv',
    'del': 'rm',
    'delete': 'rm',
    'remove': 'rm',
    'cd': 'cd',
    'change_directory': 'cd',
    'pwd': 'pwd',
    'current_directory': 'pwd',
    
    # System info
    'systeminfo': 'uname -a',
    'system_info': 'uname -a',
    'tasklist': 'ps aux',
    'processes': 'ps aux',
    'ipconfig': 'ifconfig',
    'network_info': 'ifconfig',
    'date': 'date',
    'time': 'date',
    'whoami': 'whoami',
    'hostname': 'hostname',
    'uptime': 'uptime',
    'memory': 'free -h',
    'disk': 'df -h',
    'cpu': 'top -bn1 | head -10',
    
    # App launching
    'notepad': 'nano',
    'calculator': 'bc',
    'calc': 'bc',
    'explorer': 'ls -la',
    'file_explorer': 'ls -la',
    'cmd': 'bash',
    'command_prompt': 'bash',
    'powershell': 'bash',
    
    # Basic utilities
    'echo': 'echo',
    'ping': 'ping -c 4',
    'help': 'help',
    'cls': 'clear',
    'clear': 'clear',
    'tree': 'tree',
    'find': 'find',
    'grep': 'grep',
    'cat': 'cat',
    'head': 'head',
    'tail': 'tail',
    'which': 'which',
    'history': 'history',
    'env': 'env',
    'path': 'echo $PATH',
}

# Automation command templates
AUTOMATION_TEMPLATES = {
    'system_health': [
        'date',
        'uptime',
        'memory',
        'disk',
        'processes'
    ],
    'network_check': [
        'hostname',
        'network_info',
        'ping google.com'
    ],
    'file_cleanup': [
        'pwd',
        'ls -la',
        'find . -name "*.tmp"',
        'find . -name "*.log"'
    ],
    'development_setup': [
        'pwd',
        'ls -la',
        'which python',
        'which node',
        'which git'
    ],
    'security_audit': [
        'whoami',
        'groups',
        'ps aux',
        'netstat -an'
    ]
}

# Dangerous command patterns to block
DANGEROUS_PATTERNS = [
    'format', 'fdisk', 'del /s', 'rmdir /s', 'shutdown', 'restart',
    'net user', 'net localgroup', 'reg delete', 'reg add', 'sfc',
    'dism', 'bcdedit', 'diskpart', 'wmic', 'sc delete', 'sc create',
    'taskkill /f', 'del /f /q', 'rd /s /q', 'attrib +h +s +r',
    'cipher', 'icacls', 'takeown', 'runas', 'rm -rf /', 'chmod 777',
    'sudo rm', 'mkfs', 'fdisk', 'parted', 'dd if=', 'fork bomb',
    ':(){ :|:& };:', 'killall', 'reboot', 'halt', 'poweroff'
]

def is_command_safe(command: str) -> tuple[bool, str]:
    """Check if a command is safe to execute"""
    command_lower = command.lower().strip()
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if pattern in command_lower:
            return False, f"Blocked dangerous command pattern: {pattern}"
    
    # Check if command starts with a safe command
    first_word = command_lower.split()[0] if command_lower.split() else ""
    
    # Allow basic Linux commands that are generally safe
    safe_first_words = list(SAFE_WINDOWS_COMMANDS.keys()) + [
        'ls', 'cat', 'head', 'tail', 'grep', 'find', 'which', 'echo',
        'date', 'whoami', 'hostname', 'pwd', 'uname', 'uptime', 'free',
        'df', 'ps', 'top', 'history', 'env', 'ping', 'ifconfig', 'netstat'
    ]
    
    if first_word not in safe_first_words:
        return False, f"Command '{first_word}' not in safe command whitelist"
    
    return True, "Command is safe"

def execute_system_command(command: str) -> Dict:
    """Execute a system command safely"""
    try:
        # Check if command is safe
        is_safe, safety_message = is_command_safe(command)
        if not is_safe:
            return {
                "success": False,
                "output": "",
                "error": safety_message,
                "command": command,
                "timestamp": datetime.now().isoformat()
            }
        
        # Execute the command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode,
            "command": command,
            "timestamp": datetime.now().isoformat()
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Command timed out after 30 seconds",
            "command": command,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "command": command,
            "timestamp": datetime.now().isoformat()
        }

def mock_interpret_command(natural_language: str) -> Dict:
    """Mock AI interpretation for common commands when OpenAI is not available"""
    nl_lower = natural_language.lower().strip()
    
    # Common command mappings
    interpretations = {
        'show me the files': 'ls -la',
        'list files': 'ls -la',
        'show files': 'ls -la',
        'what files are here': 'ls -la',
        'list directory': 'ls -la',
        'show directory': 'ls -la',
        
        'what time is it': 'date',
        'current time': 'date',
        'show time': 'date',
        'time': 'date',
        'date': 'date',
        
        'who am i': 'whoami',
        'current user': 'whoami',
        'show user': 'whoami',
        
        'where am i': 'pwd',
        'current directory': 'pwd',
        'show current directory': 'pwd',
        'working directory': 'pwd',
        
        'system info': 'uname -a',
        'system information': 'uname -a',
        'show system info': 'uname -a',
        
        'show processes': 'ps aux',
        'running processes': 'ps aux',
        'list processes': 'ps aux',
        'tasks': 'ps aux',
        
        'network info': 'ifconfig',
        'network information': 'ifconfig',
        'show network': 'ifconfig',
        'ip address': 'ifconfig',
        
        'disk space': 'df -h',
        'disk usage': 'df -h',
        'show disk': 'df -h',
        'free space': 'df -h',
        
        'memory usage': 'free -h',
        'memory info': 'free -h',
        'show memory': 'free -h',
        'ram usage': 'free -h',
        
        'system uptime': 'uptime',
        'uptime': 'uptime',
        'how long running': 'uptime',
        
        'clear screen': 'clear',
        'clear': 'clear',
        'cls': 'clear',
        
        'ping google': 'ping -c 4 google.com',
        'test internet': 'ping -c 4 google.com',
        'check connection': 'ping -c 4 google.com',
    }
    
    # Direct mapping
    if nl_lower in interpretations:
        command = interpretations[nl_lower]
        return {
            "success": True,
            "command": command,
            "interpretation": natural_language,
            "safety_message": "Command is safe",
            "timestamp": datetime.now().isoformat(),
            "method": "mock_ai"
        }
    
    # Pattern matching
    for pattern, command in interpretations.items():
        if pattern in nl_lower:
            return {
                "success": True,
                "command": command,
                "interpretation": natural_language,
                "safety_message": "Command is safe",
                "timestamp": datetime.now().isoformat(),
                "method": "mock_ai"
            }
    
    # If no match found, try to extract command-like words
    words = nl_lower.split()
    for word in words:
        if word in SAFE_WINDOWS_COMMANDS:
            return {
                "success": True,
                "command": SAFE_WINDOWS_COMMANDS[word],
                "interpretation": natural_language,
                "safety_message": "Command is safe",
                "timestamp": datetime.now().isoformat(),
                "method": "mock_ai"
            }
    
    return {
        "success": False,
        "command": "",
        "interpretation": natural_language,
        "error": "Could not interpret command. Try: 'show me the files', 'what time is it', 'who am i', etc.",
        "timestamp": datetime.now().isoformat(),
        "method": "mock_ai"
    }

def interpret_natural_language_to_command(natural_language: str) -> Dict:
    """Use GPT or mock AI to convert natural language to commands"""
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY', 'sk-svcacct-xgoMM56QqYTdn0kcH46aT3BlbkFJJ5dEMVrwoNjH2IgkGIfA')
        )
        
        system_prompt = """You are Jarvis, an AI assistant that converts natural language to command line commands.

IMPORTANT RULES:
1. Only return commands that are SAFE and from this whitelist: ls, dir, mkdir, cp, mv, rm, cd, pwd, uname, ps, ifconfig, date, whoami, hostname, uptime, free, df, top, echo, ping, help, clear, tree, find, grep, cat, head, tail, which, history, env
2. Never return commands that could harm the system or access sensitive data
3. If the request is unclear or unsafe, ask for clarification
4. Return only the command, no explanation unless clarification is needed
5. Use Linux command syntax (forward slashes, appropriate flags)

Examples:
- "show me the files" → "ls -la"
- "what time is it" → "date"
- "who am i" → "whoami"
- "system info" → "uname -a"
- "show processes" → "ps aux"
- "clear screen" → "clear"
- "disk usage" → "df -h"
- "memory usage" → "free -h"

User request: """ + natural_language

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": natural_language}
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        command = response.choices[0].message.content.strip()
        
        # Additional safety check
        is_safe, safety_message = is_command_safe(command)
        
        return {
            "success": is_safe,
            "command": command if is_safe else "",
            "interpretation": natural_language,
            "safety_message": safety_message,
            "timestamp": datetime.now().isoformat(),
            "method": "openai"
        }
        
    except Exception as e:
        # Fall back to mock AI if OpenAI fails
        print(f"OpenAI failed, using mock AI: {e}")
        return mock_interpret_command(natural_language)

@app.get("/api/")
async def root():
    return {"message": "Jarvis AI Assistant Backend is running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "features": {
            "command_execution": True,
            "batch_commands": True,
            "automation": True,
            "ai_interpretation": True
        }
    }

@app.post("/api/transcribe-voice")
async def transcribe_voice(file: UploadFile = File(...)):
    """Transcribe voice using OpenAI Whisper"""
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY', 'sk-svcacct-xgoMM56QqYTdn0kcH46aT3BlbkFJJ5dEMVrwoNjH2IgkGIfA')
        )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Transcribe using OpenAI Whisper
        with open(tmp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return {
            "success": True,
            "transcription": transcript,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/interpret-command")
async def interpret_command(request: CommandExecutionRequest):
    """Interpret natural language and convert to command"""
    try:
        result = interpret_natural_language_to_command(request.natural_language)
        
        # Store interpretation in database
        interpretation_doc = {
            "id": str(uuid.uuid4()),
            "user_id": request.user_id,
            "natural_language": request.natural_language,
            "interpreted_command": result.get("command", ""),
            "success": result["success"],
            "method": result.get("method", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            history_collection.insert_one(interpretation_doc)
        except Exception as db_error:
            print(f"Database error: {db_error}")
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/execute-command")
async def execute_command(request: CommandRequest):
    """Execute a system command safely"""
    try:
        result = execute_system_command(request.command)
        
        # Store execution result in database
        execution_doc = {
            "id": str(uuid.uuid4()),
            "user_id": request.user_id,
            "command": request.command,
            "success": result["success"],
            "output": result.get("output", ""),
            "error": result.get("error", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            commands_collection.insert_one(execution_doc)
        except Exception as db_error:
            print(f"Database error: {db_error}")
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/batch-execute")
async def batch_execute(request: BatchCommandRequest):
    """Execute multiple commands in batch"""
    try:
        results = []
        total_success = 0
        
        for i, command in enumerate(request.commands):
            print(f"Executing batch command {i+1}/{len(request.commands)}: {command}")
            result = execute_system_command(command)
            results.append(result)
            
            if result["success"]:
                total_success += 1
            
            # Add a small delay between commands
            await asyncio.sleep(0.1)
        
        # Store batch execution in database
        batch_doc = {
            "id": str(uuid.uuid4()),
            "user_id": request.user_id,
            "name": request.name,
            "commands": request.commands,
            "results": results,
            "total_commands": len(request.commands),
            "successful_commands": total_success,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            batch_collection.insert_one(batch_doc)
        except Exception as db_error:
            print(f"Database error: {db_error}")
        
        return {
            "success": True,
            "batch_name": request.name,
            "total_commands": len(request.commands),
            "successful_commands": total_success,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/voice-command")
async def voice_command(request: CommandExecutionRequest):
    """Complete voice command pipeline: interpret + execute"""
    try:
        # Step 1: Interpret natural language
        interpretation = interpret_natural_language_to_command(request.natural_language)
        
        if not interpretation["success"]:
            return {
                "success": False,
                "stage": "interpretation",
                "error": interpretation.get("error", "Failed to interpret command"),
                "natural_language": request.natural_language,
                "timestamp": datetime.now().isoformat()
            }
        
        command = interpretation["command"]
        
        # Step 2: Execute command (if confirmed or safe)
        if request.confirm or is_command_safe(command)[0]:
            execution = execute_system_command(command)
            
            return {
                "success": execution["success"],
                "stage": "execution",
                "natural_language": request.natural_language,
                "interpreted_command": command,
                "output": execution.get("output", ""),
                "error": execution.get("error", ""),
                "method": interpretation.get("method", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "stage": "confirmation",
                "natural_language": request.natural_language,
                "interpreted_command": command,
                "message": "Command requires confirmation before execution",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/command-history")
async def get_command_history(user_id: str = "default", limit: int = 50):
    """Get command execution history"""
    try:
        history = list(
            commands_collection.find(
                {"user_id": user_id},
                {"_id": 0}
            ).sort("timestamp", -1).limit(limit)
        )
        
        return {
            "success": True,
            "history": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/batch-history")
async def get_batch_history(user_id: str = "default", limit: int = 20):
    """Get batch execution history"""
    try:
        history = list(
            batch_collection.find(
                {"user_id": user_id},
                {"_id": 0}
            ).sort("timestamp", -1).limit(limit)
        )
        
        return {
            "success": True,
            "history": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/automation-templates")
async def get_automation_templates():
    """Get automation command templates"""
    return {
        "success": True,
        "templates": AUTOMATION_TEMPLATES,
        "template_count": len(AUTOMATION_TEMPLATES),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/execute-template")
async def execute_template(template_name: str, user_id: str = "default"):
    """Execute an automation template"""
    try:
        if template_name not in AUTOMATION_TEMPLATES:
            return {
                "success": False,
                "error": f"Template '{template_name}' not found",
                "timestamp": datetime.now().isoformat()
            }
        
        commands = AUTOMATION_TEMPLATES[template_name]
        
        # Execute as batch
        batch_request = BatchCommandRequest(
            commands=commands,
            name=f"Template: {template_name}",
            user_id=user_id
        )
        
        return await batch_execute(batch_request)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/safe-commands")
async def get_safe_commands():
    """Get list of safe commands"""
    return {
        "success": True,
        "safe_commands": SAFE_WINDOWS_COMMANDS,
        "command_count": len(SAFE_WINDOWS_COMMANDS),
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# SCREEN AUTOMATION ENDPOINTS
# ============================================

@app.post("/api/automation/screenshot")
async def take_screenshot(request: ScreenshotRequest):
    """Take a screenshot of the screen or specific region"""
    try:
        region = request.region
        if region:
            region = (region.get('x'), region.get('y'), region.get('width'), region.get('height'))
        
        result = automation.take_screenshot(region=region, filename=request.filename)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/automation/click")
async def click_at_position(request: ClickRequest):
    """Click at specific coordinates"""
    try:
        result = automation.click_at_position(
            x=request.x,
            y=request.y,
            button=request.button,
            double_click=request.double_click
        )
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/automation/click-image")
async def click_on_image(request: ClickImageRequest):
    """Click on first occurrence of template image"""
    try:
        result = automation.click_on_image(
            template_image=request.template_image,
            confidence=request.confidence,
            double_click=request.double_click
        )
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/automation/type")
async def type_text(request: TypeTextRequest):
    """Type text with specified interval"""
    try:
        result = automation.type_text(
            text=request.text,
            interval=request.interval
        )
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/automation/key")
async def press_key(request: KeyPressRequest):
    """Press key or key combination"""
    try:
        result = automation.press_key(request.key_combination)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/automation/scroll")
async def scroll_screen(request: ScrollRequest):
    """Scroll in specified direction"""
    try:
        result = automation.scroll(
            direction=request.direction,
            amount=request.amount,
            x=request.x,
            y=request.y
        )
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/automation/ocr")
async def read_text_from_screen(request: OCRRequest):
    """Extract text from screen using OCR"""
    try:
        region = request.region
        if region:
            region = (region.get('x'), region.get('y'), region.get('width'), region.get('height'))
        
        result = automation.read_text_from_screen(region=region, lang=request.lang)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/automation/windows")
async def get_window_list():
    """Get list of all open windows"""
    try:
        result = automation.get_window_list()
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/automation/activate-window")
async def activate_window(request: WindowRequest):
    """Activate window by title"""
    try:
        result = automation.activate_window(request.window_title)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/automation/wait-for-image")
async def wait_for_image(request: WaitForImageRequest):
    """Wait for image to appear on screen"""
    try:
        result = automation.wait_for_image(
            template_image=request.template_image,
            timeout=request.timeout,
            confidence=request.confidence
        )
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/automation/wake-word/start")
async def start_wake_word_detection(request: WakeWordRequest):
    """Start wake word detection"""
    try:
        result = automation.start_wake_word_detection(request.wake_word)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/automation/wake-word/stop")
async def stop_wake_word_detection():
    """Stop wake word detection"""
    try:
        result = automation.stop_wake_word_detection()
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/automation/hotkey")
async def setup_hotkey(request: HotkeyRequest):
    """Setup global hotkey"""
    try:
        result = automation.setup_hotkey(request.key_combination, request.action)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/automation/sequence")
async def execute_automation_sequence(request: AutomationSequenceRequest):
    """Execute a sequence of automation actions"""
    try:
        result = automation.execute_automation_sequence(request.sequence)
        
        # Store sequence execution in database
        sequence_doc = {
            "id": str(uuid.uuid4()),
            "user_id": request.user_id,
            "name": request.name,
            "sequence": request.sequence,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            automation_collection.insert_one(sequence_doc)
        except Exception as db_error:
            print(f"Database error: {db_error}")
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/automation/status")
async def get_automation_status():
    """Get automation system status"""
    try:
        return {
            "success": True,
            "status": "active",
            "features": {
                "screenshot": True,
                "click_automation": True,
                "image_recognition": True,
                "ocr": True,
                "window_management": True,
                "wake_word": True,
                "hotkeys": True,
                "sequence_automation": True
            },
            "screen_size": {
                "width": automation.screen_width,
                "height": automation.screen_height
            },
            "wake_word_active": automation.wake_word_active,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
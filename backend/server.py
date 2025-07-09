import os
import json
import subprocess
import platform
import tempfile
import uuid
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import openai
from pymongo import MongoClient
import uvicorn

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
    print(f"Connected to MongoDB at {mongo_url}")
except Exception as e:
    print(f"MongoDB connection failed: {e}")

# OpenAI API configuration
openai.api_key = os.environ.get('OPENAI_API_KEY', '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')

# Pydantic models
class CommandRequest(BaseModel):
    command: str
    user_id: str = "default"

class VoiceTranscriptionRequest(BaseModel):
    audio_data: str
    user_id: str = "default"

class CommandExecutionRequest(BaseModel):
    natural_language: str
    user_id: str = "default"
    confirm: bool = False

# Safe command whitelist for Windows
SAFE_WINDOWS_COMMANDS = {
    # File management
    'dir': 'dir',
    'ls': 'dir',
    'list': 'dir',
    'mkdir': 'mkdir',
    'create_folder': 'mkdir',
    'copy': 'copy',
    'move': 'move',
    'del': 'del',
    'delete': 'del',
    'remove': 'del',
    'cd': 'cd',
    'change_directory': 'cd',
    
    # System info
    'systeminfo': 'systeminfo',
    'system_info': 'systeminfo',
    'tasklist': 'tasklist',
    'processes': 'tasklist',
    'ipconfig': 'ipconfig',
    'network_info': 'ipconfig',
    'date': 'date',
    'time': 'time',
    'whoami': 'whoami',
    'hostname': 'hostname',
    
    # App launching
    'notepad': 'notepad',
    'calculator': 'calc',
    'calc': 'calc',
    'explorer': 'explorer',
    'file_explorer': 'explorer',
    'cmd': 'cmd',
    'command_prompt': 'cmd',
    'powershell': 'powershell',
    
    # Basic utilities
    'echo': 'echo',
    'ping': 'ping',
    'help': 'help',
    'cls': 'cls',
    'clear': 'cls',
    'tree': 'tree',
    'vol': 'vol',
    'type': 'type',
    'find': 'find',
}

# Dangerous command patterns to block
DANGEROUS_PATTERNS = [
    'format', 'fdisk', 'del /s', 'rmdir /s', 'shutdown', 'restart',
    'net user', 'net localgroup', 'reg delete', 'reg add', 'sfc',
    'dism', 'bcdedit', 'diskpart', 'wmic', 'sc delete', 'sc create',
    'taskkill /f', 'del /f /q', 'rd /s /q', 'attrib +h +s +r',
    'cipher', 'icacls', 'takeown', 'runas', 'powershell -windowstyle hidden'
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
    if first_word not in SAFE_WINDOWS_COMMANDS:
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

def interpret_natural_language_to_command(natural_language: str) -> Dict:
    """Use GPT-4 to convert natural language to Windows commands"""
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY', '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')
        )
        
        system_prompt = """You are Jarvis, an AI assistant that converts natural language to Windows command line commands.

IMPORTANT RULES:
1. Only return Windows CMD commands that are SAFE and from this whitelist: dir, mkdir, copy, move, del, cd, systeminfo, tasklist, ipconfig, date, time, whoami, hostname, notepad, calc, explorer, cmd, powershell, echo, ping, help, cls, tree, vol, type, find
2. Never return commands that could harm the system or access sensitive data
3. If the request is unclear or unsafe, ask for clarification
4. Return only the command, no explanation unless clarification is needed
5. For file operations, use Windows path syntax (backslashes)
6. For app launching, use simple executable names

Examples:
- "show me the files" → "dir"
- "create a folder called test" → "mkdir test"
- "open notepad" → "notepad"
- "what's my IP address" → "ipconfig"
- "show running processes" → "tasklist"
- "clear the screen" → "cls"
- "open file explorer" → "explorer"
- "what time is it" → "time"

User request: """ + natural_language

        response = client.chat.completions.create(
            model="gpt-4",
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
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "command": "",
            "interpretation": natural_language,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/")
async def root():
    return {"message": "Jarvis AI Assistant Backend is running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "platform": platform.system(),
        "python_version": platform.python_version()
    }

@app.post("/api/transcribe-voice")
async def transcribe_voice(file: UploadFile = File(...)):
    """Transcribe voice using OpenAI Whisper"""
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY', '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')
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

@app.get("/api/safe-commands")
async def get_safe_commands():
    """Get list of safe commands"""
    return {
        "success": True,
        "safe_commands": SAFE_WINDOWS_COMMANDS,
        "command_count": len(SAFE_WINDOWS_COMMANDS),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
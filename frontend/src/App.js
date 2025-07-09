import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const App = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [command, setCommand] = useState('');
  const [output, setOutput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [commandHistory, setCommandHistory] = useState([]);
  const [voiceLevel, setVoiceLevel] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [safeCommands, setSafeCommands] = useState({});
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Initialize app and check connection
  useEffect(() => {
    checkConnection();
    loadSafeCommands();
    loadCommandHistory();
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  const checkConnection = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/health`);
      const data = await response.json();
      setIsConnected(data.status === 'healthy');
    } catch (error) {
      console.error('Connection check failed:', error);
      setIsConnected(false);
    }
  };

  const loadSafeCommands = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/safe-commands`);
      const data = await response.json();
      if (data.success) {
        setSafeCommands(data.safe_commands);
      }
    } catch (error) {
      console.error('Failed to load safe commands:', error);
    }
  };

  const loadCommandHistory = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/command-history`);
      const data = await response.json();
      if (data.success) {
        setCommandHistory(data.history);
      }
    } catch (error) {
      console.error('Failed to load command history:', error);
    }
  };

  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Set up audio context for visualization
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      
      analyserRef.current.fftSize = 256;
      const bufferLength = analyserRef.current.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      const updateVoiceLevel = () => {
        analyserRef.current.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / bufferLength;
        setVoiceLevel(average);
        animationFrameRef.current = requestAnimationFrame(updateVoiceLevel);
      };
      updateVoiceLevel();
      
      // Set up media recorder
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      
      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        transcribeAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorderRef.current.start();
      setIsListening(true);
      setTranscript('Listening...');
      
    } catch (error) {
      console.error('Error starting voice recording:', error);
      setTranscript('Error: Could not access microphone');
    }
  };

  const stopVoiceRecording = () => {
    if (mediaRecorderRef.current && isListening) {
      mediaRecorderRef.current.stop();
      setIsListening(false);
      setTranscript('Processing...');
      
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      setVoiceLevel(0);
    }
  };

  const transcribeAudio = async (audioBlob) => {
    try {
      setIsProcessing(true);
      const formData = new FormData();
      formData.append('file', audioBlob, 'audio.wav');
      
      const response = await fetch(`${BACKEND_URL}/api/transcribe-voice`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (data.success) {
        setTranscript(data.transcription);
        executeVoiceCommand(data.transcription);
      } else {
        setTranscript('Error: ' + data.error);
      }
      
    } catch (error) {
      console.error('Error transcribing audio:', error);
      setTranscript('Error: Failed to transcribe audio');
    } finally {
      setIsProcessing(false);
    }
  };

  const executeVoiceCommand = async (naturalLanguage) => {
    try {
      setIsProcessing(true);
      setOutput('Processing command...');
      
      const response = await fetch(`${BACKEND_URL}/api/voice-command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          natural_language: naturalLanguage,
          confirm: true
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setCommand(data.interpreted_command);
        setOutput(data.output || 'Command executed successfully');
        speakResponse(`Command completed: ${data.interpreted_command}`);
      } else {
        setOutput(`Error: ${data.error || 'Command failed'}`);
        speakResponse(`Error: ${data.error || 'Command failed'}`);
      }
      
      // Reload command history
      loadCommandHistory();
      
    } catch (error) {
      console.error('Error executing voice command:', error);
      setOutput('Error: Failed to execute command');
      speakResponse('Error: Failed to execute command');
    } finally {
      setIsProcessing(false);
    }
  };

  const executeTextCommand = async () => {
    if (!command.trim()) return;
    
    try {
      setIsProcessing(true);
      setOutput('Executing command...');
      
      const response = await fetch(`${BACKEND_URL}/api/execute-command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: command
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setOutput(data.output || 'Command executed successfully');
        speakResponse('Command completed successfully');
      } else {
        setOutput(`Error: ${data.error || 'Command failed'}`);
        speakResponse(`Error: ${data.error || 'Command failed'}`);
      }
      
      // Reload command history
      loadCommandHistory();
      
    } catch (error) {
      console.error('Error executing command:', error);
      setOutput('Error: Failed to execute command');
      speakResponse('Error: Failed to execute command');
    } finally {
      setIsProcessing(false);
    }
  };

  const speakResponse = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;
      window.speechSynthesis.speak(utterance);
    }
  };

  const clearAll = () => {
    setTranscript('');
    setCommand('');
    setOutput('');
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="jarvis-container">
      {/* Header */}
      <div className="jarvis-header">
        <div className="jarvis-title">
          <div className="jarvis-logo">🤖</div>
          <h1>JARVIS AI Assistant</h1>
          <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </div>
        </div>
      </div>

      {/* Main Interface */}
      <div className="jarvis-main">
        {/* Voice Interface */}
        <div className="voice-interface">
          <div className="voice-controls">
            <button
              className={`voice-button ${isListening ? 'listening' : ''}`}
              onClick={isListening ? stopVoiceRecording : startVoiceRecording}
              disabled={isProcessing}
            >
              {isListening ? '🎤 Stop Listening' : '🎤 Start Voice Command'}
            </button>
            
            {isListening && (
              <div className="voice-level">
                <div 
                  className="voice-level-bar" 
                  style={{ width: `${Math.min(voiceLevel * 2, 100)}%` }}
                />
              </div>
            )}
          </div>
          
          <div className="transcript-display">
            <label>Voice Transcript:</label>
            <div className="transcript-text">{transcript}</div>
          </div>
        </div>

        {/* Command Interface */}
        <div className="command-interface">
          <div className="command-input">
            <label>Manual Command:</label>
            <div className="input-group">
              <input
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="Enter command or use voice..."
                onKeyPress={(e) => e.key === 'Enter' && executeTextCommand()}
              />
              <button 
                onClick={executeTextCommand}
                disabled={isProcessing || !command.trim()}
              >
                Execute
              </button>
            </div>
          </div>
          
          <div className="output-display">
            <label>Command Output:</label>
            <pre className="output-text">{output}</pre>
          </div>
        </div>

        {/* Control Buttons */}
        <div className="control-buttons">
          <button onClick={clearAll} className="clear-btn">
            🗑️ Clear All
          </button>
          <button onClick={loadCommandHistory} className="refresh-btn">
            🔄 Refresh History
          </button>
        </div>
      </div>

      {/* Sidebar */}
      <div className="jarvis-sidebar">
        {/* Safe Commands */}
        <div className="sidebar-section">
          <h3>Safe Commands</h3>
          <div className="safe-commands">
            {Object.entries(safeCommands).map(([key, cmd]) => (
              <div key={key} className="safe-command-item">
                <span className="command-key">{key}</span>
                <span className="command-value">{cmd}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Command History */}
        <div className="sidebar-section">
          <h3>Recent Commands</h3>
          <div className="command-history">
            {commandHistory.slice(0, 10).map((item, index) => (
              <div key={index} className="history-item">
                <div className="history-command">{item.command}</div>
                <div className="history-timestamp">{formatTimestamp(item.timestamp)}</div>
                <div className={`history-status ${item.success ? 'success' : 'error'}`}>
                  {item.success ? '✅' : '❌'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Processing Overlay */}
      {isProcessing && (
        <div className="processing-overlay">
          <div className="processing-spinner"></div>
          <div className="processing-text">Processing...</div>
        </div>
      )}
    </div>
  );
};

export default App;
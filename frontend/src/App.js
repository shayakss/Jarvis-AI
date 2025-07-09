import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const App = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [command, setCommand] = useState('');
  const [output, setOutput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [commandHistory, setCommandHistory] = useState([]);
  const [batchHistory, setBatchHistory] = useState([]);
  const [voiceLevel, setVoiceLevel] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [safeCommands, setSafeCommands] = useState({});
  const [automationTemplates, setAutomationTemplates] = useState({});
  const [activeTab, setActiveTab] = useState('voice');
  const [batchCommands, setBatchCommands] = useState(['']);
  const [batchName, setBatchName] = useState('');
  
  // Automation state
  const [automationStatus, setAutomationStatus] = useState({});
  const [screenshot, setScreenshot] = useState(null);
  const [windowList, setWindowList] = useState([]);
  const [ocrResult, setOcrResult] = useState('');
  const [isWakeWordActive, setIsWakeWordActive] = useState(false);
  const [automationSequence, setAutomationSequence] = useState([]);
  const [coordinateX, setCoordinateX] = useState('');
  const [coordinateY, setCoordinateY] = useState('');
  const [textToType, setTextToType] = useState('');
  const [keyToPress, setKeyToPress] = useState('');
  const [scrollDirection, setScrollDirection] = useState('up');
  const [scrollAmount, setScrollAmount] = useState(3);
  const [selectedWindow, setSelectedWindow] = useState('');
  
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
    loadBatchHistory();
    loadAutomationTemplates();
    loadAutomationStatus();
    loadWindowList();
    
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

  const loadBatchHistory = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/batch-history`);
      const data = await response.json();
      if (data.success) {
        setBatchHistory(data.history);
      }
    } catch (error) {
      console.error('Failed to load batch history:', error);
    }
  };

  const loadAutomationTemplates = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/automation-templates`);
      const data = await response.json();
      if (data.success) {
        setAutomationTemplates(data.templates);
      }
    } catch (error) {
      console.error('Failed to load automation templates:', error);
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
      setTranscript('Error: Could not access microphone. Try using manual commands instead.');
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
      setTranscript('Error: Failed to transcribe audio. Try typing commands instead.');
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

  const executeNaturalLanguage = async (naturalLanguage) => {
    if (!naturalLanguage.trim()) return;
    
    try {
      setIsProcessing(true);
      setOutput('Interpreting and executing...');
      
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
        speakResponse(`Executed: ${data.interpreted_command}`);
      } else {
        setOutput(`Error: ${data.error || 'Command failed'}`);
        speakResponse(`Error: ${data.error || 'Command failed'}`);
      }
      
      // Reload command history
      loadCommandHistory();
      
    } catch (error) {
      console.error('Error executing natural language command:', error);
      setOutput('Error: Failed to execute command');
      speakResponse('Error: Failed to execute command');
    } finally {
      setIsProcessing(false);
    }
  };

  const executeBatchCommands = async () => {
    const validCommands = batchCommands.filter(cmd => cmd.trim());
    if (validCommands.length === 0) return;
    
    try {
      setIsProcessing(true);
      setOutput('Executing batch commands...');
      
      const response = await fetch(`${BACKEND_URL}/api/batch-execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          commands: validCommands,
          name: batchName || 'Custom Batch'
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        let output = `Batch "${data.batch_name}" completed:\n`;
        output += `${data.successful_commands}/${data.total_commands} commands successful\n\n`;
        
        data.results.forEach((result, index) => {
          output += `Command ${index + 1}: ${validCommands[index]}\n`;
          output += `Status: ${result.success ? '✅ Success' : '❌ Failed'}\n`;
          if (result.output) output += `Output: ${result.output}\n`;
          if (result.error) output += `Error: ${result.error}\n`;
          output += '\n';
        });
        
        setOutput(output);
        speakResponse(`Batch completed: ${data.successful_commands} of ${data.total_commands} commands successful`);
      } else {
        setOutput(`Error: ${data.error || 'Batch execution failed'}`);
        speakResponse(`Error: ${data.error || 'Batch execution failed'}`);
      }
      
      // Reload histories
      loadCommandHistory();
      loadBatchHistory();
      
    } catch (error) {
      console.error('Error executing batch commands:', error);
      setOutput('Error: Failed to execute batch commands');
      speakResponse('Error: Failed to execute batch commands');
    } finally {
      setIsProcessing(false);
    }
  };

  const executeTemplate = async (templateName) => {
    try {
      setIsProcessing(true);
      setOutput(`Executing automation template: ${templateName}...`);
      
      const response = await fetch(`${BACKEND_URL}/api/execute-template?template_name=${templateName}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.success) {
        let output = `Template "${templateName}" completed:\n`;
        output += `${data.successful_commands}/${data.total_commands} commands successful\n\n`;
        
        data.results.forEach((result, index) => {
          output += `Command ${index + 1}: ${result.command}\n`;
          output += `Status: ${result.success ? '✅ Success' : '❌ Failed'}\n`;
          if (result.output) output += `Output: ${result.output}\n`;
          if (result.error) output += `Error: ${result.error}\n`;
          output += '\n';
        });
        
        setOutput(output);
        speakResponse(`Template ${templateName} completed: ${data.successful_commands} of ${data.total_commands} commands successful`);
      } else {
        setOutput(`Error: ${data.error || 'Template execution failed'}`);
        speakResponse(`Error: ${data.error || 'Template execution failed'}`);
      }
      
      // Reload histories
      loadCommandHistory();
      loadBatchHistory();
      
    } catch (error) {
      console.error('Error executing template:', error);
      setOutput('Error: Failed to execute template');
      speakResponse('Error: Failed to execute template');
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

  const addBatchCommand = () => {
    setBatchCommands([...batchCommands, '']);
  };

  const removeBatchCommand = (index) => {
    setBatchCommands(batchCommands.filter((_, i) => i !== index));
  };

  const updateBatchCommand = (index, value) => {
    const newCommands = [...batchCommands];
    newCommands[index] = value;
    setBatchCommands(newCommands);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const renderVoiceTab = () => (
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
      
      <div className="natural-language-input">
        <label>Or type natural language:</label>
        <div className="input-group">
          <input
            type="text"
            placeholder="E.g., 'show me the files', 'what time is it', 'system info'"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                executeNaturalLanguage(e.target.value);
                e.target.value = '';
              }
            }}
          />
          <button 
            onClick={(e) => {
              const input = e.target.previousElementSibling;
              executeNaturalLanguage(input.value);
              input.value = '';
            }}
            disabled={isProcessing}
          >
            Execute
          </button>
        </div>
      </div>
    </div>
  );

  const renderBatchTab = () => (
    <div className="batch-interface">
      <div className="batch-controls">
        <div className="batch-name">
          <label>Batch Name:</label>
          <input
            type="text"
            value={batchName}
            onChange={(e) => setBatchName(e.target.value)}
            placeholder="Enter batch name"
          />
        </div>
        
        <div className="batch-commands">
          <label>Commands:</label>
          {batchCommands.map((cmd, index) => (
            <div key={index} className="batch-command-row">
              <input
                type="text"
                value={cmd}
                onChange={(e) => updateBatchCommand(index, e.target.value)}
                placeholder={`Command ${index + 1}`}
              />
              <button onClick={() => removeBatchCommand(index)} className="remove-btn">
                ❌
              </button>
            </div>
          ))}
          <button onClick={addBatchCommand} className="add-btn">
            ➕ Add Command
          </button>
        </div>
        
        <button
          onClick={executeBatchCommands}
          disabled={isProcessing || batchCommands.filter(cmd => cmd.trim()).length === 0}
          className="execute-batch-btn"
        >
          🚀 Execute Batch
        </button>
      </div>
    </div>
  );

  const renderAutomationTab = () => (
    <div className="automation-interface">
      <div className="automation-templates">
        <h3>🤖 Automation Templates</h3>
        <div className="templates-grid">
          {Object.entries(automationTemplates).map(([name, commands]) => (
            <div key={name} className="template-card">
              <h4>{name.replace('_', ' ').toUpperCase()}</h4>
              <div className="template-commands">
                {commands.map((cmd, index) => (
                  <div key={index} className="template-command">{cmd}</div>
                ))}
              </div>
              <button
                onClick={() => executeTemplate(name)}
                disabled={isProcessing}
                className="execute-template-btn"
              >
                Execute Template
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

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

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-btn ${activeTab === 'voice' ? 'active' : ''}`}
          onClick={() => setActiveTab('voice')}
        >
          🎤 Voice & AI
        </button>
        <button 
          className={`tab-btn ${activeTab === 'manual' ? 'active' : ''}`}
          onClick={() => setActiveTab('manual')}
        >
          ⌨️ Manual
        </button>
        <button 
          className={`tab-btn ${activeTab === 'batch' ? 'active' : ''}`}
          onClick={() => setActiveTab('batch')}
        >
          📦 Batch
        </button>
        <button 
          className={`tab-btn ${activeTab === 'automation' ? 'active' : ''}`}
          onClick={() => setActiveTab('automation')}
        >
          🤖 Automation
        </button>
      </div>

      {/* Main Interface */}
      <div className="jarvis-main">
        {/* Tab Content */}
        {activeTab === 'voice' && renderVoiceTab()}
        
        {activeTab === 'manual' && (
          <div className="command-interface">
            <div className="command-input">
              <label>Manual Command:</label>
              <div className="input-group">
                <input
                  type="text"
                  value={command}
                  onChange={(e) => setCommand(e.target.value)}
                  placeholder="Enter command directly (e.g., ls -la, date, whoami)"
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
          </div>
        )}
        
        {activeTab === 'batch' && renderBatchTab()}
        {activeTab === 'automation' && renderAutomationTab()}
        
        {/* Output Display */}
        <div className="output-display">
          <label>Command Output:</label>
          <pre className="output-text">{output}</pre>
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
            {Object.entries(safeCommands).slice(0, 10).map(([key, cmd]) => (
              <div key={key} className="safe-command-item">
                <span className="command-key">{key}</span>
                <span className="command-value">{cmd}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Commands */}
        <div className="sidebar-section">
          <h3>Recent Commands</h3>
          <div className="command-history">
            {commandHistory.slice(0, 8).map((item, index) => (
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

        {/* Batch History */}
        <div className="sidebar-section">
          <h3>Batch History</h3>
          <div className="batch-history">
            {batchHistory.slice(0, 5).map((item, index) => (
              <div key={index} className="batch-item">
                <div className="batch-name">{item.name}</div>
                <div className="batch-stats">
                  {item.successful_commands}/{item.total_commands} successful
                </div>
                <div className="batch-timestamp">{formatTimestamp(item.timestamp)}</div>
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
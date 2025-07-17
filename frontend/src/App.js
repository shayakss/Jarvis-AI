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
  const [activeTab, setActiveTab] = useState('dashboard');
  const [batchCommands, setBatchCommands] = useState(['']);
  const [batchName, setBatchName] = useState('');
  
  // Dashboard state
  const [systemStats, setSystemStats] = useState({
    cpu: 0,
    memory: 0,
    disk: 0,
    uptime: '0:00:00',
    activeConnections: 0,
    tasksCompleted: 0,
    tasksQueue: 0,
    automationStatus: 'idle'
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);
  const [quickActions, setQuickActions] = useState([
    { id: 1, name: 'Take Screenshot', icon: '📸', action: 'screenshot' },
    { id: 2, name: 'System Check', icon: '🔍', action: 'health' },
    { id: 3, name: 'Voice Command', icon: '🎤', action: 'voice' },
    { id: 4, name: 'Batch Execute', icon: '⚡', action: 'batch' }
  ]);
  
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
    loadDashboardData();
    
    // Auto-refresh dashboard data every 5 seconds
    const dashboardInterval = setInterval(() => {
      if (activeTab === 'dashboard') {
        loadDashboardData();
      }
    }, 5000);
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      clearInterval(dashboardInterval);
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

  const loadAutomationStatus = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/automation/status`);
      const data = await response.json();
      if (data.success) {
        setAutomationStatus(data);
        setIsWakeWordActive(data.wake_word_active);
      }
    } catch (error) {
      console.error('Failed to load automation status:', error);
    }
  };

  const loadWindowList = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/automation/windows`);
      const data = await response.json();
      if (data.success) {
        setWindowList(data.windows);
      }
    } catch (error) {
      console.error('Failed to load window list:', error);
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

  // ============================================
  // AUTOMATION FUNCTIONS
  // ============================================

  const takeScreenshot = async () => {
    try {
      setIsProcessing(true);
      const response = await fetch(`${BACKEND_URL}/api/automation/screenshot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
      });
      
      const data = await response.json();
      if (data.success) {
        setScreenshot(data.image_base64);
        setOutput(`Screenshot taken: ${data.filename} (${data.size[0]}x${data.size[1]})`);
      } else {
        setOutput(`Screenshot failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Screenshot error:', error);
      setOutput('Screenshot failed: Network error');
    } finally {
      setIsProcessing(false);
    }
  };

  const clickAtPosition = async () => {
    if (!coordinateX || !coordinateY) return;
    
    try {
      setIsProcessing(true);
      const response = await fetch(`${BACKEND_URL}/api/automation/click`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          x: parseInt(coordinateX),
          y: parseInt(coordinateY),
          button: 'left'
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setOutput(`Clicked at position (${data.position.x}, ${data.position.y})`);
      } else {
        setOutput(`Click failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Click error:', error);
      setOutput('Click failed: Network error');
    } finally {
      setIsProcessing(false);
    }
  };

  const typeText = async () => {
    if (!textToType) return;
    
    try {
      setIsProcessing(true);
      const response = await fetch(`${BACKEND_URL}/api/automation/type`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: textToType,
          interval: 0.01
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setOutput(`Typed text: "${data.text}" (${data.character_count} characters)`);
      } else {
        setOutput(`Type failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Type error:', error);
      setOutput('Type failed: Network error');
    } finally {
      setIsProcessing(false);
    }
  };

  const pressKey = async () => {
    if (!keyToPress) return;
    
    try {
      setIsProcessing(true);
      const response = await fetch(`${BACKEND_URL}/api/automation/key`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          key_combination: keyToPress
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setOutput(`Pressed key: ${data.key_combination}`);
      } else {
        setOutput(`Key press failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Key press error:', error);
      setOutput('Key press failed: Network error');
    } finally {
      setIsProcessing(false);
    }
  };

  const scrollScreen = async () => {
    try {
      setIsProcessing(true);
      const response = await fetch(`${BACKEND_URL}/api/automation/scroll`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          direction: scrollDirection,
          amount: scrollAmount
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setOutput(`Scrolled ${data.direction} by ${data.amount} units`);
      } else {
        setOutput(`Scroll failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Scroll error:', error);
      setOutput('Scroll failed: Network error');
    } finally {
      setIsProcessing(false);
    }
  };

  const performOCR = async () => {
    try {
      setIsProcessing(true);
      const response = await fetch(`${BACKEND_URL}/api/automation/ocr`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lang: 'eng'
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setOcrResult(data.text);
        setOutput(`OCR completed: Found ${data.word_count} words`);
      } else {
        setOutput(`OCR failed: ${data.error}`);
      }
    } catch (error) {
      console.error('OCR error:', error);
      setOutput('OCR failed: Network error');
    } finally {
      setIsProcessing(false);
    }
  };

  const activateWindow = async () => {
    if (!selectedWindow) return;
    
    try {
      setIsProcessing(true);
      const response = await fetch(`${BACKEND_URL}/api/automation/activate-window`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          window_title: selectedWindow
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setOutput(`Activated window: ${data.window_title}`);
      } else {
        setOutput(`Window activation failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Window activation error:', error);
      setOutput('Window activation failed: Network error');
    } finally {
      setIsProcessing(false);
    }
  };

  const toggleWakeWord = async () => {
    try {
      setIsProcessing(true);
      const endpoint = isWakeWordActive ? '/api/automation/wake-word/stop' : '/api/automation/wake-word/start';
      const method = 'POST';
      const body = isWakeWordActive ? {} : { wake_word: 'shayak' };
      
      const response = await fetch(`${BACKEND_URL}${endpoint}`, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      });
      
      const data = await response.json();
      if (data.success) {
        setIsWakeWordActive(!isWakeWordActive);
        setOutput(`Wake word detection ${isWakeWordActive ? 'stopped' : 'started'}`);
      } else {
        setOutput(`Wake word toggle failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Wake word toggle error:', error);
      setOutput('Wake word toggle failed: Network error');
    } finally {
      setIsProcessing(false);
    }
  };

  const executeAutomationSequence = async () => {
    if (automationSequence.length === 0) return;
    
    try {
      setIsProcessing(true);
      const response = await fetch(`${BACKEND_URL}/api/automation/sequence`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sequence: automationSequence,
          name: 'Custom Sequence'
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setOutput(`Sequence completed: ${data.successful_actions}/${data.total_actions} actions successful`);
      } else {
        setOutput(`Sequence failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Sequence error:', error);
      setOutput('Sequence failed: Network error');
    } finally {
      setIsProcessing(false);
    }
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

  const renderScreenAutomationTab = () => (
    <div className="screen-automation-interface">
      <div className="automation-controls">
        <h3>🖥️ Screen Automation</h3>
        
        {/* Screenshot Section */}
        <div className="automation-section">
          <h4>📸 Screenshot</h4>
          <div className="control-row">
            <button onClick={takeScreenshot} disabled={isProcessing} className="automation-btn">
              Take Screenshot
            </button>
          </div>
          {screenshot && (
            <div className="screenshot-preview">
              <img src={`data:image/png;base64,${screenshot}`} alt="Screenshot" style={{maxWidth: '300px', maxHeight: '200px'}} />
            </div>
          )}
        </div>

        {/* Click Section */}
        <div className="automation-section">
          <h4>🖱️ Click Control</h4>
          <div className="control-row">
            <input
              type="number"
              value={coordinateX}
              onChange={(e) => setCoordinateX(e.target.value)}
              placeholder="X coordinate"
              className="coordinate-input"
            />
            <input
              type="number"
              value={coordinateY}
              onChange={(e) => setCoordinateY(e.target.value)}
              placeholder="Y coordinate"
              className="coordinate-input"
            />
            <button onClick={clickAtPosition} disabled={isProcessing} className="automation-btn">
              Click
            </button>
          </div>
        </div>

        {/* Type Text Section */}
        <div className="automation-section">
          <h4>⌨️ Type Text</h4>
          <div className="control-row">
            <input
              type="text"
              value={textToType}
              onChange={(e) => setTextToType(e.target.value)}
              placeholder="Text to type"
              className="text-input"
            />
            <button onClick={typeText} disabled={isProcessing} className="automation-btn">
              Type
            </button>
          </div>
        </div>

        {/* Key Press Section */}
        <div className="automation-section">
          <h4>🔑 Key Press</h4>
          <div className="control-row">
            <input
              type="text"
              value={keyToPress}
              onChange={(e) => setKeyToPress(e.target.value)}
              placeholder="Key combination (e.g., ctrl+c, enter)"
              className="text-input"
            />
            <button onClick={pressKey} disabled={isProcessing} className="automation-btn">
              Press
            </button>
          </div>
        </div>

        {/* Scroll Section */}
        <div className="automation-section">
          <h4>📜 Scroll</h4>
          <div className="control-row">
            <select
              value={scrollDirection}
              onChange={(e) => setScrollDirection(e.target.value)}
              className="scroll-select"
            >
              <option value="up">Up</option>
              <option value="down">Down</option>
              <option value="left">Left</option>
              <option value="right">Right</option>
            </select>
            <input
              type="number"
              value={scrollAmount}
              onChange={(e) => setScrollAmount(parseInt(e.target.value))}
              min="1"
              max="10"
              className="scroll-amount"
            />
            <button onClick={scrollScreen} disabled={isProcessing} className="automation-btn">
              Scroll
            </button>
          </div>
        </div>

        {/* OCR Section */}
        <div className="automation-section">
          <h4>👁️ OCR (Read Screen)</h4>
          <div className="control-row">
            <button onClick={performOCR} disabled={isProcessing} className="automation-btn">
              Read Screen Text
            </button>
          </div>
          {ocrResult && (
            <div className="ocr-result">
              <h5>Detected Text:</h5>
              <pre>{ocrResult}</pre>
            </div>
          )}
        </div>

        {/* Window Management Section */}
        <div className="automation-section">
          <h4>🪟 Window Management</h4>
          <div className="control-row">
            <select
              value={selectedWindow}
              onChange={(e) => setSelectedWindow(e.target.value)}
              className="window-select"
            >
              <option value="">Select Window</option>
              {windowList.map((window, index) => (
                <option key={index} value={window.title}>
                  {window.title}
                </option>
              ))}
            </select>
            <button onClick={activateWindow} disabled={isProcessing} className="automation-btn">
              Activate
            </button>
            <button onClick={loadWindowList} disabled={isProcessing} className="automation-btn">
              Refresh
            </button>
          </div>
        </div>

        {/* Wake Word Section */}
        <div className="automation-section">
          <h4>🎤 Wake Word</h4>
          <div className="control-row">
            <span className={`wake-word-status ${isWakeWordActive ? 'active' : 'inactive'}`}>
              Status: {isWakeWordActive ? 'Active' : 'Inactive'}
            </span>
            <button onClick={toggleWakeWord} disabled={isProcessing} className="automation-btn">
              {isWakeWordActive ? 'Stop' : 'Start'} Wake Word
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAdvancedAutomationTab = () => (
    <div className="advanced-automation-interface">
      <div className="automation-controls">
        <h3>🚀 Advanced Automation</h3>
        
        {/* Automation Status */}
        <div className="automation-section">
          <h4>📊 System Status</h4>
          <div className="status-grid">
            <div className="status-item">
              <span>Screen Size:</span>
              <span>{automationStatus.screen_size?.width}x{automationStatus.screen_size?.height}</span>
            </div>
            <div className="status-item">
              <span>Screenshot:</span>
              <span className={automationStatus.features?.screenshot ? 'status-active' : 'status-inactive'}>
                {automationStatus.features?.screenshot ? '✅' : '❌'}
              </span>
            </div>
            <div className="status-item">
              <span>Click Automation:</span>
              <span className={automationStatus.features?.click_automation ? 'status-active' : 'status-inactive'}>
                {automationStatus.features?.click_automation ? '✅' : '❌'}
              </span>
            </div>
            <div className="status-item">
              <span>Image Recognition:</span>
              <span className={automationStatus.features?.image_recognition ? 'status-active' : 'status-inactive'}>
                {automationStatus.features?.image_recognition ? '✅' : '❌'}
              </span>
            </div>
            <div className="status-item">
              <span>OCR:</span>
              <span className={automationStatus.features?.ocr ? 'status-active' : 'status-inactive'}>
                {automationStatus.features?.ocr ? '✅' : '❌'}
              </span>
            </div>
            <div className="status-item">
              <span>Wake Word:</span>
              <span className={automationStatus.features?.wake_word ? 'status-active' : 'status-inactive'}>
                {automationStatus.features?.wake_word ? '✅' : '❌'}
              </span>
            </div>
          </div>
        </div>

        {/* Sequence Builder */}
        <div className="automation-section">
          <h4>📝 Automation Sequence Builder</h4>
          <div className="sequence-builder">
            <p>Feature coming soon - Build complex automation sequences</p>
            <button onClick={executeAutomationSequence} disabled={isProcessing || automationSequence.length === 0} className="automation-btn">
              Execute Sequence
            </button>
          </div>
        </div>

        {/* Browser Automation */}
        <div className="automation-section">
          <h4>🌐 Browser Automation</h4>
          <div className="browser-controls">
            <button onClick={() => activateWindow('Chrome')} disabled={isProcessing} className="automation-btn">
              Activate Chrome
            </button>
            <button onClick={() => activateWindow('Firefox')} disabled={isProcessing} className="automation-btn">
              Activate Firefox
            </button>
            <button onClick={() => activateWindow('Edge')} disabled={isProcessing} className="automation-btn">
              Activate Edge
            </button>
          </div>
        </div>

        {/* Desktop App Automation */}
        <div className="automation-section">
          <h4>🖥️ Desktop App Automation</h4>
          <div className="desktop-controls">
            <button onClick={() => activateWindow('Notepad')} disabled={isProcessing} className="automation-btn">
              Activate Notepad
            </button>
            <button onClick={() => activateWindow('Calculator')} disabled={isProcessing} className="automation-btn">
              Activate Calculator
            </button>
            <button onClick={() => activateWindow('File Explorer')} disabled={isProcessing} className="automation-btn">
              Activate Explorer
            </button>
          </div>
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
          <h1>Shayak AI Assistant</h1>
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
          🤖 Templates
        </button>
        <button 
          className={`tab-btn ${activeTab === 'screen' ? 'active' : ''}`}
          onClick={() => setActiveTab('screen')}
        >
          🖥️ Screen
        </button>
        <button 
          className={`tab-btn ${activeTab === 'advanced' ? 'active' : ''}`}
          onClick={() => setActiveTab('advanced')}
        >
          🚀 Advanced
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
        {activeTab === 'screen' && renderScreenAutomationTab()}
        {activeTab === 'advanced' && renderAdvancedAutomationTab()}
        
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
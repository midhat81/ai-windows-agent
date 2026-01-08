import React, { useState, useEffect, useRef } from 'react';
import { 
  Mic, 
  MicOff, 
  Send, 
  Loader2, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Activity,
  History,
  Trash2,
  Volume2
} from 'lucide-react';
import apiClient, { CommandResponse, HistoryEntry, HealthResponse } from './services/apiClient';
import './App.css';

function App() {
  // State
  const [command, setCommand] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [lastResponse, setLastResponse] = useState<CommandResponse | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [activeTab, setActiveTab] = useState<'preview' | 'history'>('preview');
  
  // Voice state
  const [isListening, setIsListening] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize Voice Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setCommand(transcript);
        setIsListening(false);
        speak(`You said: ${transcript}`);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        setVoiceError(`Voice error: ${event.error}`);
        setTimeout(() => setVoiceError(null), 3000);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  // Check backend health on mount
  useEffect(() => {
    checkHealth();
    loadHistory();

    // Connect WebSocket
    apiClient.connectWebSocket((data) => {
      if (data.type === 'command_executed') {
        loadHistory();
      }
    });

    apiClient.on('connected', () => setIsConnected(true));
    apiClient.on('disconnected', () => setIsConnected(false));

    return () => {
      apiClient.disconnectWebSocket();
    };
  }, []);

  // Voice Functions
  const speak = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;
      window.speechSynthesis.speak(utterance);
    }
  };

  const toggleListening = () => {
    if (!recognitionRef.current) {
      setVoiceError('Voice recognition not supported in your browser');
      setTimeout(() => setVoiceError(null), 3000);
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setVoiceError(null);
      recognitionRef.current.start();
      setIsListening(true);
      speak('Listening...');
    }
  };

  const checkHealth = async () => {
    try {
      const healthData = await apiClient.checkHealth();
      setHealth(healthData);
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };

  const loadHistory = async () => {
    try {
      const historyData = await apiClient.getHistory(20);
      setHistory(historyData.history.reverse());
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const handlePreview = async () => {
    if (!command.trim()) return;

    setIsLoading(true);
    try {
      const response = await apiClient.previewCommand(command);
      setLastResponse(response);
      setActiveTab('preview');
      speak(`Command preview ready. Risk level: ${response.command?.risk_level || 'unknown'}`);
    } catch (error) {
      console.error('Preview failed:', error);
      speak('Preview failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!command.trim()) return;

    setIsLoading(true);
    try {
      const response = await apiClient.executeCommand(command, false);
      setLastResponse(response);
      setCommand('');
      await loadHistory();
      speak('Command executed successfully');
    } catch (error) {
      console.error('Execution failed:', error);
      speak('Execution failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!confirm('Clear all command history?')) return;

    try {
      await apiClient.clearHistory();
      setHistory([]);
      speak('History cleared');
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handlePreview();
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low': return 'text-green-400 bg-green-500/10 border-green-500/20';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
      case 'high': return 'text-red-400 bg-red-500/10 border-red-500/20';
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/20';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-950/20 to-black">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-xl bg-white/5 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg">
                <Volume2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">AI Windows Agent</h1>
                <p className="text-sm text-gray-400">Voice-controlled automation</p>
              </div>
            </div>

            {/* Status Indicators */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg glass-card">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
                <span className="text-sm text-gray-300">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              {health && (
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg glass-card">
                  {health.llm_available ? (
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-400" />
                  )}
                  <span className="text-sm text-gray-300">
                    {health.llm_available ? 'LLM Ready' : 'LLM Offline'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Command Input */}
          <div className="space-y-6">
            <div className="glass-card p-6">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Mic className="w-5 h-5 text-blue-400" />
                Voice Command
              </h2>

              <div className="space-y-4">
                {/* Text Input with Voice Button */}
                <div className="relative">
                  <textarea
                    value={command}
                    onChange={(e) => setCommand(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type or speak your command... e.g., 'Open Chrome'"
                    className="input-field h-32 resize-none pr-14"
                    disabled={isLoading}
                  />
                  <button
                    onClick={toggleListening}
                    disabled={isLoading}
                    className={`absolute right-3 top-3 p-2.5 rounded-lg transition-all shadow-lg ${
                      isListening 
                        ? 'bg-red-500 hover:bg-red-600 animate-pulse scale-110' 
                        : 'bg-blue-600 hover:bg-blue-700 hover:scale-105'
                    }`}
                    title={isListening ? 'Stop listening' : 'Start voice input'}
                  >
                    {isListening ? (
                      <MicOff className="w-5 h-5 text-white" />
                    ) : (
                      <Mic className="w-5 h-5 text-white" />
                    )}
                  </button>
                </div>

                {/* Voice Error Display */}
                {voiceError && (
                  <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 animate-pulse">
                    <AlertTriangle className="w-4 h-4 text-red-400" />
                    <span className="text-sm text-red-300">{voiceError}</span>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={handlePreview}
                    disabled={isLoading || !command.trim()}
                    className="btn-secondary flex items-center justify-center gap-2 flex-1"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Activity className="w-4 h-4" />
                        Preview
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleExecute}
                    disabled={isLoading || !command.trim()}
                    className="btn-primary flex items-center justify-center gap-2 flex-1"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Executing...
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        Execute
                      </>
                    )}
                  </button>
                </div>

                {/* Tip */}
                <div className="flex items-start gap-2 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                  <AlertTriangle className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-blue-300">
                    <strong>Tip:</strong> Click the microphone for voice input or Preview to see what will happen before executing.
                  </p>
                </div>
              </div>
            </div>

            {/* Examples */}
            <div className="glass-card p-6">
              <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wide">
                Example Commands
              </h3>
              <div className="space-y-2">
                {[
                  'Open Chrome',
                  'Create a file called notes.txt',
                  'Search for PDFs in Documents',
                  'Open Notepad and Calculator'
                ].map((example) => (
                  <button
                    key={example}
                    onClick={() => setCommand(example)}
                    className="w-full text-left px-4 py-2.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-sm text-gray-300 transition-all hover:border-blue-500/30 hover:translate-x-1"
                  >
                    💡 {example}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Preview & History */}
          <div className="space-y-6">
            {/* Tabs */}
            <div className="flex gap-2 glass-card p-2">
              <button
                onClick={() => setActiveTab('preview')}
                className={`flex-1 px-4 py-2.5 rounded-lg font-medium transition-all ${
                  activeTab === 'preview'
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                Command Preview
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`flex-1 px-4 py-2.5 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                  activeTab === 'history'
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <History className="w-4 h-4" />
                History ({history.length})
              </button>
            </div>

            {/* Preview Tab */}
            {activeTab === 'preview' && (
              <div className="glass-card p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Command Preview</h2>

                {lastResponse ? (
                  <div className="space-y-4">
                    {/* Status */}
                    <div className={`flex items-center gap-2 p-3 rounded-lg border ${
                      lastResponse.success
                        ? 'bg-green-500/10 border-green-500/20 text-green-400'
                        : 'bg-red-500/10 border-red-500/20 text-red-400'
                    }`}>
                      {lastResponse.success ? (
                        <CheckCircle className="w-5 h-5" />
                      ) : (
                        <XCircle className="w-5 h-5" />
                      )}
                      <span className="font-medium">
                        {lastResponse.success ? 'Success' : 'Failed'}
                      </span>
                    </div>

                    {lastResponse.command && (
                      <>
                        {/* Intent & Risk */}
                        <div>
                          <p className="text-sm text-gray-400 mb-2">Intent:</p>
                          <p className="text-white font-medium">{lastResponse.command.intent}</p>
                        </div>

                        <div>
                          <p className="text-sm text-gray-400 mb-2">Risk Level:</p>
                          <span className={`inline-flex px-3 py-1.5 rounded-full text-sm font-medium border ${
                            getRiskColor(lastResponse.command.risk_level)
                          }`}>
                            {lastResponse.command.risk_level.toUpperCase()}
                          </span>
                        </div>

                        {/* Explanation */}
                        <div>
                          <p className="text-sm text-gray-400 mb-2">Explanation:</p>
                          <p className="text-gray-300 leading-relaxed">{lastResponse.command.explanation}</p>
                        </div>

                        {/* Steps */}
                        <div>
                          <p className="text-sm text-gray-400 mb-3">Execution Steps:</p>
                          <div className="space-y-2">
                            {lastResponse.command.steps.map((step, idx) => (
                              <div key={idx} className="p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-sm font-medium">
                                    {idx + 1}
                                  </span>
                                  <span className="text-white font-medium uppercase text-xs tracking-wide">
                                    {step.action}
                                  </span>
                                </div>
                                <div className="pl-8 space-y-1">
                                  {Object.entries(step.parameters).map(([key, value]) => (
                                    <p key={key} className="text-sm text-gray-400">
                                      <span className="text-gray-500">{key}:</span>{' '}
                                      <span className="text-gray-300">{String(value)}</span>
                                    </p>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </>
                    )}

                    {lastResponse.error && (
                      <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
                        <p className="text-sm text-red-300">{lastResponse.error}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-16 text-gray-500">
                    <Activity className="w-16 h-16 mb-4 opacity-30" />
                    <p className="text-sm">No preview yet</p>
                    <p className="text-xs text-gray-600 mt-1">Enter a command and click Preview</p>
                  </div>
                )}
              </div>
            )}

            {/* History Tab */}
            {activeTab === 'history' && (
              <div className="glass-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-white">Command History</h2>
                  {history.length > 0 && (
                    <button
                      onClick={handleClearHistory}
                      className="text-sm text-red-400 hover:text-red-300 flex items-center gap-1 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                      Clear All
                    </button>
                  )}
                </div>

                {history.length > 0 ? (
                  <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
                    {history.map((entry, idx) => (
                      <div
                        key={idx}
                        className="p-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
                      >
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <p className="text-sm text-white font-medium flex-1">
                            {entry.command}
                          </p>
                          {entry.success ? (
                            <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                          ) : (
                            <XCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                          )}
                        </div>
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <span className="text-gray-400">{entry.intent}</span>
                          <span>•</span>
                          <span>{new Date(entry.timestamp).toLocaleTimeString()}</span>
                          {entry.dry_run && (
                            <>
                              <span>•</span>
                              <span className="text-yellow-400">Preview Only</span>
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-16 text-gray-500">
                    <History className="w-16 h-16 mb-4 opacity-30" />
                    <p className="text-sm">No commands executed yet</p>
                    <p className="text-xs text-gray-600 mt-1">Your command history will appear here</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
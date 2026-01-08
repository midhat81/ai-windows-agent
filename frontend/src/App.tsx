import { useState, useEffect } from 'react';
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
  Trash2
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

  // Check backend health on mount
  useEffect(() => {
    checkHealth();
    loadHistory();

    // Connect WebSocket
    apiClient.connectWebSocket((data) => {
      if (data.type === 'command_executed') {
        loadHistory(); // Refresh history when command executed
      }
    });

    apiClient.on('connected', () => setIsConnected(true));
    apiClient.on('disconnected', () => setIsConnected(false));

    // Cleanup
    return () => {
      apiClient.disconnectWebSocket();
    };
  }, []);

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
    } catch (error) {
      console.error('Preview failed:', error);
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
      setCommand(''); // Clear input after execution
      await loadHistory(); // Refresh history
    } catch (error) {
      console.error('Execution failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!confirm('Clear all command history?')) return;

    try {
      await apiClient.clearHistory();
      setHistory([]);
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
    switch (risk) {
      case 'low': return 'text-green-400 bg-green-500/10 border-green-500/20';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
      case 'high': return 'text-red-400 bg-red-500/10 border-red-500/20';
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/20';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-950 to-black">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-xl bg-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
                <Mic className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">AI Windows Agent</h1>
                <p className="text-sm text-gray-400">Voice-controlled automation</p>
              </div>
            </div>

            {/* Status Indicators */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg glass-card">
                <Activity className={`w-4 h-4 ${isConnected ? 'text-green-400 animate-pulse' : 'text-gray-400'}`} />
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
                <Send className="w-5 h-5 text-primary-400" />
                Voice Command
              </h2>

              <div className="space-y-4">
                <textarea
                  value={command}
                  onChange={(e) => setCommand(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your command... e.g., 'Open Chrome and search for Python tutorials'"
                  className="input-field h-32 resize-none"
                  disabled={isLoading}
                />

                <div className="flex gap-3">
                  <button
                    onClick={handlePreview}
                    disabled={isLoading || !command.trim()}
                    className="btn-secondary flex items-center gap-2 flex-1"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <AlertTriangle className="w-4 h-4" />
                        Preview
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleExecute}
                    disabled={isLoading || !command.trim()}
                    className="btn-primary flex items-center gap-2 flex-1"
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

                <div className="flex items-start gap-2 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                  <AlertTriangle className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-blue-300">
                    <strong>Tip:</strong> Preview your command first to see what will happen before executing it.
                  </p>
                </div>
              </div>
            </div>

            {/* Examples */}
            <div className="glass-card p-6">
              <h3 className="text-sm font-semibold text-gray-400 mb-3">Example Commands</h3>
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
                    className="w-full text-left px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-sm text-gray-300 transition-all"
                  >
                    {example}
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
                className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
                  activeTab === 'preview'
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Preview
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                  activeTab === 'history'
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-400 hover:text-white'
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
                          <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium border ${
                            getRiskColor(lastResponse.command.risk_level)
                          }`}>
                            {lastResponse.command.risk_level.toUpperCase()}
                          </span>
                        </div>

                        {/* Explanation */}
                        <div>
                          <p className="text-sm text-gray-400 mb-2">Explanation:</p>
                          <p className="text-gray-300">{lastResponse.command.explanation}</p>
                        </div>

                        {/* Steps */}
                        <div>
                          <p className="text-sm text-gray-400 mb-2">Steps:</p>
                          <div className="space-y-2">
                            {lastResponse.command.steps.map((step, idx) => (
                              <div key={idx} className="p-3 rounded-lg bg-white/5 border border-white/10">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="text-primary-400 font-mono text-sm">
                                    {idx + 1}.
                                  </span>
                                  <span className="text-white font-medium uppercase text-xs">
                                    {step.action}
                                  </span>
                                </div>
                                <div className="pl-6 space-y-1">
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
                      <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                        <p className="text-sm text-red-300">{lastResponse.error}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                    <AlertTriangle className="w-12 h-12 mb-3 opacity-50" />
                    <p className="text-sm">No preview yet. Enter a command and click Preview.</p>
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
                      className="text-sm text-red-400 hover:text-red-300 flex items-center gap-1"
                    >
                      <Trash2 className="w-4 h-4" />
                      Clear
                    </button>
                  )}
                </div>

                {history.length > 0 ? (
                  <div className="space-y-2 max-h-[600px] overflow-y-auto">
                    {history.map((entry, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
                      >
                        <div className="flex items-start justify-between gap-2 mb-1">
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
                          <span>{entry.intent}</span>
                          <span>•</span>
                          <span>{new Date(entry.timestamp).toLocaleTimeString()}</span>
                          {entry.dry_run && (
                            <>
                              <span>•</span>
                              <span className="text-yellow-400">Dry-run</span>
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                    <History className="w-12 h-12 mb-3 opacity-50" />
                    <p className="text-sm">No commands executed yet.</p>
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
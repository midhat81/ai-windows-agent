/**
 * API Client for AI Windows Agent Backend
 * Handles REST and WebSocket communication
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// ============================================
// Types
// ============================================

export interface CommandRequest {
  command: string;
  dry_run?: boolean;
}

export interface CommandStep {
  action: string;
  parameters: Record<string, any>;
}

export interface Command {
  intent: string;
  steps: CommandStep[];
  risk_level: 'low' | 'medium' | 'high';
  requires_confirmation: boolean;
  explanation: string;
}

export interface CommandResponse {
  success: boolean;
  command?: Command;
  result?: {
    success: boolean;
    message: string;
    details: any;
  };
  error?: string;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  llm_available: boolean;
  executor_ready: boolean;
  timestamp: string;
}

export interface HistoryEntry {
  timestamp: string;
  command: string;
  intent: string;
  success: boolean;
  dry_run: boolean;
}

export interface HistoryResponse {
  history: HistoryEntry[];
  total: number;
}

export interface CapabilitiesResponse {
  actions: string[];
  examples: string[];
}

// ============================================
// API Client Class
// ============================================

class APIClient {
  private client: AxiosInstance;
  private ws: WebSocket | null = null;
  private wsHandlers: Map<string, Function[]> = new Map();

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  // ============================================
  // REST API Methods
  // ============================================

  /**
   * Check backend health
   */
  async checkHealth(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  /**
   * Execute a voice command
   */
  async executeCommand(command: string, dryRun: boolean = false): Promise<CommandResponse> {
    const response = await this.client.post<CommandResponse>('/api/command', {
      command,
      dry_run: dryRun,
    });
    return response.data;
  }

  /**
   * Preview command in dry-run mode
   */
  async previewCommand(command: string): Promise<CommandResponse> {
    return this.executeCommand(command, true);
  }

  /**
   * Get command history
   */
  async getHistory(limit: number = 50): Promise<HistoryResponse> {
    const response = await this.client.get<HistoryResponse>('/api/history', {
      params: { limit },
    });
    return response.data;
  }

  /**
   * Clear command history
   */
  async clearHistory(): Promise<{ message: string; success: boolean }> {
    const response = await this.client.delete('/api/history');
    return response.data;
  }

  /**
   * Get available capabilities
   */
  async getCapabilities(): Promise<CapabilitiesResponse> {
    const response = await this.client.get<CapabilitiesResponse>('/api/capabilities');
    return response.data;
  }

  // ============================================
  // WebSocket Methods
  // ============================================

  /**
   * Connect to WebSocket for real-time updates
   */
  connectWebSocket(onMessage?: (data: any) => void): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws';
    console.log('Connecting to WebSocket:', wsUrl);

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected');
      this.emit('connected', { connected: true });
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📥 WebSocket message:', data);

        // Call registered handlers
        const handlers = this.wsHandlers.get(data.type) || [];
        handlers.forEach((handler) => handler(data));

        // Call generic message handler
        if (onMessage) {
          onMessage(data);
        }
      } catch (error) {
        console.error('WebSocket message parse error:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      this.emit('error', error);
    };

    this.ws.onclose = () => {
      console.log('❌ WebSocket disconnected');
      this.emit('disconnected', { connected: false });
      this.ws = null;
    };
  }

  /**
   * Send message via WebSocket
   */
  sendWebSocketMessage(type: string, data: any = {}): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }

    this.ws.send(JSON.stringify({ type, ...data }));
  }

  /**
   * Register handler for WebSocket message type
   */
  on(type: string, handler: Function): void {
    if (!this.wsHandlers.has(type)) {
      this.wsHandlers.set(type, []);
    }
    this.wsHandlers.get(type)!.push(handler);
  }

  /**
   * Emit event to registered handlers
   */
  private emit(type: string, data: any): void {
    const handlers = this.wsHandlers.get(type) || [];
    handlers.forEach((handler) => handler(data));
  }

  /**
   * Disconnect WebSocket
   */
  disconnectWebSocket(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Send ping via WebSocket
   */
  ping(): void {
    this.sendWebSocketMessage('ping');
  }
}

// Export singleton instance
export const apiClient = new APIClient();

export default apiClient;
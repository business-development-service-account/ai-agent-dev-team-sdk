import { WebSocketConfig, WebSocketMessage, AgentStatusUpdate, Task } from '@/types';

export class WebSocketManager {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private reconnectAttempts = 0;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private messageHandlers = new Map<string, (message: WebSocketMessage) => void>();
  private connectionState: 'disconnected' | 'connecting' | 'connected' | 'reconnecting' = 'disconnected';

  constructor(config: WebSocketConfig) {
    this.config = config;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.connectionState === 'connected' || this.connectionState === 'connecting') {
        resolve();
        return;
      }

      this.connectionState = 'connecting';

      try {
        this.ws = new WebSocket(this.config.url, this.config.protocols);

        this.ws.onopen = () => {
          this.connectionState = 'connected';
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          console.log('WebSocket connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          this.connectionState = 'disconnected';
          this.stopHeartbeat();
          console.log('WebSocket disconnected:', event.code, event.reason);

          if (!event.wasClean && this.reconnectAttempts < this.config.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.connectionState = 'disconnected';
          reject(error);
        };
      } catch (error) {
        this.connectionState = 'disconnected';
        reject(error);
      }
    });
  }

  private handleMessage(message: WebSocketMessage) {
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      handler(message);
    }

    // Handle system messages
    switch (message.type) {
      case 'heartbeat':
        this.handleHeartbeat(message);
        break;
      case 'status_update':
        this.handleStatusUpdate(message);
        break;
      case 'task_assignment':
      case 'task_result':
        // These are handled by registered handlers
        break;
      case 'error':
        console.error('WebSocket error message:', message.payload);
        break;
    }
  }

  private handleHeartbeat(message: WebSocketMessage) {
    // Respond to heartbeat with pong
    this.send({
      type: 'heartbeat',
      payload: { timestamp: Date.now() },
      messageId: `heartbeat-${Date.now()}`,
      timestamp: new Date().toISOString()
    });
  }

  private handleStatusUpdate(message: WebSocketMessage) {
    const statusUpdate = message.payload as AgentStatusUpdate;
    // Status updates are handled by registered handlers
    console.log('Agent status update:', statusUpdate);
  }

  private scheduleReconnect() {
    this.connectionState = 'reconnecting';
    const delay = this.config.reconnectInterval * Math.pow(2, this.reconnectAttempts);

    setTimeout(() => {
      this.reconnectAttempts++;
      this.connect().catch(error => {
        console.error('Reconnection failed:', error);
      });
    }, delay);
  }

  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({
          type: 'heartbeat',
          payload: { timestamp: Date.now() },
          messageId: `heartbeat-${Date.now()}`,
          timestamp: new Date().toISOString()
        });
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  send(message: WebSocketMessage): boolean {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
      return true;
    }
    return false;
  }

  onMessageType(type: string, handler: (message: WebSocketMessage) => void) {
    this.messageHandlers.set(type, handler);
  }

  offMessageType(type: string) {
    this.messageHandlers.delete(type);
  }

  disconnect() {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.connectionState = 'disconnected';
    this.messageHandlers.clear();
  }

  getConnectionState(): string {
    return this.connectionState;
  }

  isConnected(): boolean {
    return this.connectionState === 'connected' && this.ws?.readyState === WebSocket.OPEN;
  }
}

// WebSocket configuration
export const wsConfig: WebSocketConfig = {
  url: import.meta.env.VITE_WS_URL || 'ws://localhost:8080',
  protocols: ['agent-protocol-v1'],
  reconnectInterval: 5000,
  maxReconnectAttempts: 10,
  heartbeatInterval: 30000
};

// Global WebSocket manager instance
export const wsManager = new WebSocketManager(wsConfig);
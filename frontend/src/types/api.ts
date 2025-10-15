export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface AuthConfig {
  clientId: string;
  redirectUri: string;
  scopes: string[];
  authority: string;
  responseType: 'code';
  grantType: 'authorization_code';
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
  scope: string;
}

export interface TokenManager {
  getAccessToken(): Promise<string>;
  refreshToken(): Promise<string>;
  isTokenExpired(token: string): boolean;
  clearTokens(): void;
  storeTokens(tokens: TokenResponse): void;
}

export interface ApiError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
  requestId?: string;
}

export interface SystemConfig {
  agents: {
    maxConcurrent: number;
    timeoutMs: number;
    retryAttempts: number;
  };
  tasks: {
    maxQueueSize: number;
    defaultTimeoutMs: number;
    cleanupIntervalMs: number;
  };
  monitoring: {
    metricsIntervalMs: number;
    retentionDays: number;
  };
}

export interface SystemPrompt {
  id: string;
  name: string;
  type: 'system' | 'agent' | 'task';
  content: string;
  version: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, any>;
}

export interface MCPServer {
  id: string;
  name: string;
  type: string;
  status: 'online' | 'offline' | 'error';
  endpoint: string;
  capabilities: string[];
  lastHeartbeat: string;
  config: Record<string, any>;
  metrics: {
    requestsHandled: number;
    averageResponseTime: number;
    errorRate: number;
  };
}

export interface TaskFilters {
  status?: Task['status'][];
  type?: string[];
  priority?: Task['priority'][];
  assignedAgentId?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
  tags?: string[];
  search?: string;
}

export interface AgentFilters {
  type?: Agent['type'][];
  status?: Agent['status'][];
  capabilities?: string[];
  search?: string;
}

export interface MessageFilters {
  fromAgentId?: string[];
  toAgentId?: string[];
  type?: AgentMessage['type'][];
  dateRange?: {
    start: string;
    end: string;
  };
  threadId?: string;
}
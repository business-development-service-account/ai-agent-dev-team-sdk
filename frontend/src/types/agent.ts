export interface Agent {
  id: string;
  type: 'research' | 'codebase' | 'frontend' | 'backend' | 'devops' | 'security' | 'qa' | 'documentation';
  status: 'idle' | 'busy' | 'success' | 'error' | 'offline';
  name: string;
  description: string;
  capabilities: string[];
  currentTask?: Task;
  lastActivity: string;
  metrics: AgentMetrics;
}

export interface AgentMetrics {
  tasksCompleted: number;
  tasksFailed: number;
  averageExecutionTime: number;
  successRate: number;
  totalExecutionTime: number;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  type: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignedAgentId?: string;
  assignedAgent?: Agent;
  createdAt: string;
  updatedAt: string;
  startedAt?: string;
  completedAt?: string;
  estimatedDuration?: number;
  actualDuration?: number;
  progress: number;
  result?: TaskResult;
  dependencies: string[];
  tags: string[];
}

export interface TaskResult {
  success: boolean;
  data?: any;
  error?: string;
  output?: string;
  artifacts?: Artifact[];
  executionTime: number;
  completedAt: string;
}

export interface Artifact {
  id: string;
  name: string;
  type: 'file' | 'directory' | 'url' | 'data';
  path?: string;
  url?: string;
  data?: any;
  size?: number;
  checksum?: string;
  createdAt: string;
}

export interface AgentMessage {
  id: string;
  fromAgentId: string;
  toAgentId?: string;
  type: 'task_assignment' | 'task_result' | 'status_update' | 'error' | 'heartbeat' | 'coordination';
  payload: any;
  timestamp: string;
  correlationId?: string;
  threadId?: string;
}

export interface AgentStatusUpdate {
  agentId: string;
  status: Agent['status'];
  currentTask?: Task;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface WebSocketConfig {
  url: string;
  protocols: string[];
  reconnectInterval: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
}

export interface WebSocketMessage {
  type: 'task_assignment' | 'task_result' | 'status_update' | 'error' | 'heartbeat';
  payload: any;
  timestamp: string;
  messageId: string;
  agentId?: string;
  correlationId?: string;
}
import { ReactNode } from 'react';

export interface AgentStatusProps {
  status: 'idle' | 'busy' | 'success' | 'error' | 'offline';
  agentType: 'research' | 'codebase' | 'frontend' | 'backend' | 'devops' | 'security' | 'qa' | 'documentation';
  lastActivity: string;
  showLabel?: boolean;
  size?: 'small' | 'medium' | 'large';
}

export interface TaskProgressProps {
  taskId: string;
  progress: number;
  currentStep: string;
  estimatedTimeRemaining?: number;
  showPercentage?: boolean;
  showETA?: boolean;
}

export interface CommunicationLogProps {
  messages: import('./agent').AgentMessage[];
  filters: import('./api').MessageFilters;
  realtimeUpdates: boolean;
  onFiltersChange: (filters: import('./api').MessageFilters) => void;
  maxHeight?: number;
}

export interface PromptEditorProps {
  promptId: string;
  initialContent: string;
  onSave: (content: string) => void;
  previewMode: boolean;
  readOnly?: boolean;
  height?: number;
}

export interface DashboardCardProps {
  title: string;
  children: ReactNode;
  loading?: boolean;
  error?: string;
  actions?: ReactNode;
  className?: string;
  extra?: ReactNode;
}

export interface AgentMetricsCardProps {
  agent: import('./agent').Agent;
  showDetails?: boolean;
  compact?: boolean;
}

export interface TaskListProps {
  tasks: import('./agent').Task[];
  filters: import('./api').TaskFilters;
  onFiltersChange: (filters: import('./api').TaskFilters) => void;
  onTaskSelect: (task: import('./agent').Task) => void;
  loading?: boolean;
  selectable?: boolean;
  showAgent?: boolean;
}

export interface SystemStatusProps {
  agents: import('./agent').Agent[];
  tasks: import('./agent').Task[];
  servers: import('./api').MCPServer[];
  refreshRate?: number;
  autoRefresh?: boolean;
}

export interface NotificationItem {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actions?: {
    label: string;
    action: () => void;
  }[];
}

export interface LayoutProps {
  children: ReactNode;
  sidebar?: boolean;
  header?: boolean;
  footer?: boolean;
  className?: string;
}

export interface NavigationItem {
  key: string;
  label: string;
  icon?: ReactNode;
  path: string;
  children?: NavigationItem[];
  badge?: {
    count: number;
    color: 'default' | 'red' | 'orange' | 'green' | 'blue';
  };
}

export interface ThemeConfig {
  mode: 'light' | 'dark' | 'auto';
  primaryColor: string;
  compactMode: boolean;
}

export interface UserPreferences {
  theme: ThemeConfig;
  notifications: {
    enabled: boolean;
    types: string[];
    sound: boolean;
  };
  dashboard: {
    refreshRate: number;
    autoRefresh: boolean;
    layout: 'grid' | 'list';
  };
}
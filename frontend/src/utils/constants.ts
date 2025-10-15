export const AGENT_TYPES = {
  RESEARCH: 'research',
  CODEBASE: 'codebase',
  FRONTEND: 'frontend',
  BACKEND: 'backend',
  DEVOPS: 'devops',
  SECURITY: 'security',
  QA: 'qa',
  DOCUMENTATION: 'documentation'
} as const;

export const AGENT_STATUS = {
  IDLE: 'idle',
  BUSY: 'busy',
  SUCCESS: 'success',
  ERROR: 'error',
  OFFLINE: 'offline'
} as const;

export const TASK_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled'
} as const;

export const TASK_PRIORITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
} as const;

export const MESSAGE_TYPES = {
  TASK_ASSIGNMENT: 'task_assignment',
  TASK_RESULT: 'task_result',
  STATUS_UPDATE: 'status_update',
  ERROR: 'error',
  HEARTBEAT: 'heartbeat',
  COORDINATION: 'coordination'
} as const;

export const REFRESH_INTERVALS = {
  FAST: 5000,      // 5 seconds
  NORMAL: 15000,   // 15 seconds
  SLOW: 60000,     // 1 minute
  VERY_SLOW: 300000 // 5 minutes
} as const;

export const CHART_COLORS = {
  PRIMARY: '#3b82f6',
  SUCCESS: '#10b981',
  WARNING: '#f59e0b',
  ERROR: '#ef4444',
  INFO: '#6366f1',
  GRAY: '#6b7280'
} as const;

export const DEFAULT_PAGINATION = {
  PAGE: 1,
  PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100
} as const;

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_PREFERENCES: 'user_preferences',
  LAST_DASHBOARD_VIEW: 'last_dashboard_view',
  TASK_FILTERS: 'task_filters',
  AGENT_FILTERS: 'agent_filters'
} as const;

export const LOCAL_STORAGE_KEYS = {
  THEME: 'theme',
  SIDEBAR_COLLAPSED: 'sidebar_collapsed',
  NOTIFICATIONS_ENABLED: 'notifications_enabled',
  AUTO_REFRESH: 'auto_refresh',
  REFRESH_RATE: 'refresh_rate'
} as const;
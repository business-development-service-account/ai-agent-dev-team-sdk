import { rest } from 'msw';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const handlers = [
  // Mock agent endpoints
  rest.get(`${API_BASE}/agents`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        data: [
          {
            id: 'agent-1',
            type: 'research',
            status: 'idle',
            name: 'Research Agent 1',
            description: 'Research agent for market analysis',
            capabilities: ['research', 'analysis'],
            lastActivity: new Date().toISOString(),
            metrics: {
              tasksCompleted: 10,
              tasksFailed: 2,
              averageExecutionTime: 120,
              successRate: 83.3,
              totalExecutionTime: 1200
            }
          },
          {
            id: 'agent-2',
            type: 'frontend',
            status: 'busy',
            name: 'Frontend Agent 1',
            description: 'Frontend development agent',
            capabilities: ['react', 'typescript', 'ui'],
            currentTask: {
              id: 'task-1',
              title: 'Build dashboard UI',
              status: 'in_progress'
            },
            lastActivity: new Date().toISOString(),
            metrics: {
              tasksCompleted: 15,
              tasksFailed: 1,
              averageExecutionTime: 300,
              successRate: 93.8,
              totalExecutionTime: 4500
            }
          }
        ]
      })
    );
  }),

  // Mock task endpoints
  rest.get(`${API_BASE}/tasks`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        data: [
          {
            id: 'task-1',
            title: 'Build dashboard UI',
            description: 'Create the main dashboard interface',
            type: 'development',
            status: 'in_progress',
            priority: 'high',
            assignedAgentId: 'agent-2',
            assignedAgent: {
              id: 'agent-2',
              name: 'Frontend Agent 1'
            },
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            progress: 75
          },
          {
            id: 'task-2',
            title: 'Research market trends',
            description: 'Analyze current market trends',
            type: 'research',
            status: 'completed',
            priority: 'medium',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            progress: 100
          }
        ],
        pagination: {
          page: 1,
          pageSize: 20,
          total: 2,
          totalPages: 1,
          hasNext: false,
          hasPrev: false
        }
      })
    );
  }),

  // Mock system status endpoint
  rest.get(`${API_BASE}/system/status`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        data: {
          uptime: 86400,
          version: '1.0.0',
          status: 'healthy'
        }
      })
    );
  }),

  // Mock system prompts endpoint
  rest.get(`${API_BASE}/system/prompts`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        data: [
          {
            id: 'prompt-1',
            name: 'System Initialization',
            type: 'system',
            content: 'Initialize the system...',
            version: '1.0.0',
            isActive: true,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          }
        ]
      })
    );
  }),

  // Mock MCP servers endpoint
  rest.get(`${API_BASE}/system/mcp-servers`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        data: [
          {
            id: 'server-1',
            name: 'Development Server',
            type: 'development',
            status: 'online',
            endpoint: 'http://localhost:3000',
            capabilities: ['development', 'testing'],
            lastHeartbeat: new Date().toISOString(),
            metrics: {
              requestsHandled: 100,
              averageResponseTime: 150,
              errorRate: 0.02
            }
          }
        ]
      })
    );
  })
];
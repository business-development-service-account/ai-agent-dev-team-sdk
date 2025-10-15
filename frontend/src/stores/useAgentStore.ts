import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { Agent, AgentStatusUpdate, AgentFilters } from '@/types';
import { agentService } from '@/services';
import { wsManager } from '@/utils/websocket';

interface AgentStore {
  // State
  agents: Agent[];
  selectedAgent: Agent | null;
  filters: AgentFilters;
  loading: boolean;
  error: string | null;
  realtimeUpdates: boolean;
  lastUpdated: string | null;

  // Actions
  fetchAgents: () => Promise<void>;
  setSelectedAgent: (agent: Agent | null) => void;
  updateAgent: (agentId: string, updates: Partial<Agent>) => void;
  updateAgentStatus: (agentId: string, status: Agent['status']) => void;
  setFilters: (filters: Partial<AgentFilters>) => void;
  clearFilters: () => void;
  toggleRealtimeUpdates: () => void;
  refreshAgents: () => Promise<void>;
  executeTask: (agentId: string, taskSpec: any) => Promise<void>;
  stopAgent: (agentId: string) => Promise<void>;
  restartAgent: (agentId: string) => Promise<void>;

  // Internal actions
  _setLoading: (loading: boolean) => void;
  _setError: (error: string | null) => void;
  _setAgents: (agents: Agent[]) => void;
  _updateAgentFromWebSocket: (update: AgentStatusUpdate) => void;
}

export const useAgentStore = create<AgentStore>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // Initial state
      agents: [],
      selectedAgent: null,
      filters: {},
      loading: false,
      error: null,
      realtimeUpdates: true,
      lastUpdated: null,

      // Actions
      fetchAgents: async () => {
        const { _setLoading, _setError, _setAgents, filters } = get();

        try {
          _setLoading(true);
          _setError(null);

          const agents = await agentService.getAgents(filters);
          _setAgents(agents);
        } catch (error) {
          _setError(error instanceof Error ? error.message : 'Failed to fetch agents');
        } finally {
          _setLoading(false);
        }
      },

      setSelectedAgent: (agent) => {
        set({ selectedAgent: agent });
      },

      updateAgent: (agentId, updates) => {
        set((state) => ({
          agents: state.agents.map((agent) =>
            agent.id === agentId ? { ...agent, ...updates } : agent
          ),
          selectedAgent:
            state.selectedAgent?.id === agentId
              ? { ...state.selectedAgent, ...updates }
              : state.selectedAgent,
          lastUpdated: new Date().toISOString()
        }));
      },

      updateAgentStatus: (agentId, status) => {
        get().updateAgent(agentId, {
          status,
          lastActivity: new Date().toISOString()
        });
      },

      setFilters: (newFilters) => {
        set((state) => ({
          filters: { ...state.filters, ...newFilters }
        }));
      },

      clearFilters: () => {
        set({ filters: {} });
      },

      toggleRealtimeUpdates: () => {
        const { realtimeUpdates } = get();
        set({ realtimeUpdates: !realtimeUpdates });

        if (!realtimeUpdates) {
          // Enable WebSocket updates
          wsManager.onMessageType('status_update', (message) => {
            get()._updateAgentFromWebSocket(message.payload as AgentStatusUpdate);
          });
        } else {
          // Disable WebSocket updates
          wsManager.offMessageType('status_update');
        }
      },

      refreshAgents: async () => {
        await get().fetchAgents();
      },

      executeTask: async (agentId, taskSpec) => {
        try {
          await agentService.executeTask(agentId, taskSpec);
          // Agent status will be updated via WebSocket
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to execute task'
          });
        }
      },

      stopAgent: async (agentId) => {
        try {
          await agentService.stopAgent(agentId);
          get().updateAgentStatus(agentId, 'offline');
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to stop agent'
          });
        }
      },

      restartAgent: async (agentId) => {
        try {
          await agentService.restartAgent(agentId);
          get().updateAgentStatus(agentId, 'idle');
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to restart agent'
          });
        }
      },

      // Internal actions
      _setLoading: (loading) => {
        set({ loading });
      },

      _setError: (error) => {
        set({ error });
      },

      _setAgents: (agents) => {
        set({
          agents,
          lastUpdated: new Date().toISOString()
        });
      },

      _updateAgentFromWebSocket: (update) => {
        const { agents } = get();
        const existingAgent = agents.find(a => a.id === update.agentId);

        if (existingAgent) {
          get().updateAgent(update.agentId, {
            status: update.status,
            lastActivity: update.timestamp,
            currentTask: update.currentTask
          });
        }
      }
    })),
    {
      name: 'agent-store'
    }
  )
);

// Initialize WebSocket listeners when store is created
useAgentStore.subscribe((state) => {
  if (state.realtimeUpdates && !wsManager.isConnected()) {
    wsManager.connect().catch(console.error);
  }
});
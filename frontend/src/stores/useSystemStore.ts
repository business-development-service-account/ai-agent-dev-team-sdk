import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { SystemConfig, SystemPrompt, MCPServer } from '@/types';
import { systemService } from '@/services';

interface SystemStore {
  // State
  config: SystemConfig | null;
  systemPrompts: SystemPrompt[];
  mcpServers: MCPServer[];
  systemStatus: any;
  systemMetrics: any;
  systemLogs: any[];
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;

  // Config actions
  fetchConfig: () => Promise<void>;
  updateConfig: (config: Partial<SystemConfig>) => Promise<void>;

  // System prompt actions
  fetchSystemPrompts: () => Promise<void>;
  createSystemPrompt: (prompt: Partial<SystemPrompt>) => Promise<void>;
  updateSystemPrompt: (id: string, prompt: Partial<SystemPrompt>) => Promise<void>;
  deleteSystemPrompt: (id: string) => Promise<void>;
  loadExternalPrompts: (directory: string) => Promise<void>;

  // MCP server actions
  fetchMCPServers: () => Promise<void>;
  addMCPServer: (server: Partial<MCPServer>) => Promise<void>;
  updateMCPServer: (id: string, server: Partial<MCPServer>) => Promise<void>;
  deleteMCPServer: (id: string) => Promise<void>;
  testMCPServerConnection: (id: string) => Promise<void>;
  restartMCPServer: (id: string) => Promise<void>;

  // System status actions
  fetchSystemStatus: () => Promise<void>;
  fetchSystemMetrics: () => Promise<void>;
  fetchSystemLogs: (limit?: number, level?: string) => Promise<void>;

  // System actions
  shutdownSystem: () => Promise<void>;
  restartSystem: () => Promise<void>;
  exportConfiguration: () => Promise<Blob>;
  importConfiguration: (file: File) => Promise<void>;

  // Internal actions
  _setLoading: (loading: boolean) => void;
  _setError: (error: string | null) => void;
  _setConfig: (config: SystemConfig) => void;
  _setSystemPrompts: (prompts: SystemPrompt[]) => void;
  _setMCPServers: (servers: MCPServer[]) => void;
  _setSystemStatus: (status: any) => void;
  _setSystemMetrics: (metrics: any) => void;
  _setSystemLogs: (logs: any[]) => void;
}

export const useSystemStore = create<SystemStore>()(
  devtools((set, get) => ({
    // Initial state
    config: null,
    systemPrompts: [],
    mcpServers: [],
    systemStatus: null,
    systemMetrics: null,
    systemLogs: [],
    loading: false,
    error: null,
    lastUpdated: null,

    // Config actions
    fetchConfig: async () => {
      const { _setLoading, _setError, _setConfig } = get();

      try {
        _setLoading(true);
        _setError(null);

        const config = await systemService.getConfig();
        _setConfig(config);
      } catch (error) {
        _setError(error instanceof Error ? error.message : 'Failed to fetch system config');
      } finally {
        _setLoading(false);
      }
    },

    updateConfig: async (updates) => {
      const { _setLoading, _setError, _setConfig } = get();

      try {
        _setLoading(true);
        _setError(null);

        const config = await systemService.updateConfig(updates);
        _setConfig(config);
      } catch (error) {
        _setError(error instanceof Error ? error.message : 'Failed to update system config');
      } finally {
        _setLoading(false);
      }
    },

    // System prompt actions
    fetchSystemPrompts: async () => {
      const { _setLoading, _setError, _setSystemPrompts } = get();

      try {
        _setLoading(true);
        _setError(null);

        const prompts = await systemService.getSystemPrompts();
        _setSystemPrompts(prompts);
      } catch (error) {
        _setError(error instanceof Error ? error.message : 'Failed to fetch system prompts');
      } finally {
        _setLoading(false);
      }
    },

    createSystemPrompt: async (prompt) => {
      try {
        const newPrompt = await systemService.createSystemPrompt(prompt);
        set((state) => ({
          systemPrompts: [...state.systemPrompts, newPrompt],
          lastUpdated: new Date().toISOString()
        }));
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to create system prompt'
        });
      }
    },

    updateSystemPrompt: async (id, prompt) => {
      try {
        const updatedPrompt = await systemService.updateSystemPrompt(id, prompt);
        set((state) => ({
          systemPrompts: state.systemPrompts.map((p) =>
            p.id === id ? updatedPrompt : p
          ),
          lastUpdated: new Date().toISOString()
        }));
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to update system prompt'
        });
      }
    },

    deleteSystemPrompt: async (id) => {
      try {
        await systemService.deleteSystemPrompt(id);
        set((state) => ({
          systemPrompts: state.systemPrompts.filter((p) => p.id !== id),
          lastUpdated: new Date().toISOString()
        }));
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to delete system prompt'
        });
      }
    },

    loadExternalPrompts: async (directory) => {
      const { _setLoading, _setError } = get();

      try {
        _setLoading(true);
        _setError(null);

        const prompts = await systemService.loadExternalSystemPrompts(directory);
        set((state) => ({
          systemPrompts: [...state.systemPrompts, ...prompts],
          lastUpdated: new Date().toISOString()
        }));
      } catch (error) {
        _setError(error instanceof Error ? error.message : 'Failed to load external prompts');
      } finally {
        _setLoading(false);
      }
    },

    // MCP server actions
    fetchMCPServers: async () => {
      const { _setLoading, _setError, _setMCPServers } = get();

      try {
        _setLoading(true);
        _setError(null);

        const servers = await systemService.getMCPServers();
        _setMCPServers(servers);
      } catch (error) {
        _setError(error instanceof Error ? error.message : 'Failed to fetch MCP servers');
      } finally {
        _setLoading(false);
      }
    },

    addMCPServer: async (server) => {
      try {
        const newServer = await systemService.addMCPServer(server);
        set((state) => ({
          mcpServers: [...state.mcpServers, newServer],
          lastUpdated: new Date().toISOString()
        }));
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to add MCP server'
        });
      }
    },

    updateMCPServer: async (id, server) => {
      try {
        const updatedServer = await systemService.updateMCPServer(id, server);
        set((state) => ({
          mcpServers: state.mcpServers.map((s) =>
            s.id === id ? updatedServer : s
          ),
          lastUpdated: new Date().toISOString()
        }));
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to update MCP server'
        });
      }
    },

    deleteMCPServer: async (id) => {
      try {
        await systemService.deleteMCPServer(id);
        set((state) => ({
          mcpServers: state.mcpServers.filter((s) => s.id !== id),
          lastUpdated: new Date().toISOString()
        }));
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to delete MCP server'
        });
      }
    },

    testMCPServerConnection: async (id) => {
      try {
        const result = await systemService.testMCPServerConnection(id);
        set((state) => ({
          mcpServers: state.mcpServers.map((s) =>
            s.id === id ? { ...s, status: result.success ? 'online' : 'error' } : s
          ),
          lastUpdated: new Date().toISOString()
        }));
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to test MCP server connection'
        });
      }
    },

    restartMCPServer: async (id) => {
      try {
        await systemService.restartMCPServer(id);
        set((state) => ({
          mcpServers: state.mcpServers.map((s) =>
            s.id === id ? { ...s, status: 'online', lastHeartbeat: new Date().toISOString() } : s
          ),
          lastUpdated: new Date().toISOString()
        }));
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to restart MCP server'
        });
      }
    },

    // System status actions
    fetchSystemStatus: async () => {
      try {
        const status = await systemService.getStatus();
        set({ systemStatus: status, lastUpdated: new Date().toISOString() });
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to fetch system status'
        });
      }
    },

    fetchSystemMetrics: async () => {
      try {
        const metrics = await systemService.getMetrics();
        set({ systemMetrics: metrics, lastUpdated: new Date().toISOString() });
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to fetch system metrics'
        });
      }
    },

    fetchSystemLogs: async (limit = 100, level) => {
      try {
        const logs = await systemService.getSystemLogs(limit, level);
        set({ systemLogs: logs, lastUpdated: new Date().toISOString() });
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to fetch system logs'
        });
      }
    },

    // System actions
    shutdownSystem: async () => {
      try {
        await systemService.shutdownSystem();
        set({ systemStatus: null });
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to shutdown system'
        });
      }
    },

    restartSystem: async () => {
      try {
        await systemService.restartSystem();
        set({ systemStatus: null });
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to restart system'
        });
      }
    },

    exportConfiguration: async () => {
      try {
        return await systemService.exportConfiguration();
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to export configuration'
        });
        throw error;
      }
    },

    importConfiguration: async (file) => {
      const { _setLoading, _setError } = get();

      try {
        _setLoading(true);
        _setError(null);

        await systemService.importConfiguration(file);

        // Refresh all data after import
        await get().fetchConfig();
        await get().fetchSystemPrompts();
        await get().fetchMCPServers();
      } catch (error) {
        _setError(error instanceof Error ? error.message : 'Failed to import configuration');
      } finally {
        _setLoading(false);
      }
    },

    // Internal actions
    _setLoading: (loading) => {
      set({ loading });
    },

    _setError: (error) => {
      set({ error });
    },

    _setConfig: (config) => {
      set({ config, lastUpdated: new Date().toISOString() });
    },

    _setSystemPrompts: (prompts) => {
      set({ systemPrompts: prompts, lastUpdated: new Date().toISOString() });
    },

    _setMCPServers: (servers) => {
      set({ mcpServers: servers, lastUpdated: new Date().toISOString() });
    },

    _setSystemStatus: (status) => {
      set({ systemStatus: status, lastUpdated: new Date().toISOString() });
    },

    _setSystemMetrics: (metrics) => {
      set({ systemMetrics: metrics, lastUpdated: new Date().toISOString() });
    },

    _setSystemLogs: (logs) => {
      set({ systemLogs: logs, lastUpdated: new Date().toISOString() });
    }
  })),
  {
    name: 'system-store'
  }
));
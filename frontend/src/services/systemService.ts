import { apiClient } from '@/utils/apiClient';
import { SystemConfig, SystemPrompt, MCPServer, ApiResponse } from '@/types';

export class SystemService {
  async getConfig(): Promise<SystemConfig> {
    const response = await apiClient.get<SystemConfig>('/system/config');
    return response.data;
  }

  async updateConfig(config: Partial<SystemConfig>): Promise<SystemConfig> {
    const response = await apiClient.put<SystemConfig>('/system/config', config);
    return response.data;
  }

  async getStatus(): Promise<any> {
    const response = await apiClient.get<any>('/system/status');
    return response.data;
  }

  async getHealth(): Promise<any> {
    const response = await apiClient.get<any>('/system/health');
    return response.data;
  }

  async getMetrics(): Promise<any> {
    const response = await apiClient.get<any>('/system/metrics');
    return response.data;
  }

  async getSystemPrompts(): Promise<SystemPrompt[]> {
    const response = await apiClient.get<SystemPrompt[]>('/system/prompts');
    return response.data || [];
  }

  async getSystemPrompt(id: string): Promise<SystemPrompt | null> {
    const response = await apiClient.get<SystemPrompt>(`/system/prompts/${id}`);
    return response.data;
  }

  async createSystemPrompt(prompt: Partial<SystemPrompt>): Promise<SystemPrompt> {
    const response = await apiClient.post<SystemPrompt>('/system/prompts', prompt);
    return response.data;
  }

  async updateSystemPrompt(id: string, prompt: Partial<SystemPrompt>): Promise<SystemPrompt> {
    const response = await apiClient.patch<SystemPrompt>(`/system/prompts/${id}`, prompt);
    return response.data;
  }

  async deleteSystemPrompt(id: string): Promise<void> {
    await apiClient.delete(`/system/prompts/${id}`);
  }

  async loadExternalSystemPrompts(directory: string): Promise<SystemPrompt[]> {
    const response = await apiClient.post<SystemPrompt[]>('/system/prompts/load', { directory });
    return response.data || [];
  }

  async validateSystemPrompt(content: string): Promise<any> {
    const response = await apiClient.post<any>('/system/prompts/validate', { content });
    return response.data;
  }

  async getMCPServers(): Promise<MCPServer[]> {
    const response = await apiClient.get<MCPServer[]>('/system/mcp-servers');
    return response.data || [];
  }

  async getMCPServer(id: string): Promise<MCPServer | null> {
    const response = await apiClient.get<MCPServer>(`/system/mcp-servers/${id}`);
    return response.data;
  }

  async addMCPServer(server: Partial<MCPServer>): Promise<MCPServer> {
    const response = await apiClient.post<MCPServer>('/system/mcp-servers', server);
    return response.data;
  }

  async updateMCPServer(id: string, server: Partial<MCPServer>): Promise<MCPServer> {
    const response = await apiClient.patch<MCPServer>(`/system/mcp-servers/${id}`, server);
    return response.data;
  }

  async deleteMCPServer(id: string): Promise<void> {
    await apiClient.delete(`/system/mcp-servers/${id}`);
  }

  async testMCPServerConnection(id: string): Promise<any> {
    const response = await apiClient.post<any>(`/system/mcp-servers/${id}/test`);
    return response.data;
  }

  async restartMCPServer(id: string): Promise<void> {
    await apiClient.post(`/system/mcp-servers/${id}/restart`);
  }

  async getSystemLogs(limit: number = 100, level?: string): Promise<any[]> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (level) {
      params.append('level', level);
    }

    const response = await apiClient.get<any[]>(`/system/logs?${params.toString()}`);
    return response.data || [];
  }

  async exportConfiguration(): Promise<Blob> {
    const response = await fetch('/api/system/config/export');
    if (!response.ok) {
      throw new Error('Failed to export configuration');
    }
    return response.blob();
  }

  async importConfiguration(file: File): Promise<void> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/api/system/config/import', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error('Failed to import configuration');
    }
  }

  async shutdownSystem(): Promise<void> {
    await apiClient.post('/system/shutdown');
  }

  async restartSystem(): Promise<void> {
    await apiClient.post('/system/restart');
  }
}

export const systemService = new SystemService();
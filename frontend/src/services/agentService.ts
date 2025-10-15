import { apiClient } from '@/utils/apiClient';
import { Agent, AgentFilters, PaginatedResponse, ApiResponse } from '@/types';

export class AgentService {
  async getAgents(filters?: AgentFilters): Promise<Agent[]> {
    const params = new URLSearchParams();

    if (filters?.type?.length) {
      params.append('type', filters.type.join(','));
    }
    if (filters?.status?.length) {
      params.append('status', filters.status.join(','));
    }
    if (filters?.capabilities?.length) {
      params.append('capabilities', filters.capabilities.join(','));
    }
    if (filters?.search) {
      params.append('search', filters.search);
    }

    const response = await apiClient.get<Agent[]>(`/agents?${params.toString()}`);
    return response.data || [];
  }

  async getAgent(id: string): Promise<Agent | null> {
    const response = await apiClient.get<Agent>(`/agents/${id}`);
    return response.data;
  }

  async updateAgentStatus(agentId: string, status: Agent['status']): Promise<Agent> {
    const response = await apiClient.patch<Agent>(`/agents/${agentId}/status`, { status });
    return response.data;
  }

  async getAgentMetrics(agentId: string): Promise<Agent['metrics']> {
    const response = await apiClient.get<Agent['metrics']>(`/agents/${agentId}/metrics`);
    return response.data;
  }

  async executeTask(agentId: string, taskSpec: any): Promise<any> {
    const response = await apiClient.post(`/agents/${agentId}/execute`, taskSpec);
    return response.data;
  }

  async stopAgent(agentId: string): Promise<void> {
    await apiClient.post(`/agents/${agentId}/stop`);
  }

  async restartAgent(agentId: string): Promise<void> {
    await apiClient.post(`/agents/${agentId}/restart`);
  }

  async getAgentConfig(agentId: string): Promise<any> {
    const response = await apiClient.get<any>(`/agents/${agentId}/config`);
    return response.data;
  }

  async updateAgentConfig(agentId: string, config: any): Promise<any> {
    const response = await apiClient.put(`/agents/${agentId}/config`, config);
    return response.data;
  }

  async getAgentLogs(agentId: string, limit: number = 100): Promise<any[]> {
    const response = await apiClient.get<any[]>(`/agents/${agentId}/logs?limit=${limit}`);
    return response.data || [];
  }
}

export const agentService = new AgentService();
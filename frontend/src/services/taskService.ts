import { apiClient } from '@/utils/apiClient';
import { Task, TaskFilters, TaskResult, PaginatedResponse, ApiResponse } from '@/types';

export class TaskService {
  async getTasks(filters?: TaskFilters, page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<Task>> {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());

    if (filters?.status?.length) {
      params.append('status', filters.status.join(','));
    }
    if (filters?.type?.length) {
      params.append('type', filters.type.join(','));
    }
    if (filters?.priority?.length) {
      params.append('priority', filters.priority.join(','));
    }
    if (filters?.assignedAgentId?.length) {
      params.append('assigned_agent_id', filters.assignedAgentId.join(','));
    }
    if (filters?.dateRange) {
      params.append('start_date', filters.dateRange.start);
      params.append('end_date', filters.dateRange.end);
    }
    if (filters?.tags?.length) {
      params.append('tags', filters.tags.join(','));
    }
    if (filters?.search) {
      params.append('search', filters.search);
    }

    const response = await apiClient.get<PaginatedResponse<Task>>(`/tasks?${params.toString()}`);
    return response.data;
  }

  async getTask(id: string): Promise<Task | null> {
    const response = await apiClient.get<Task>(`/tasks/${id}`);
    return response.data;
  }

  async createTask(taskSpec: Partial<Task>): Promise<Task> {
    const response = await apiClient.post<Task>('/tasks', taskSpec);
    return response.data;
  }

  async updateTask(id: string, updates: Partial<Task>): Promise<Task> {
    const response = await apiClient.patch<Task>(`/tasks/${id}`, updates);
    return response.data;
  }

  async cancelTask(id: string, reason?: string): Promise<Task> {
    const response = await apiClient.post<Task>(`/tasks/${id}/cancel`, { reason });
    return response.data;
  }

  async retryTask(id: string): Promise<Task> {
    const response = await apiClient.post<Task>(`/tasks/${id}/retry`);
    return response.data;
  }

  async assignTask(taskId: string, agentId: string): Promise<Task> {
    const response = await apiClient.post<Task>(`/tasks/${taskId}/assign`, { agent_id: agentId });
    return response.data;
  }

  async unassignTask(taskId: string): Promise<Task> {
    const response = await apiClient.post<Task>(`/tasks/${taskId}/unassign`);
    return response.data;
  }

  async getTaskResult(taskId: string): Promise<TaskResult | null> {
    const response = await apiClient.get<TaskResult>(`/tasks/${taskId}/result`);
    return response.data;
  }

  async getTaskLogs(taskId: string): Promise<any[]> {
    const response = await apiClient.get<any[]>(`/tasks/${taskId}/logs`);
    return response.data || [];
  }

  async getTaskArtifacts(taskId: string): Promise<any[]> {
    const response = await apiClient.get<any[]>(`/tasks/${taskId}/artifacts`);
    return response.data || [];
  }

  async downloadTaskArtifact(taskId: string, artifactId: string): Promise<Blob> {
    const response = await fetch(`/api/tasks/${taskId}/artifacts/${artifactId}/download`);
    if (!response.ok) {
      throw new Error('Failed to download artifact');
    }
    return response.blob();
  }

  async getTaskQueueStats(): Promise<any> {
    const response = await apiClient.get<any>('/tasks/queue/stats');
    return response.data;
  }

  async pauseTaskQueue(): Promise<void> {
    await apiClient.post('/tasks/queue/pause');
  }

  async resumeTaskQueue(): Promise<void> {
    await apiClient.post('/tasks/queue/resume');
  }

  async clearTaskQueue(): Promise<void> {
    await apiClient.post('/tasks/queue/clear');
  }
}

export const taskService = new TaskService();
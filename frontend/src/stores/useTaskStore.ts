import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { Task, TaskFilters, WebSocketMessage } from '@/types';
import { taskService } from '@/services';
import { wsManager } from '@/utils/websocket';

interface TaskStore {
  // State
  tasks: Task[];
  selectedTask: Task | null;
  filters: TaskFilters;
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
  realtimeUpdates: boolean;
  lastUpdated: string | null;

  // Actions
  fetchTasks: (page?: number, filters?: TaskFilters) => Promise<void>;
  setSelectedTask: (task: Task | null) => void;
  createTask: (taskSpec: Partial<Task>) => Promise<void>;
  updateTask: (taskId: string, updates: Partial<Task>) => void;
  cancelTask: (taskId: string, reason?: string) => Promise<void>;
  retryTask: (taskId: string) => Promise<void>;
  assignTask: (taskId: string, agentId: string) => Promise<void>;
  unassignTask: (taskId: string) => Promise<void>;
  setFilters: (filters: Partial<TaskFilters>) => void;
  clearFilters: () => void;
  toggleRealtimeUpdates: () => void;
  refreshTasks: () => Promise<void>;
  loadMoreTasks: () => Promise<void>;

  // Internal actions
  _setLoading: (loading: boolean) => void;
  _setError: (error: string | null) => void;
  _setTasks: (tasks: Task[], pagination: any) => void;
  _addTask: (task: Task) => void;
  _updateTask: (taskId: string, updates: Partial<Task>) => void;
  _updateTaskFromWebSocket: (message: WebSocketMessage) => void;
}

export const useTaskStore = create<TaskStore>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // Initial state
      tasks: [],
      selectedTask: null,
      filters: {},
      loading: false,
      error: null,
      pagination: {
        page: 1,
        pageSize: 20,
        total: 0,
        totalPages: 0
      },
      realtimeUpdates: true,
      lastUpdated: null,

      // Actions
      fetchTasks: async (page = 1, filters) => {
        const { _setLoading, _setError, _setTasks, filters: currentFilters } = get();

        try {
          _setLoading(true);
          _setError(null);

          const response = await taskService.getTasks(
            filters || currentFilters,
            page,
            get().pagination.pageSize
          );

          _setTasks(response.data || [], response.pagination);
        } catch (error) {
          _setError(error instanceof Error ? error.message : 'Failed to fetch tasks');
        } finally {
          _setLoading(false);
        }
      },

      setSelectedTask: (task) => {
        set({ selectedTask: task });
      },

      createTask: async (taskSpec) => {
        try {
          const task = await taskService.createTask(taskSpec);
          get()._addTask(task);
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to create task'
          });
        }
      },

      updateTask: (taskId, updates) => {
        get()._updateTask(taskId, updates);
      },

      cancelTask: async (taskId, reason) => {
        try {
          await taskService.cancelTask(taskId, reason);
          get()._updateTask(taskId, { status: 'cancelled' });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to cancel task'
          });
        }
      },

      retryTask: async (taskId) => {
        try {
          await taskService.retryTask(taskId);
          get()._updateTask(taskId, { status: 'pending' });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to retry task'
          });
        }
      },

      assignTask: async (taskId, agentId) => {
        try {
          await taskService.assignTask(taskId, agentId);
          get()._updateTask(taskId, { assignedAgentId: agentId, status: 'in_progress' });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to assign task'
          });
        }
      },

      unassignTask: async (taskId) => {
        try {
          await taskService.unassignTask(taskId);
          get()._updateTask(taskId, { assignedAgentId: undefined, status: 'pending' });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to unassign task'
          });
        }
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
          wsManager.onMessageType('task_assignment', (message) => {
            get()._updateTaskFromWebSocket(message);
          });
          wsManager.onMessageType('task_result', (message) => {
            get()._updateTaskFromWebSocket(message);
          });
        } else {
          // Disable WebSocket updates
          wsManager.offMessageType('task_assignment');
          wsManager.offMessageType('task_result');
        }
      },

      refreshTasks: async () => {
        const { pagination } = get();
        await get().fetchTasks(pagination.page);
      },

      loadMoreTasks: async () => {
        const { pagination } = get();
        if (pagination.page < pagination.totalPages) {
          await get().fetchTasks(pagination.page + 1);
        }
      },

      // Internal actions
      _setLoading: (loading) => {
        set({ loading });
      },

      _setError: (error) => {
        set({ error });
      },

      _setTasks: (tasks, pagination) => {
        set({
          tasks,
          pagination,
          lastUpdated: new Date().toISOString()
        });
      },

      _addTask: (task) => {
        set((state) => ({
          tasks: [task, ...state.tasks],
          pagination: {
            ...state.pagination,
            total: state.pagination.total + 1
          },
          lastUpdated: new Date().toISOString()
        }));
      },

      _updateTask: (taskId, updates) => {
        set((state) => ({
          tasks: state.tasks.map((task) =>
            task.id === taskId ? { ...task, ...updates, updatedAt: new Date().toISOString() } : task
          ),
          selectedTask:
            state.selectedTask?.id === taskId
              ? { ...state.selectedTask, ...updates, updatedAt: new Date().toISOString() }
              : state.selectedTask,
          lastUpdated: new Date().toISOString()
        }));
      },

      _updateTaskFromWebSocket: (message) => {
        if (message.type === 'task_assignment') {
          const task = message.payload as Task;
          get()._addTask(task);
        } else if (message.type === 'task_result') {
          const { taskId, result } = message.payload;
          get()._updateTask(taskId, {
            status: result.success ? 'completed' : 'failed',
            result,
            completedAt: result.completedAt,
            progress: 100
          });
        }
      }
    })),
    {
      name: 'task-store'
    }
  )
);

// Initialize WebSocket listeners when store is created
useTaskStore.subscribe((state) => {
  if (state.realtimeUpdates && !wsManager.isConnected()) {
    wsManager.connect().catch(console.error);
  }
});
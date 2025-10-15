import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { tokenStorage } from './tokenStorage';
import { ApiResponse, ApiError, TokenResponse } from '@/types';

class ApiClient {
  private client: AxiosInstance;
  private refreshTokenPromise: Promise<string> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for authentication
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = tokenStorage.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshAuthToken();
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
            }
            return this.client(originalRequest);
          } catch (refreshError) {
            tokenStorage.clearTokens();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(this.handleError(error));
      }
    );
  }

  private async refreshAuthToken(): Promise<string> {
    if (this.refreshTokenPromise) {
      return this.refreshTokenPromise;
    }

    this.refreshTokenPromise = this.doRefreshToken();

    try {
      const token = await this.refreshTokenPromise;
      return token;
    } finally {
      this.refreshTokenPromise = null;
    }
  }

  private async doRefreshToken(): Promise<string> {
    const refreshToken = tokenStorage.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await axios.post<TokenResponse>(
      `${import.meta.env.VITE_API_URL}/auth/refresh`,
      { refresh_token: refreshToken }
    );

    tokenStorage.storeTokens(response.data);
    return response.data.access_token;
  }

  private handleError(error: AxiosError): ApiError {
    const apiError: ApiError = {
      code: error.code || 'UNKNOWN_ERROR',
      message: error.message || 'An unexpected error occurred',
      timestamp: new Date().toISOString(),
      requestId: error.response?.headers['x-request-id']
    };

    if (error.response?.data) {
      const errorData = error.response.data as any;
      apiError.code = errorData.code || apiError.code;
      apiError.message = errorData.message || errorData.error || apiError.message;
      apiError.details = errorData.details;
    }

    return apiError;
  }

  async get<T>(url: string, params?: any): Promise<ApiResponse<T>> {
    const response = await this.client.get<ApiResponse<T>>(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.client.post<ApiResponse<T>>(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.client.put<ApiResponse<T>>(url, data);
    return response.data;
  }

  async patch<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.client.patch<ApiResponse<T>>(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<ApiResponse<T>> {
    const response = await this.client.delete<ApiResponse<T>>(url);
    return response.data;
  }

  // WebSocket connection helper
  createWebSocket(url: string): WebSocket {
    const wsUrl = url.startsWith('ws') ? url : `ws://${url}`;
    return new WebSocket(wsUrl);
  }
}

export const apiClient = new ApiClient();
export default apiClient;
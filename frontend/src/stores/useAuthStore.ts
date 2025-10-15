import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { AuthConfig, TokenResponse, TokenManager } from '@/types';

interface AuthStore {
  // State
  isAuthenticated: boolean;
  user: any | null;
  loading: boolean;
  error: string | null;

  // Actions
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  clearError: () => void;
  initializeAuth: () => Promise<void>;

  // Internal actions
  _setLoading: (loading: boolean) => void;
  _setError: (error: string | null) => void;
  _setAuthenticated: (authenticated: boolean) => void;
  _setUser: (user: any | null) => void;
}

// Mock authentication for development
const mockAuth = {
  login: async (username: string, password: string) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));

    if (username === 'admin' && password === 'password') {
      return {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        expires_in: 3600,
        token_type: 'Bearer',
        scope: 'all'
      };
    }

    throw new Error('Invalid credentials');
  },

  getUserInfo: async () => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return {
      id: '1',
      username: 'admin',
      email: 'admin@ai-agent-sdk.com',
      name: 'Administrator',
      roles: ['admin']
    };
  }
};

export const useAuthStore = create<AuthStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        isAuthenticated: false,
        user: null,
        loading: false,
        error: null,

        // Actions
        login: async (username, password) => {
          const { _setLoading, _setError, _setAuthenticated, _setUser } = get();

          try {
            _setLoading(true);
            _setError(null);

            const tokenResponse = await mockAuth.login(username, password);
            const userInfo = await mockAuth.getUserInfo();

            // Store tokens (in a real app, this would use the tokenStorage utility)
            localStorage.setItem('access_token', tokenResponse.access_token);
            localStorage.setItem('refresh_token', tokenResponse.refresh_token);

            _setAuthenticated(true);
            _setUser(userInfo);
          } catch (error) {
            _setError(error instanceof Error ? error.message : 'Login failed');
          } finally {
            _setLoading(false);
          }
        },

        logout: () => {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');

          set({
            isAuthenticated: false,
            user: null,
            error: null
          });
        },

        refreshToken: async () => {
          // In a real implementation, this would use the refresh token
          // For now, we'll just clear authentication
          const { logout } = get();
          logout();
        },

        clearError: () => {
          set({ error: null });
        },

        initializeAuth: async () => {
          const { _setLoading, _setAuthenticated, _setUser } = get();

          const accessToken = localStorage.getItem('access_token');

          if (accessToken) {
            _setLoading(true);

            try {
              // In a real app, validate the token and get user info
              const userInfo = await mockAuth.getUserInfo();

              _setAuthenticated(true);
              _setUser(userInfo);
            } catch (error) {
              // Token is invalid, clear it
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
            } finally {
              _setLoading(false);
            }
          }
        },

        // Internal actions
        _setLoading: (loading) => {
          set({ loading });
        },

        _setError: (error) => {
          set({ error });
        },

        _setAuthenticated: (authenticated) => {
          set({ isAuthenticated: authenticated });
        },

        _setUser: (user) => {
          set({ user });
        }
      }),
      {
        name: 'auth-store',
        partialize: (state) => ({
          isAuthenticated: state.isAuthenticated,
          user: state.user
        })
      }
    ),
    {
      name: 'auth-store'
    }
  )
);

// Initialize auth on app start
useAuthStore.getState().initializeAuth();
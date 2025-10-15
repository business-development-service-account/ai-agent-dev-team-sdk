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

// OAuth2 authentication implementation
const oauth2Auth = {
  login: async (username: string, password: string) => {
    // OAuth2 Resource Owner Password Credentials Grant
    const tokenUrl = import.meta.env.VITE_OAUTH_TOKEN_URL || 'http://localhost:8000/auth/token';
    const clientId = import.meta.env.VITE_OAUTH_CLIENT_ID || 'ai-agent-sdk-client';

    const params = new URLSearchParams();
    params.append('grant_type', 'password');
    params.append('username', username);
    params.append('password', password);
    params.append('client_id', clientId);
    params.append('scope', 'all');

    const response = await fetch(tokenUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    });

    if (!response.ok) {
      throw new Error('Authentication failed');
    }

    return await response.json();
  },

  getUserInfo: async () => {
    const token = tokenStorage.getAccessToken();
    if (!token) {
      throw new Error('No access token available');
    }

    const userInfoUrl = import.meta.env.VITE_USER_INFO_URL || 'http://localhost:8000/auth/user';

    const response = await fetch(userInfoUrl, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get user info');
    }

    return await response.json();
  },

  refreshToken: async (refreshToken: string) => {
    const tokenUrl = import.meta.env.VITE_OAUTH_TOKEN_URL || 'http://localhost:8000/auth/token';
    const clientId = import.meta.env.VITE_OAUTH_CLIENT_ID || 'ai-agent-sdk-client';

    const params = new URLSearchParams();
    params.append('grant_type', 'refresh_token');
    params.append('refresh_token', refreshToken);
    params.append('client_id', clientId);

    const response = await fetch(tokenUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    return await response.json();
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

            const tokenResponse = await oauth2Auth.login(username, password);
            const userInfo = await oauth2Auth.getUserInfo();

            // Store tokens using the tokenStorage utility
            tokenStorage.setTokens(tokenResponse.access_token, tokenResponse.refresh_token);

            _setAuthenticated(true);
            _setUser(userInfo);
          } catch (error) {
            _setError(error instanceof Error ? error.message : 'Login failed');
          } finally {
            _setLoading(false);
          }
        },

        logout: () => {
          tokenStorage.clearTokens();

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
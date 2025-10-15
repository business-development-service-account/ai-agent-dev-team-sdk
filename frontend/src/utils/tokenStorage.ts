import { TokenResponse } from '@/types';

export const tokenStorage = {
  getAccessToken: (): string | null => {
    return sessionStorage.getItem('access_token');
  },

  getRefreshToken: (): string | null => {
    return localStorage.getItem('refresh_token');
  },

  setTokens: (accessToken: string, refreshToken: string): void => {
    sessionStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  },

  clearTokens: (): void => {
    sessionStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  isTokenExpired: (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp < currentTime;
    } catch {
      return true;
    }
  },

  storeTokens: (tokens: TokenResponse): void => {
    tokenStorage.setTokens(tokens.access_token, tokens.refresh_token);
  }
};
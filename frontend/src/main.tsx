import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import './styles/globals.css';

// Ant Design theme configuration
const theme = {
  token: {
    colorPrimary: '#3b82f6',
    colorSuccess: '#10b981',
    colorWarning: '#f59e0b',
    colorError: '#ef4444',
    colorInfo: '#6366f1',
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    fontSize: 14,
    borderRadius: 8,
  },
  components: {
    Layout: {
      headerBg: '#ffffff',
      siderBg: '#fafafa',
      bodyBg: '#ffffff',
    },
    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: '#eff6ff',
      itemHoverBg: '#f3f4f6',
    },
    Card: {
      borderRadius: 8,
    },
    Button: {
      borderRadius: 6,
    },
  },
};

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 60 * 1000, // 1 minute
      refetchOnWindowFocus: false,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ConfigProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <App />
        </QueryClientProvider>
      </ConfigProvider>
    </BrowserRouter>
  </React.StrictMode>
);
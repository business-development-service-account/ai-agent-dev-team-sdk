import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from 'antd';
import MainLayout from '@/components/layout/MainLayout';
import Dashboard from '@/pages/Dashboard';
import AgentMonitor from '@/pages/AgentMonitor';
import TaskManager from '@/pages/TaskManager';
import SystemConfig from '@/pages/SystemConfig';
import Login from '@/pages/Login';
import { useAuthStore } from '@/stores/useAuthStore';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

const { Content } = Layout;

function App() {
  const { isAuthenticated, loading } = useAuthStore();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <MainLayout>
      <Content className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/agents" element={<AgentMonitor />} />
          <Route path="/tasks" element={<TaskManager />} />
          <Route path="/config" element={<SystemConfig />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Content>
    </MainLayout>
  );
}

export default App;
import React, { useState, useEffect } from 'react';
import { Layout, Menu, Avatar, Dropdown, Button, Space, Badge, Tooltip, Switch } from 'antd';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  RobotOutlined,
  UnorderedListOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  WifiOutlined,
  DisconnectOutlined
} from '@ant-design/icons';
import { useAuthStore } from '@/stores/useAuthStore';
import { useAgentStore } from '@/stores/useAgentStore';
import { NavigationItem } from '@/types';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { agents, realtimeUpdates, toggleRealtimeUpdates } = useAgentStore();

  const navigationItems: NavigationItem[] = [
    {
      key: '/dashboard',
      label: 'Dashboard',
      icon: <DashboardOutlined />,
      path: '/dashboard'
    },
    {
      key: '/agents',
      label: 'Agent Monitor',
      icon: <RobotOutlined />,
      path: '/agents',
      badge: {
        count: agents.filter(a => a.status === 'busy').length,
        color: 'blue'
      }
    },
    {
      key: '/tasks',
      label: 'Task Manager',
      icon: <UnorderedListOutlined />,
      path: '/tasks'
    },
    {
      key: '/config',
      label: 'System Config',
      icon: <SettingOutlined />,
      path: '/config'
    }
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
      onClick: () => navigate('/profile')
    },
    {
      type: 'divider' as const
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: handleLogout
    }
  ];

  // Initialize WebSocket connection
  useEffect(() => {
    if (realtimeUpdates) {
      import('@/utils/websocket').then(({ wsManager }) => {
        wsManager.connect().catch(console.error);
      });
    }
  }, [realtimeUpdates]);

  const activeAgents = agents.filter(a => a.status !== 'offline').length;
  const busyAgents = agents.filter(a => a.status === 'busy').length;

  return (
    <Layout className="min-h-screen">
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        className="bg-white border-r border-gray-200"
        width={240}
      >
        <div className="h-16 flex items-center justify-center border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <RobotOutlined className="text-2xl text-blue-600" />
            {!collapsed && (
              <span className="text-lg font-semibold text-gray-900">
                Agent SDK
              </span>
            )}
          </div>
        </div>

        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={navigationItems.map(item => ({
            key: item.key,
            icon: item.icon,
            label: (
              <div className="flex items-center justify-between">
                <span>{item.label}</span>
                {item.badge && (
                  <Badge
                    count={item.badge.count}
                    size="small"
                    color={item.badge.color}
                  />
                )}
              </div>
            )
          }))}
          onClick={handleMenuClick}
          className="border-r-0"
        />
      </Sider>

      <Layout>
        <Header className="bg-white border-b border-gray-200 px-6 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              className="text-lg"
            />

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">Real-time:</span>
                <Switch
                  checked={realtimeUpdates}
                  onChange={toggleRealtimeUpdates}
                  size="small"
                />
                <Tooltip title={realtimeUpdates ? 'Connected' : 'Disconnected'}>
                  {realtimeUpdates ? (
                    <WifiOutlined className="text-green-500" />
                  ) : (
                    <DisconnectOutlined className="text-gray-400" />
                  )}
                </Tooltip>
              </div>

              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span>Active: <strong>{activeAgents}</strong></span>
                <span>Busy: <strong>{busyAgents}</strong></span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <Tooltip title="Notifications">
              <Button type="text" icon={<BellOutlined />} />
            </Tooltip>

            <Dropdown
              menu={{ items: userMenuItems }}
              placement="bottomRight"
              trigger={['click']}
            >
              <div className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 px-2 py-1 rounded">
                <Avatar
                  size="small"
                  icon={<UserOutlined />}
                  src={user?.avatar}
                />
                <span className="text-sm font-medium">{user?.name || 'User'}</span>
              </div>
            </Dropdown>
          </div>
        </Header>

        <Content className="bg-gray-50">
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
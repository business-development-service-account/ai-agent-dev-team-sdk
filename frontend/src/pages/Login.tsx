import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, Alert, Space } from 'antd';
import { UserOutlined, LockOutlined, RobotOutlined } from '@ant-design/icons';
import { useAuthStore } from '@/stores/useAuthStore';
import { LoadingSpinner } from '@/components/common';

const { Title, Text } = Typography;

interface LoginForm {
  username: string;
  password: string;
}

const Login: React.FC = () => {
  const [form] = Form.useForm();
  const { login, loading, error, clearError } = useAuthStore();

  const handleSubmit = async (values: LoginForm) => {
    clearError();
    await login(values.username, values.password);
  };

  const handleValuesChange = () => {
    clearError();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Space direction="vertical" size="large">
            <RobotOutlined className="text-6xl text-blue-600" />
            <div>
              <Title level={2} className="m-0">
                AI Agent SDK
              </Title>
              <Text type="secondary">
                Developer Dashboard
              </Text>
            </div>
          </Space>
        </div>

        <Card className="shadow-lg">
          <Form
            form={form}
            name="login"
            onFinish={handleSubmit}
            onValuesChange={handleValuesChange}
            layout="vertical"
            size="large"
          >
            {error && (
              <Alert
                message="Login Failed"
                description={error}
                type="error"
                showIcon
                className="mb-6"
                closable
                onClose={clearError}
              />
            )}

            <Form.Item
              name="username"
              label="Username"
              rules={[
                { required: true, message: 'Please input your username!' },
                { min: 3, message: 'Username must be at least 3 characters!' }
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="Enter your username"
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="password"
              label="Password"
              rules={[
                { required: true, message: 'Please input your password!' },
                { min: 6, message: 'Password must be at least 6 characters!' }
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Enter your password"
                autoComplete="current-password"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                className="w-full"
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </Form.Item>
          </Form>

          <div className="text-center mt-6">
            <Text type="secondary" className="text-xs">
              Demo credentials: admin / password
            </Text>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Login;
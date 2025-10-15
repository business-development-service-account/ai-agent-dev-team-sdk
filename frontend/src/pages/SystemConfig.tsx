import React, { useEffect, useState } from 'react';
import {
  Card,
  Tabs,
  Table,
  Button,
  Space,
  Typography,
  Form,
  Input,
  Select,
  InputNumber,
  Switch,
  Modal,
  message,
  Upload,
  Descriptions,
  Tag,
  Row,
  Col,
  Statistic,
  Alert
} from 'antd';
import {
  SettingOutlined,
  FileTextOutlined,
  ServerOutlined,
  UploadOutlined,
  DownloadOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  StopOutlined
} from '@ant-design/icons';
import { useSystemStore } from '@/stores/useSystemStore';
import { SystemPrompt, MCPServer } from '@/types';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { TextArea } = Input;
const { Option } = Select;

const SystemConfig: React.FC = () => {
  const {
    config,
    systemPrompts,
    mcpServers,
    systemStatus,
    loading,
    error,
    fetchConfig,
    fetchSystemPrompts,
    fetchMCPServers,
    createSystemPrompt,
    updateSystemPrompt,
    deleteSystemPrompt,
    loadExternalPrompts,
    addMCPServer,
    updateMCPServer,
    deleteMCPServer,
    testMCPServerConnection,
    restartMCPServer,
    exportConfiguration,
    importConfiguration
  } = useSystemStore();

  const [promptModalVisible, setPromptModalVisible] = useState(false);
  const [serverModalVisible, setServerModalVisible] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<SystemPrompt | null>(null);
  const [editingServer, setEditingServer] = useState<MCPServer | null>(null);
  const [promptForm] = Form.useForm();
  const [serverForm] = Form.useForm();

  useEffect(() => {
    fetchConfig();
    fetchSystemPrompts();
    fetchMCPServers();
  }, [fetchConfig, fetchSystemPrompts, fetchMCPServers]);

  const handleCreatePrompt = async (values: any) => {
    try {
      await createSystemPrompt({
        ...values,
        version: '1.0.0',
        isActive: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      });
      message.success('System prompt created successfully');
      setPromptModalVisible(false);
      promptForm.resetFields();
    } catch (error) {
      message.error('Failed to create system prompt');
    }
  };

  const handleUpdatePrompt = async (values: any) => {
    if (!editingPrompt) return;

    try {
      await updateSystemPrompt(editingPrompt.id, {
        ...values,
        updatedAt: new Date().toISOString()
      });
      message.success('System prompt updated successfully');
      setPromptModalVisible(false);
      setEditingPrompt(null);
      promptForm.resetFields();
    } catch (error) {
      message.error('Failed to update system prompt');
    }
  };

  const handleDeletePrompt = async (id: string) => {
    Modal.confirm({
      title: 'Delete System Prompt',
      content: 'Are you sure you want to delete this system prompt?',
      okText: 'Yes',
      cancelText: 'No',
      onOk: async () => {
        try {
          await deleteSystemPrompt(id);
          message.success('System prompt deleted successfully');
        } catch (error) {
          message.error('Failed to delete system prompt');
        }
      }
    });
  };

  const handleCreateServer = async (values: any) => {
    try {
      await addMCPServer({
        ...values,
        status: 'offline',
        lastHeartbeat: new Date().toISOString(),
        metrics: {
          requestsHandled: 0,
          averageResponseTime: 0,
          errorRate: 0
        }
      });
      message.success('MCP server added successfully');
      setServerModalVisible(false);
      serverForm.resetFields();
    } catch (error) {
      message.error('Failed to add MCP server');
    }
  };

  const handleUpdateServer = async (values: any) => {
    if (!editingServer) return;

    try {
      await updateMCPServer(editingServer.id, values);
      message.success('MCP server updated successfully');
      setServerModalVisible(false);
      setEditingServer(null);
      serverForm.resetFields();
    } catch (error) {
      message.error('Failed to update MCP server');
    }
  };

  const handleDeleteServer = async (id: string) => {
    Modal.confirm({
      title: 'Delete MCP Server',
      content: 'Are you sure you want to delete this MCP server?',
      okText: 'Yes',
      cancelText: 'No',
      onOk: async () => {
        try {
          await deleteServer(id);
          message.success('MCP server deleted successfully');
        } catch (error) {
          message.error('Failed to delete MCP server');
        }
      }
    });
  };

  const handleTestConnection = async (id: string) => {
    try {
      await testMCPServerConnection(id);
      message.success('Connection test successful');
    } catch (error) {
      message.error('Connection test failed');
    }
  };

  const handleRestartServer = async (id: string) => {
    try {
      await restartMCPServer(id);
      message.success('Server restarted successfully');
    } catch (error) {
      message.error('Failed to restart server');
    }
  };

  const handleExportConfig = async () => {
    try {
      const blob = await exportConfiguration();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'system-config.json';
      a.click();
      window.URL.revokeObjectURL(url);
      message.success('Configuration exported successfully');
    } catch (error) {
      message.error('Failed to export configuration');
    }
  };

  const handleImportConfig = (file: File) => {
    importConfiguration(file)
      .then(() => {
        message.success('Configuration imported successfully');
      })
      .catch((error) => {
        message.error('Failed to import configuration');
      });
    return false; // Prevent default upload behavior
  };

  const promptColumns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => (
        <Tag color={type === 'system' ? 'blue' : type === 'agent' ? 'green' : 'orange'}>
          {type.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Version',
      dataIndex: 'version',
      key: 'version'
    },
    {
      title: 'Active',
      dataIndex: 'isActive',
      key: 'isActive',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'ACTIVE' : 'INACTIVE'}
        </Tag>
      )
    },
    {
      title: 'Updated',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      render: (updatedAt: string) => (
        <Text className="text-xs">
          {dayjs(updatedAt).format('MMM DD, HH:mm')}
        </Text>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (record: SystemPrompt) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EditOutlined />}
            size="small"
            onClick={() => {
              setEditingPrompt(record);
              promptForm.setFieldsValue(record);
              setPromptModalVisible(true);
            }}
          />
          <Button
            type="text"
            icon={<DeleteOutlined />}
            size="small"
            onClick={() => handleDeletePrompt(record.id)}
          />
        </Space>
      )
    }
  ];

  const serverColumns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type'
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'online' ? 'green' : status === 'error' ? 'red' : 'gray'}>
          {status.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Endpoint',
      dataIndex: 'endpoint',
      key: 'endpoint'
    },
    {
      title: 'Last Heartbeat',
      dataIndex: 'lastHeartbeat',
      key: 'lastHeartbeat',
      render: (lastHeartbeat: string) => (
        <Text className="text-xs">
          {dayjs(lastHeartbeat).format('MMM DD, HH:mm')}
        </Text>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (record: MCPServer) => (
        <Space size="small">
          <Button
            type="text"
            icon={<PlayCircleOutlined />}
            size="small"
            onClick={() => handleTestConnection(record.id)}
          />
          <Button
            type="text"
            icon={<ReloadOutlined />}
            size="small"
            onClick={() => handleRestartServer(record.id)}
          />
          <Button
            type="text"
            icon={<EditOutlined />}
            size="small"
            onClick={() => {
              setEditingServer(record);
              serverForm.setFieldsValue(record);
              setServerModalVisible(true);
            }}
          />
          <Button
            type="text"
            icon={<DeleteOutlined />}
            size="small"
            onClick={() => handleDeleteServer(record.id)}
          />
        </Space>
      )
    }
  ];

  return (
    <div className="p-6">
      <div className="mb-6">
        <Title level={2}>System Configuration</Title>
        <Text type="secondary">
          Manage system settings, prompts, and MCP servers
        </Text>
      </div>

      {/* System Status Overview */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="System Prompts"
              value={systemPrompts.length}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="MCP Servers"
              value={mcpServers.length}
              prefix={<ServerOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Online Servers"
              value={mcpServers.filter(s => s.status === 'online').length}
              valueStyle={{ color: '#3f8600' }}
              prefix={<PlayCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Active Prompts"
              value={systemPrompts.filter(p => p.isActive).length}
              valueStyle={{ color: '#1890ff' }}
              prefix={<SettingOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Tabs defaultActiveKey="prompts">
        {/* System Prompts Tab */}
        <TabPane tab="System Prompts" key="prompts">
          <Card>
            <div className="mb-4 flex justify-between items-center">
              <Title level={4}>System Prompts</Title>
              <Space>
                <Upload
                  accept=".md,.txt"
                  showUploadList={false}
                  beforeUpload={(file) => {
                    loadExternalPrompts('/');
                    return false;
                  }}
                >
                  <Button icon={<UploadOutlined />}>
                    Load External Prompts
                  </Button>
                </Upload>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => {
                    setEditingPrompt(null);
                    promptForm.resetFields();
                    setPromptModalVisible(true);
                  }}
                >
                  Add Prompt
                </Button>
              </Space>
            </div>

            <Table
              columns={promptColumns}
              dataSource={systemPrompts}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true
              }}
            />
          </Card>
        </TabPane>

        {/* MCP Servers Tab */}
        <TabPane tab="MCP Servers" key="servers">
          <Card>
            <div className="mb-4 flex justify-between items-center">
              <Title level={4}>MCP Servers</Title>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => {
                  setEditingServer(null);
                  serverForm.resetFields();
                  setServerModalVisible(true);
                }}
              >
                Add Server
              </Button>
            </div>

            <Table
              columns={serverColumns}
              dataSource={mcpServers}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true
              }}
            />
          </Card>
        </TabPane>

        {/* Configuration Tab */}
        <TabPane tab="Configuration" key="config">
          <Card>
            <div className="mb-4 flex justify-between items-center">
              <Title level={4}>System Configuration</Title>
              <Space>
                <Upload
                  accept=".json"
                  showUploadList={false}
                  beforeUpload={handleImportConfig}
                >
                  <Button icon={<UploadOutlined />}>
                    Import Config
                  </Button>
                </Upload>
                <Button
                  icon={<DownloadOutlined />}
                  onClick={handleExportConfig}
                >
                  Export Config
                </Button>
              </Space>
            </div>

            {config && (
              <Descriptions bordered column={1}>
                <Descriptions.Item label="Max Concurrent Agents">
                  {config.agents.maxConcurrent}
                </Descriptions.Item>
                <Descriptions.Item label="Agent Timeout (ms)">
                  {config.agents.timeoutMs}
                </Descriptions.Item>
                <Descriptions.Item label="Agent Retry Attempts">
                  {config.agents.retryAttempts}
                </Descriptions.Item>
                <Descriptions.Item label="Max Queue Size">
                  {config.tasks.maxQueueSize}
                </Descriptions.Item>
                <Descriptions.Item label="Default Task Timeout (ms)">
                  {config.tasks.defaultTimeoutMs}
                </Descriptions.Item>
                <Descriptions.Item label="Metrics Interval (ms)">
                  {config.monitoring.metricsIntervalMs}
                </Descriptions.Item>
                <Descriptions.Item label="Retention Days">
                  {config.monitoring.retentionDays}
                </Descriptions.Item>
              </Descriptions>
            )}
          </Card>
        </TabPane>
      </Tabs>

      {/* System Prompt Modal */}
      <Modal
        title={editingPrompt ? 'Edit System Prompt' : 'Create System Prompt'}
        open={promptModalVisible}
        onCancel={() => {
          setPromptModalVisible(false);
          setEditingPrompt(null);
          promptForm.resetFields();
        }}
        footer={null}
        width={800}
      >
        <Form
          form={promptForm}
          layout="vertical"
          onFinish={editingPrompt ? handleUpdatePrompt : handleCreatePrompt}
        >
          <Form.Item
            name="name"
            label="Prompt Name"
            rules={[{ required: true, message: 'Please enter prompt name' }]}
          >
            <Input placeholder="Enter prompt name" />
          </Form.Item>

          <Form.Item
            name="type"
            label="Prompt Type"
            rules={[{ required: true, message: 'Please select prompt type' }]}
          >
            <Select placeholder="Select prompt type">
              <Option value="system">System</Option>
              <Option value="agent">Agent</Option>
              <Option value="task">Task</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="content"
            label="Content"
            rules={[{ required: true, message: 'Please enter prompt content' }]}
          >
            <TextArea rows={10} placeholder="Enter prompt content" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingPrompt ? 'Update' : 'Create'}
              </Button>
              <Button onClick={() => {
                setPromptModalVisible(false);
                setEditingPrompt(null);
                promptForm.resetFields();
              }}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* MCP Server Modal */}
      <Modal
        title={editingServer ? 'Edit MCP Server' : 'Add MCP Server'}
        open={serverModalVisible}
        onCancel={() => {
          setServerModalVisible(false);
          setEditingServer(null);
          serverForm.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={serverForm}
          layout="vertical"
          onFinish={editingServer ? handleUpdateServer : handleCreateServer}
        >
          <Form.Item
            name="name"
            label="Server Name"
            rules={[{ required: true, message: 'Please enter server name' }]}
          >
            <Input placeholder="Enter server name" />
          </Form.Item>

          <Form.Item
            name="type"
            label="Server Type"
            rules={[{ required: true, message: 'Please enter server type' }]}
          >
            <Input placeholder="Enter server type" />
          </Form.Item>

          <Form.Item
            name="endpoint"
            label="Endpoint"
            rules={[{ required: true, message: 'Please enter server endpoint' }]}
          >
            <Input placeholder="Enter server endpoint (e.g., http://localhost:3000)" />
          </Form.Item>

          <Form.Item
            name="capabilities"
            label="Capabilities"
          >
            <Select
              mode="tags"
              placeholder="Enter server capabilities"
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingServer ? 'Update' : 'Add'}
              </Button>
              <Button onClick={() => {
                setServerModalVisible(false);
                setEditingServer(null);
                serverForm.resetFields();
              }}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default SystemConfig;
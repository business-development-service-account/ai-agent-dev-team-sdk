import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Typography,
  Input,
  Select,
  Row,
  Col,
  Statistic,
  Modal,
  message
} from 'antd';
import {
  SearchOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { useAgentStore } from '@/stores/useAgentStore';
import { Agent, AgentFilters } from '@/types';
import AgentStatus from '@/components/common/AgentStatus';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { Search } = Input;
const { Option } = Select;

const AgentMonitor: React.FC = () => {
  const {
    agents,
    loading,
    error,
    filters,
    fetchAgents,
    setSelectedAgent,
    updateAgentStatus,
    stopAgent,
    restartAgent,
    setFilters,
    clearFilters
  } = useAgentStore();

  const [searchText, setSearchText] = useState('');
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  const handleSearch = (value: string) => {
    setSearchText(value);
    setFilters({ ...filters, search: value });
  };

  const handleFilterChange = (key: string, value: any) => {
    setFilters({ ...filters, [key]: value });
  };

  const handleClearFilters = () => {
    setSearchText('');
    clearFilters();
  };

  const handleStopAgent = async (agentId: string) => {
    Modal.confirm({
      title: 'Stop Agent',
      content: 'Are you sure you want to stop this agent?',
      okText: 'Yes',
      cancelText: 'No',
      onOk: async () => {
        try {
          await stopAgent(agentId);
          message.success('Agent stopped successfully');
        } catch (error) {
          message.error('Failed to stop agent');
        }
      }
    });
  };

  const handleRestartAgent = async (agentId: string) => {
    Modal.confirm({
      title: 'Restart Agent',
      content: 'Are you sure you want to restart this agent?',
      okText: 'Yes',
      cancelText: 'No',
      onOk: async () => {
        try {
          await restartAgent(agentId);
          message.success('Agent restarted successfully');
        } catch (error) {
          message.error('Failed to restart agent');
        }
      }
    });
  };

  const getAgentTypeColor = (type: string) => {
    const colors = {
      research: 'blue',
      codebase: 'green',
      frontend: 'purple',
      backend: 'orange',
      devops: 'red',
      security: 'yellow',
      qa: 'cyan',
      documentation: 'pink'
    };
    return colors[type as keyof typeof colors] || 'default';
  };

  const columns = [
    {
      title: 'Agent',
      key: 'agent',
      render: (agent: Agent) => (
        <Space direction="vertical" size="small">
          <div className="flex items-center space-x-2">
            <Text strong>{agent.name}</Text>
            <Tag color={getAgentTypeColor(agent.type)} size="small">
              {agent.type}
            </Tag>
          </div>
          <Text type="secondary" className="text-xs">
            {agent.description}
          </Text>
        </Space>
      )
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: Agent['status'], agent: Agent) => (
        <AgentStatus
          status={status}
          agentType={agent.type}
          lastActivity={agent.lastActivity}
          showLabel={true}
          size="small"
        />
      )
    },
    {
      title: 'Current Task',
      key: 'currentTask',
      render: (agent: Agent) => (
        <Space direction="vertical" size="small">
          {agent.currentTask ? (
            <>
              <Text>{agent.currentTask.title}</Text>
              <Text type="secondary" className="text-xs">
                {agent.currentTask.status}
              </Text>
            </>
          ) : (
            <Text type="secondary">Idle</Text>
          )}
        </Space>
      )
    },
    {
      title: 'Last Activity',
      dataIndex: 'lastActivity',
      key: 'lastActivity',
      render: (lastActivity: string) => (
        <Text className="text-xs">
          {dayjs(lastActivity).format('MMM DD, HH:mm')}
        </Text>
      )
    },
    {
      title: 'Performance',
      key: 'metrics',
      render: (agent: Agent) => (
        <Space direction="vertical" size="small">
          <div className="flex items-center space-x-4 text-xs">
            <span>Success: {agent.metrics.successRate.toFixed(1)}%</span>
            <span>Tasks: {agent.metrics.tasksCompleted}</span>
          </div>
          <div className="flex items-center space-x-4 text-xs">
            <span>Avg Time: {agent.metrics.averageExecutionTime.toFixed(0)}s</span>
          </div>
        </Space>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (agent: Agent) => (
        <Space size="small">
          {agent.status === 'busy' && (
            <Button
              type="text"
              icon={<PauseCircleOutlined />}
              size="small"
              onClick={() => handleStopAgent(agent.id)}
            />
          )}
          {agent.status === 'error' && (
            <Button
              type="text"
              icon={<PlayCircleOutlined />}
              size="small"
              onClick={() => handleRestartAgent(agent.id)}
            />
          )}
          <Button
            type="text"
            icon={<StopOutlined />}
            size="small"
            onClick={() => handleStopAgent(agent.id)}
          />
        </Space>
      )
    }
  ];

  const rowSelection = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys: React.Key[]) => {
      setSelectedRowKeys(newSelectedRowKeys as string[]);
    }
  };

  const activeAgents = agents.filter(a => a.status !== 'offline');
  const busyAgents = agents.filter(a => a.status === 'busy');
  const successfulAgents = agents.filter(a => a.status === 'success');
  const errorAgents = agents.filter(a => a.status === 'error');

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <Title level={2}>Agent Monitor</Title>
            <Text type="secondary">
              Monitor and manage your AI agent development team
            </Text>
          </div>
          <Button
            type="primary"
            icon={<ReloadOutlined />}
            onClick={() => fetchAgents()}
            loading={loading}
          >
            Refresh
          </Button>
        </div>

        {/* Statistics */}
        <Row gutter={[16, 16]} className="mb-6">
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Total Agents"
                value={agents.length}
                prefix={<CheckCircleOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Active"
                value={activeAgents.length}
                valueStyle={{ color: '#3f8600' }}
                prefix={<PlayCircleOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Busy"
                value={busyAgents.length}
                valueStyle={{ color: '#1890ff' }}
                prefix={<ClockCircleOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Errors"
                value={errorAgents.length}
                valueStyle={{ color: '#cf1322' }}
                prefix={<ExclamationCircleOutlined />}
              />
            </Card>
          </Col>
        </Row>

        {/* Filters */}
        <Card className="mb-6">
          <Row gutter={[16, 16]} align="middle">
            <Col xs={24} sm={8}>
              <Search
                placeholder="Search agents..."
                allowClear
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onSearch={handleSearch}
              />
            </Col>
            <Col xs={24} sm={4}>
              <Select
                placeholder="Type"
                allowClear
                value={filters.type}
                onChange={(value) => handleFilterChange('type', value)}
                className="w-full"
              >
                <Option value="research">Research</Option>
                <Option value="codebase">Codebase</Option>
                <Option value="frontend">Frontend</Option>
                <Option value="backend">Backend</Option>
                <Option value="devops">DevOps</Option>
                <Option value="security">Security</Option>
                <Option value="qa">QA</Option>
                <Option value="documentation">Documentation</Option>
              </Select>
            </Col>
            <Col xs={24} sm={4}>
              <Select
                placeholder="Status"
                allowClear
                value={filters.status}
                onChange={(value) => handleFilterChange('status', value)}
                className="w-full"
              >
                <Option value="idle">Idle</Option>
                <Option value="busy">Busy</Option>
                <Option value="success">Success</Option>
                <Option value="error">Error</Option>
                <Option value="offline">Offline</Option>
              </Select>
            </Col>
            <Col xs={24} sm={4}>
              <Button onClick={handleClearFilters}>
                Clear Filters
              </Button>
            </Col>
          </Row>
        </Card>
      </div>

      {/* Agents Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={agents}
          rowKey="id"
          loading={loading}
          rowSelection={rowSelection}
          pagination={{
            total: agents.length,
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} agents`
          }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </div>
  );
};

export default AgentMonitor;
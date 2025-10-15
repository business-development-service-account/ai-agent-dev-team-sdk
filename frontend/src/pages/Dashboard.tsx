import React, { useEffect } from 'react';
import { Row, Col, Card, Statistic, Typography, Space, List, Progress, Tag } from 'antd';
import {
  RobotOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  UnorderedListOutlined,
  TrophyOutlined
} from '@ant-design/icons';
import { useAgentStore } from '@/stores/useAgentStore';
import { useTaskStore } from '@/stores/useTaskStore';
import { useSystemStore } from '@/stores/useSystemStore';
import AgentStatus from '@/components/common/AgentStatus';
import TaskProgress from '@/components/common/TaskProgress';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  const { agents, fetchAgents, loading: agentsLoading } = useAgentStore();
  const { tasks, fetchTasks, loading: tasksLoading } = useTaskStore();
  const { systemStatus, fetchSystemStatus } = useSystemStore();

  useEffect(() => {
    fetchAgents();
    fetchTasks();
    fetchSystemStatus();
  }, [fetchAgents, fetchTasks, fetchSystemStatus]);

  const activeAgents = agents.filter(a => a.status !== 'offline');
  const busyAgents = agents.filter(a => a.status === 'busy');
  const successfulAgents = agents.filter(a => a.status === 'success');
  const errorAgents = agents.filter(a => a.status === 'error');

  const recentTasks = tasks.slice(0, 5);
  const activeTasks = tasks.filter(t => t.status === 'in_progress');
  const completedTasks = tasks.filter(t => t.status === 'completed');
  const failedTasks = tasks.filter(t => t.status === 'failed');

  const systemUptime = systemStatus?.uptime ? dayjs.duration(systemStatus.uptime, 'seconds').humanize() : 'Unknown';

  return (
    <div className="p-6">
      <div className="mb-6">
        <Title level={2}>Dashboard</Title>
        <Text type="secondary">
          Real-time overview of your AI agent development team
        </Text>
      </div>

      {/* System Status Cards */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Agents"
              value={agents.length}
              prefix={<RobotOutlined />}
              loading={agentsLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Active Agents"
              value={activeAgents.length}
              valueStyle={{ color: '#3f8600' }}
              prefix={<CheckCircleOutlined />}
              loading={agentsLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Tasks"
              value={tasks.length}
              prefix={<UnorderedListOutlined />}
              loading={tasksLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="System Uptime"
              value={systemUptime}
              prefix={<TrophyOutlined />}
              loading={!systemStatus}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Agent Status Overview */}
        <Col xs={24} lg={12}>
          <Card title="Agent Status Overview" loading={agentsLoading}>
            <Space direction="vertical" className="w-full" size="middle">
              <div className="flex items-center justify-between">
                <Space>
                  <Tag color="green">Active</Tag>
                  <Text>{activeAgents.length} agents</Text>
                </Space>
                <Progress
                  percent={Math.round((activeAgents.length / agents.length) * 100)}
                  size="small"
                  strokeColor="#52c41a"
                  showInfo={false}
                />
              </div>

              <div className="flex items-center justify-between">
                <Space>
                  <Tag color="blue">Busy</Tag>
                  <Text>{busyAgents.length} agents</Text>
                </Space>
                <Progress
                  percent={agents.length > 0 ? Math.round((busyAgents.length / agents.length) * 100) : 0}
                  size="small"
                  strokeColor="#1890ff"
                  showInfo={false}
                />
              </div>

              <div className="flex items-center justify-between">
                <Space>
                  <Tag color="green">Successful</Tag>
                  <Text>{successfulAgents.length} agents</Text>
                </Space>
                <Progress
                  percent={agents.length > 0 ? Math.round((successfulAgents.length / agents.length) * 100) : 0}
                  size="small"
                  strokeColor="#52c41a"
                  showInfo={false}
                />
              </div>

              <div className="flex items-center justify-between">
                <Space>
                  <Tag color="red">Error</Tag>
                  <Text>{errorAgents.length} agents</Text>
                </Space>
                <Progress
                  percent={agents.length > 0 ? Math.round((errorAgents.length / agents.length) * 100) : 0}
                  size="small"
                  strokeColor="#ff4d4f"
                  showInfo={false}
                />
              </div>
            </Space>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <List
                size="small"
                dataSource={agents.slice(0, 5)}
                renderItem={(agent) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={
                        <AgentStatus
                          status={agent.status}
                          agentType={agent.type}
                          lastActivity={agent.lastActivity}
                          showLabel={false}
                          size="small"
                        />
                      }
                      title={agent.name}
                      description={agent.currentTask?.title || 'Idle'}
                    />
                  </List.Item>
                )}
              />
            </div>
          </Card>
        </Col>

        {/* Recent Tasks */}
        <Col xs={24} lg={12}>
          <Card title="Recent Tasks" loading={tasksLoading}>
            <Space direction="vertical" className="w-full" size="middle">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <Statistic
                    title="Active"
                    value={activeTasks.length}
                    valueStyle={{ color: '#1890ff', fontSize: '16px' }}
                  />
                </div>
                <div>
                  <Statistic
                    title="Completed"
                    value={completedTasks.length}
                    valueStyle={{ color: '#52c41a', fontSize: '16px' }}
                  />
                </div>
                <div>
                  <Statistic
                    title="Failed"
                    value={failedTasks.length}
                    valueStyle={{ color: '#ff4d4f', fontSize: '16px' }}
                  />
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <List
                  size="small"
                  dataSource={recentTasks}
                  renderItem={(task) => (
                    <List.Item>
                      <List.Item.Meta
                        title={
                          <Space>
                            <Text>{task.title}</Text>
                            <Tag color={task.status === 'completed' ? 'green' : task.status === 'failed' ? 'red' : 'blue'}>
                              {task.status}
                            </Tag>
                          </Space>
                        }
                        description={
                          <Space direction="vertical" size="small" className="w-full">
                            <Text type="secondary">
                              {task.assignedAgent?.name || 'Unassigned'}
                            </Text>
                            {task.status === 'in_progress' && (
                              <Progress
                                percent={task.progress}
                                size="small"
                                strokeColor="#1890ff"
                              />
                            )}
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              </div>
            </Space>
          </Card>
        </Col>

        {/* Active Tasks Progress */}
        {activeTasks.length > 0 && (
          <Col xs={24}>
            <Card title="Active Tasks Progress">
              <List
                grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 3 }}
                dataSource={activeTasks}
                renderItem={(task) => (
                  <List.Item>
                    <TaskProgress
                      taskId={task.id}
                      progress={task.progress}
                      currentStep={task.title}
                      estimatedTimeRemaining={task.estimatedDuration}
                      showPercentage={true}
                      showETA={true}
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        )}
      </Row>
    </div>
  );
};

export default Dashboard;
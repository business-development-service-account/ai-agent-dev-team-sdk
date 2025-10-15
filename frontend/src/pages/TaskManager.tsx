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
  DatePicker,
  Row,
  Col,
  Statistic,
  Modal,
  Form,
  message,
  Drawer,
  Descriptions,
  Progress
} from 'antd';
import {
  SearchOutlined,
  ReloadOutlined,
  PlusOutlined,
  PlayCircleOutlined,
  StopOutlined,
  RedoOutlined,
  UserOutlined,
  CalendarOutlined,
  FilterOutlined
} from '@ant-design/icons';
import { useTaskStore } from '@/stores/useTaskStore';
import { useAgentStore } from '@/stores/useAgentStore';
import { Task, TaskFilters } from '@/types';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { Search } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;

const TaskManager: React.FC = () => {
  const {
    tasks,
    loading,
    error,
    filters,
    pagination,
    fetchTasks,
    createTask,
    updateTask,
    cancelTask,
    retryTask,
    assignTask,
    unassignTask,
    setFilters,
    clearFilters,
    setSelectedTask
  } = useTaskStore();

  const { agents } = useAgentStore();
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [selectedTaskDetail, setSelectedTaskDetail] = useState<Task | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleSearch = (value: string) => {
    setFilters({ ...filters, search: value });
  };

  const handleFilterChange = (key: string, value: any) => {
    setFilters({ ...filters, [key]: value });
  };

  const handleDateRangeChange = (dates: any) => {
    if (dates && dates.length === 2) {
      setFilters({
        ...filters,
        dateRange: {
          start: dates[0].toISOString(),
          end: dates[1].toISOString()
        }
      });
    } else {
      const { dateRange, ...rest } = filters;
      setFilters(rest);
    }
  };

  const handleClearFilters = () => {
    clearFilters();
    form.resetFields();
  };

  const handleCreateTask = async (values: any) => {
    try {
      await createTask({
        ...values,
        status: 'pending',
        createdAt: new Date().toISOString(),
        progress: 0
      });
      message.success('Task created successfully');
      setCreateModalVisible(false);
      form.resetFields();
    } catch (error) {
      message.error('Failed to create task');
    }
  };

  const handleViewTask = (task: Task) => {
    setSelectedTaskDetail(task);
    setSelectedTask(task);
    setDetailDrawerVisible(true);
  };

  const handleCancelTask = async (taskId: string) => {
    Modal.confirm({
      title: 'Cancel Task',
      content: 'Are you sure you want to cancel this task?',
      okText: 'Yes',
      cancelText: 'No',
      onOk: async () => {
        try {
          await cancelTask(taskId);
          message.success('Task cancelled successfully');
        } catch (error) {
          message.error('Failed to cancel task');
        }
      }
    });
  };

  const handleRetryTask = async (taskId: string) => {
    try {
      await retryTask(taskId);
      message.success('Task retry initiated');
    } catch (error) {
      message.error('Failed to retry task');
    }
  };

  const handleAssignTask = async (taskId: string, agentId: string) => {
    try {
      await assignTask(taskId, agentId);
      message.success('Task assigned successfully');
    } catch (error) {
      message.error('Failed to assign task');
    }
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      low: 'default',
      medium: 'blue',
      high: 'orange',
      critical: 'red'
    };
    return colors[priority as keyof typeof colors] || 'default';
  };

  const getStatusColor = (status: string) => {
    const colors = {
      pending: 'default',
      in_progress: 'processing',
      completed: 'success',
      failed: 'error',
      cancelled: 'warning'
    };
    return colors[status as keyof typeof colors] || 'default';
  };

  const columns = [
    {
      title: 'Task',
      key: 'task',
      render: (task: Task) => (
        <Space direction="vertical" size="small">
          <Text strong className="cursor-pointer hover:text-blue-600" onClick={() => handleViewTask(task)}>
            {task.title}
          </Text>
          <Text type="secondary" className="text-xs">
            {task.description}
          </Text>
        </Space>
      )
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: Task['status'], task: Task) => (
        <Space direction="vertical" size="small">
          <Tag color={getStatusColor(status)}>
            {status.replace('_', ' ').toUpperCase()}
          </Tag>
          {status === 'in_progress' && (
            <Progress
              percent={task.progress}
              size="small"
              strokeColor="#1890ff"
            />
          )}
        </Space>
      )
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority: Task['priority']) => (
        <Tag color={getPriorityColor(priority)}>
          {priority.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Assigned Agent',
      key: 'assignedAgent',
      render: (task: Task) => (
        task.assignedAgent ? (
          <Space>
            <UserOutlined />
            <Text>{task.assignedAgent.name}</Text>
          </Space>
        ) : (
          <Text type="secondary">Unassigned</Text>
        )
      )
    },
    {
      title: 'Created',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (createdAt: string) => (
        <Text className="text-xs">
          {dayjs(createdAt).format('MMM DD, HH:mm')}
        </Text>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (task: Task) => (
        <Space size="small">
          <Button
            type="text"
            size="small"
            onClick={() => handleViewTask(task)}
          >
            View
          </Button>
          {task.status === 'failed' && (
            <Button
              type="text"
              icon={<RedoOutlined />}
              size="small"
              onClick={() => handleRetryTask(task.id)}
            />
          )}
          {task.status === 'in_progress' && (
            <Button
              type="text"
              icon={<StopOutlined />}
              size="small"
              onClick={() => handleCancelTask(task.id)}
            />
          )}
          {!task.assignedAgent && (
            <Select
              placeholder="Assign"
              size="small"
              style={{ width: 120 }}
              onChange={(agentId) => handleAssignTask(task.id, agentId)}
            >
              {agents.map(agent => (
                <Option key={agent.id} value={agent.id}>
                  {agent.name}
                </Option>
              ))}
            </Select>
          )}
        </Space>
      )
    }
  ];

  const pendingTasks = tasks.filter(t => t.status === 'pending');
  const activeTasks = tasks.filter(t => t.status === 'in_progress');
  const completedTasks = tasks.filter(t => t.status === 'completed');
  const failedTasks = tasks.filter(t => t.status === 'failed');

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <Title level={2}>Task Manager</Title>
            <Text type="secondary">
              Create, monitor, and manage tasks across your agent team
            </Text>
          </div>
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              Create Task
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => fetchTasks()}
              loading={loading}
            >
              Refresh
            </Button>
          </Space>
        </div>

        {/* Statistics */}
        <Row gutter={[16, 16]} className="mb-6">
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Pending"
                value={pendingTasks.length}
                valueStyle={{ color: '#1890ff' }}
                prefix={<CalendarOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Active"
                value={activeTasks.length}
                valueStyle={{ color: '#52c41a' }}
                prefix={<PlayCircleOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Completed"
                value={completedTasks.length}
                valueStyle={{ color: '#3f8600' }}
                prefix={<UserOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Failed"
                value={failedTasks.length}
                valueStyle={{ color: '#cf1322' }}
                prefix={<StopOutlined />}
              />
            </Card>
          </Col>
        </Row>

        {/* Filters */}
        <Card className="mb-6">
          <Row gutter={[16, 16]} align="middle">
            <Col xs={24} sm={6}>
              <Search
                placeholder="Search tasks..."
                allowClear
                onSearch={handleSearch}
              />
            </Col>
            <Col xs={24} sm={4}>
              <Select
                placeholder="Status"
                allowClear
                value={filters.status}
                onChange={(value) => handleFilterChange('status', value)}
                className="w-full"
              >
                <Option value="pending">Pending</Option>
                <Option value="in_progress">In Progress</Option>
                <Option value="completed">Completed</Option>
                <Option value="failed">Failed</Option>
                <Option value="cancelled">Cancelled</Option>
              </Select>
            </Col>
            <Col xs={24} sm={4}>
              <Select
                placeholder="Priority"
                allowClear
                value={filters.priority}
                onChange={(value) => handleFilterChange('priority', value)}
                className="w-full"
              >
                <Option value="low">Low</Option>
                <Option value="medium">Medium</Option>
                <Option value="high">High</Option>
                <Option value="critical">Critical</Option>
              </Select>
            </Col>
            <Col xs={24} sm={6}>
              <RangePicker
                onChange={handleDateRangeChange}
                className="w-full"
              />
            </Col>
            <Col xs={24} sm={4}>
              <Button icon={<FilterOutlined />} onClick={handleClearFilters}>
                Clear Filters
              </Button>
            </Col>
          </Row>
        </Card>
      </div>

      {/* Tasks Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={tasks}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.page,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} tasks`,
            onChange: (page, pageSize) => fetchTasks(page, filters)
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* Create Task Modal */}
      <Modal
        title="Create New Task"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateTask}
        >
          <Form.Item
            name="title"
            label="Task Title"
            rules={[{ required: true, message: 'Please enter task title' }]}
          >
            <Input placeholder="Enter task title" />
          </Form.Item>

          <Form.Item
            name="description"
            label="Description"
            rules={[{ required: true, message: 'Please enter task description' }]}
          >
            <Input.TextArea rows={4} placeholder="Enter task description" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="type"
                label="Task Type"
                rules={[{ required: true, message: 'Please select task type' }]}
              >
                <Select placeholder="Select task type">
                  <Option value="research">Research</Option>
                  <Option value="development">Development</Option>
                  <Option value="testing">Testing</Option>
                  <Option value="documentation">Documentation</Option>
                  <Option value="deployment">Deployment</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="priority"
                label="Priority"
                rules={[{ required: true, message: 'Please select priority' }]}
              >
                <Select placeholder="Select priority">
                  <Option value="low">Low</Option>
                  <Option value="medium">Medium</Option>
                  <Option value="high">High</Option>
                  <Option value="critical">Critical</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="estimatedDuration"
            label="Estimated Duration (seconds)"
          >
            <Input type="number" placeholder="Enter estimated duration" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Create Task
              </Button>
              <Button onClick={() => {
                setCreateModalVisible(false);
                form.resetFields();
              }}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Task Detail Drawer */}
      <Drawer
        title={selectedTaskDetail?.title}
        placement="right"
        onClose={() => {
          setDetailDrawerVisible(false);
          setSelectedTaskDetail(null);
        }}
        open={detailDrawerVisible}
        width={600}
      >
        {selectedTaskDetail && (
          <Space direction="vertical" size="large" className="w-full">
            <Descriptions title="Task Details" bordered column={1}>
              <Descriptions.Item label="Status">
                <Tag color={getStatusColor(selectedTaskDetail.status)}>
                  {selectedTaskDetail.status.replace('_', ' ').toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Priority">
                <Tag color={getPriorityColor(selectedTaskDetail.priority)}>
                  {selectedTaskDetail.priority.toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Type">
                {selectedTaskDetail.type}
              </Descriptions.Item>
              <Descriptions.Item label="Description">
                {selectedTaskDetail.description}
              </Descriptions.Item>
              <Descriptions.Item label="Assigned Agent">
                {selectedTaskDetail.assignedAgent?.name || 'Unassigned'}
              </Descriptions.Item>
              <Descriptions.Item label="Created">
                {dayjs(selectedTaskDetail.createdAt).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
              {selectedTaskDetail.startedAt && (
                <Descriptions.Item label="Started">
                  {dayjs(selectedTaskDetail.startedAt).format('YYYY-MM-DD HH:mm:ss')}
                </Descriptions.Item>
              )}
              {selectedTaskDetail.completedAt && (
                <Descriptions.Item label="Completed">
                  {dayjs(selectedTaskDetail.completedAt).format('YYYY-MM-DD HH:mm:ss')}
                </Descriptions.Item>
              )}
            </Descriptions>

            {selectedTaskDetail.progress > 0 && (
              <div>
                <Title level={5}>Progress</Title>
                <Progress
                  percent={selectedTaskDetail.progress}
                  strokeColor="#1890ff"
                />
              </div>
            )}

            {selectedTaskDetail.result && (
              <div>
                <Title level={5}>Result</Title>
                <Card size="small">
                  <pre className="whitespace-pre-wrap text-xs">
                    {JSON.stringify(selectedTaskDetail.result, null, 2)}
                  </pre>
                </Card>
              </div>
            )}
          </Space>
        )}
      </Drawer>
    </div>
  );
};

export default TaskManager;
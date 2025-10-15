import React from 'react';
import { Badge, Tooltip } from 'antd';
import { CheckCircleOutlined, ClockCircleOutlined, LoadingOutlined, ExclamationCircleOutlined, StopOutlined } from '@ant-design/icons';
import { AgentStatusProps } from '@/types';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const AgentStatus: React.FC<AgentStatusProps> = ({
  status,
  agentType,
  lastActivity,
  showLabel = true,
  size = 'medium'
}) => {
  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'success':
        return {
          color: 'success',
          icon: <CheckCircleOutlined />,
          text: 'Success'
        };
      case 'busy':
        return {
          color: 'processing',
          icon: <LoadingOutlined />,
          text: 'Busy'
        };
      case 'error':
        return {
          color: 'error',
          icon: <ExclamationCircleOutlined />,
          text: 'Error'
        };
      case 'offline':
        return {
          color: 'default',
          icon: <StopOutlined />,
          text: 'Offline'
        };
      case 'idle':
      default:
        return {
          color: 'default',
          icon: <ClockCircleOutlined />,
          text: 'Idle'
        };
    }
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

  const config = getStatusConfig(status);
  const lastActivityTime = dayjs(lastActivity).fromNow();

  const statusElement = (
    <div className="flex items-center gap-2">
      <Badge
        status={config.color as any}
        icon={config.icon}
        size={size === 'small' ? 'small' : 'default'}
      />
      {showLabel && (
        <div className="flex items-center gap-2">
          <span className={`text-${size === 'small' ? 'xs' : 'sm'} font-medium`}>
            {config.text}
          </span>
          <Badge
            color={getAgentTypeColor(agentType) as any}
            text={agentType}
            size={size === 'small' ? 'small' : 'default'}
          />
        </div>
      )}
    </div>
  );

  return (
    <Tooltip title={`Last activity: ${lastActivityTime}`}>
      {statusElement}
    </Tooltip>
  );
};

export default AgentStatus;
import React from 'react';
import { Progress, Tooltip, Card } from 'antd';
import { TaskProgressProps } from '@/types';
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';

dayjs.extend(duration);

const TaskProgress: React.FC<TaskProgressProps> = ({
  taskId,
  progress,
  currentStep,
  estimatedTimeRemaining,
  showPercentage = true,
  showETA = true
}) => {
  const getProgressColor = (progress: number) => {
    if (progress < 25) return '#ff4d4f';
    if (progress < 50) return '#faad14';
    if (progress < 75) return '#1890ff';
    return '#52c41a';
  };

  const formatETA = (seconds?: number) => {
    if (!seconds) return 'Unknown';

    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h`;
  };

  const progressColor = getProgressColor(progress);
  const eta = formatETA(estimatedTimeRemaining);

  return (
    <Card size="small" className="task-progress-card">
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">
            {currentStep || 'Processing...'}
          </span>
          {showPercentage && (
            <span className="text-sm text-gray-500">
              {Math.round(progress)}%
            </span>
          )}
        </div>

        <Progress
          percent={progress}
          strokeColor={progressColor}
          trailColor="#f0f0f0"
          strokeWidth={6}
          showInfo={false}
        />

        {showETA && estimatedTimeRemaining && (
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Estimated remaining time:</span>
            <Tooltip title={`${Math.round(estimatedTimeRemaining)} seconds`}>
              <span>{eta}</span>
            </Tooltip>
          </div>
        )}
      </div>
    </Card>
  );
};

export default TaskProgress;
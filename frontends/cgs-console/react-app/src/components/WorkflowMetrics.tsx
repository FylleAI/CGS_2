import React from 'react';
import { WorkflowMetrics as WorkflowMetricsType } from '../types';

interface WorkflowMetricsProps {
  metrics?: WorkflowMetricsType;
  className?: string;
}

const WorkflowMetrics: React.FC<WorkflowMetricsProps> = ({ metrics, className = '' }) => {
  if (!metrics) {
    return null;
  }

  const formatCost = (cost: number) => {
    return `$${cost.toFixed(6)}`;
  };

  const formatTokens = (tokens: number) => {
    return tokens.toLocaleString();
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) {
      return `${seconds.toFixed(1)}s`;
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
    } else {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${hours}h ${minutes}m`;
    }
  };

  const formatSuccessRate = (rate: number) => {
    return `${(rate * 100).toFixed(1)}%`;
  };

  return (
    <div className={`bg-gray-50 rounded-lg p-4 border ${className}`}>
      <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
        <span className="mr-2">📊</span>
        Workflow Metrics
      </h3>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {/* Total Cost */}
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">Total Cost</div>
          <div className="text-lg font-bold text-green-600">
            {formatCost(metrics.total_cost)}
          </div>
        </div>

        {/* Total Tokens */}
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">Total Tokens</div>
          <div className="text-lg font-bold text-blue-600">
            {formatTokens(metrics.total_tokens)}
          </div>
        </div>

        {/* Duration */}
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">Duration</div>
          <div className="text-lg font-bold text-purple-600">
            {formatDuration(metrics.duration_seconds)}
          </div>
        </div>

        {/* Agents Used */}
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">Agents Used</div>
          <div className="text-lg font-bold text-orange-600">
            {metrics.agents_used}
          </div>
        </div>

        {/* Success Rate */}
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">Success Rate</div>
          <div className={`text-lg font-bold ${
            metrics.success_rate >= 0.9 ? 'text-green-600' : 
            metrics.success_rate >= 0.7 ? 'text-yellow-600' : 'text-red-600'
          }`}>
            {formatSuccessRate(metrics.success_rate)}
          </div>
        </div>
      </div>

      {/* Cost Efficiency Indicator */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <div className="text-sm text-blue-800 mb-1">Cost Efficiency</div>
        <div className="text-xs text-blue-600">
          {metrics.total_tokens > 0 && (
            <>
              ${((metrics.total_cost / metrics.total_tokens) * 1000).toFixed(4)} per 1K tokens
              {metrics.duration_seconds > 0 && (
                <span className="ml-2">
                  • {(metrics.total_tokens / metrics.duration_seconds).toFixed(0)} tokens/sec
                </span>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default WorkflowMetrics;

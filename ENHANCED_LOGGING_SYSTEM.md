# Enhanced Logging System for CGSRef

## Overview

The CGSRef application now features a comprehensive, multi-layered logging system that provides accurate token usage tracking, cost calculation, workflow completion reporting, and system-wide monitoring. This enhanced system addresses the critical need for precise cost tracking and comprehensive analytics in AI content generation workflows.

## Key Features

### ✅ **Accurate Token Usage & Cost Tracking**
- **Real Token Usage**: Extracts actual token counts from LLM API responses instead of estimates
- **Provider-Specific Pricing**: Accurate cost calculation for OpenAI, Anthropic, and DeepSeek models
- **Model Tier Support**: Handles different pricing tiers (Basic, Standard, Premium, Reasoning)
- **Cache Cost Tracking**: Supports Anthropic's prompt caching cost calculation
- **Reasoning Token Support**: Tracks reasoning tokens for OpenAI o1 models

### ✅ **Comprehensive Workflow Reporting**
- **Complete Workflow Metrics**: Total cost, tokens, duration, agents used, success rate
- **Agent Performance Analytics**: Individual agent performance, tool usage, response times
- **Cost Breakdown**: By provider, model, and agent
- **Workflow Completion Reports**: Detailed summaries when workflows finish
- **Historical Tracking**: Maintains workflow history for analysis

### ✅ **Enhanced Agent Interaction Logging**
- **Session-Based Tracking**: Complete agent execution sessions with unique IDs
- **Detailed Interaction Types**: Agent start/end, thinking, tool calls, LLM requests/responses
- **Tool Usage Monitoring**: Comprehensive tool call tracking with timing and results
- **Error Tracking**: Detailed error logging with context and stack traces
- **Context Preservation**: Maintains workflow and task context throughout execution

### ✅ **Frontend Logging System**
- **User Interaction Tracking**: Comprehensive logging of user actions and UI events
- **API Request/Response Logging**: Detailed tracking of all API communications
- **Performance Monitoring**: Page load times, memory usage, component render metrics
- **Error Boundary Integration**: Automatic capture of frontend errors and crashes
- **Workflow Progress Tracking**: Frontend-side workflow execution monitoring

### ✅ **System-Level Monitoring**
- **Resource Monitoring**: CPU, memory, disk usage tracking
- **Application Health**: Health status, response times, error rates
- **Alert System**: Configurable thresholds for critical metrics
- **Performance Metrics**: System performance tracking and analysis
- **Uptime Monitoring**: Application uptime and availability tracking

### ✅ **REST API for Analytics**
- **Logging Endpoints**: RESTful API for accessing all logging data
- **Cost Analytics**: Detailed cost breakdown and analysis endpoints
- **Performance Reports**: Agent and system performance analytics
- **Export Functionality**: JSON and CSV export of logging data
- **Real-time Monitoring**: Live system status and health endpoints

## Architecture Components

### Backend Components

#### 1. **Cost Calculator** (`core/infrastructure/logging/cost_calculator.py`)
```python
# Accurate cost calculation with real pricing data
cost_breakdown = cost_calculator.calculate_cost(
    provider="openai",
    model="gpt-4o",
    token_usage=TokenUsage(prompt_tokens=100, completion_tokens=50)
)
```

#### 2. **Workflow Reporter** (`core/infrastructure/logging/workflow_reporter.py`)
```python
# Comprehensive workflow tracking
workflow_reporter.start_workflow_tracking(workflow_id, workflow_type)
metrics = workflow_reporter.complete_workflow_tracking(workflow_id, final_output)
```

#### 3. **System Monitor** (`core/infrastructure/logging/system_monitor.py`)
```python
# System-wide monitoring
await system_monitor.start_monitoring(interval_seconds=60)
status = system_monitor.get_current_status()
```

#### 4. **Enhanced Agent Logger** (`core/infrastructure/logging/agent_logger.py`)
```python
# Detailed agent interaction logging
session_id = agent_logger.start_agent_session(agent_id, agent_name, task_id, workflow_id)
agent_logger.log_llm_response(session_id, request_id, provider, model, response, tokens, cost, duration)
```

### Frontend Components

#### 1. **Frontend Logger** (`web/react-app/src/services/logger.ts`)
```typescript
// Comprehensive frontend logging
frontendLogger.logUserAction('click', 'GenerateButton', { workflowType: 'article' });
const workflowId = frontendLogger.logWorkflowStart('enhanced_article', parameters);
frontendLogger.logWorkflowComplete(workflowId, result, backendMetrics);
```

#### 2. **Workflow Metrics Component** (`web/react-app/src/components/WorkflowMetrics.tsx`)
```tsx
// Display workflow metrics in UI
<WorkflowMetrics metrics={result.workflowMetrics} />
```

### API Endpoints

#### Logging & Analytics Endpoints
- `GET /api/v1/logs/system/status` - Current system status
- `GET /api/v1/logs/workflows/summary` - Workflow execution summary
- `GET /api/v1/logs/workflows/{workflow_id}` - Detailed workflow report
- `GET /api/v1/logs/agents/performance` - Agent performance analytics
- `GET /api/v1/logs/costs/breakdown` - Cost breakdown analysis
- `POST /api/v1/logs/frontend` - Frontend log ingestion
- `GET /api/v1/logs/export` - Export logs in JSON/CSV format

## Usage Examples

### 1. **Tracking Workflow Costs**
```python
# Backend automatically tracks costs during workflow execution
# View costs via API:
GET /api/v1/logs/costs/breakdown?hours=24

# Response includes:
{
  "total_cost": 0.045,
  "total_tokens": 15000,
  "cost_by_provider": {
    "openai": {"cost": 0.030, "tokens": 10000},
    "anthropic": {"cost": 0.015, "tokens": 5000}
  }
}
```

### 2. **Monitoring Agent Performance**
```python
# Get agent performance metrics
GET /api/v1/logs/agents/performance?hours=24

# Response includes:
{
  "agent_performance": {
    "research_agent": {
      "total_sessions": 15,
      "avg_response_time_ms": 2500,
      "total_cost": 0.025,
      "success_rate": 0.95
    }
  }
}
```

### 3. **Frontend Workflow Tracking**
```typescript
// Track complete workflow from frontend
const workflowId = frontendLogger.logWorkflowStart('enhanced_article', {
  topic: 'AI in Healthcare',
  target_word_count: 1500
});

// API call automatically tracked
const result = await apiService.generateContent(request);

// Complete workflow tracking with backend metrics
frontendLogger.logWorkflowComplete(workflowId, result, result.workflowMetrics);
```

## Configuration

### Cost Calculator Configuration
Update pricing data in `cost_calculator.py` for new models or pricing changes:

```python
"gpt-4o": {
    "tier": ModelTier.PREMIUM,
    "prompt_cost_per_1k": 0.0025,
    "completion_cost_per_1k": 0.01,
    "supports_caching": False
}
```

### System Monitor Thresholds
Configure alert thresholds in `system_monitor.py`:

```python
self.alert_thresholds = {
    'cpu_percent': 80.0,
    'memory_percent': 85.0,
    'disk_percent': 90.0,
    'error_rate': 0.05,
    'response_time_ms': 5000.0
}
```

### Frontend Logger Settings
Enable/disable frontend logging:

```typescript
// Enable log sending to backend in production
REACT_APP_ENABLE_LOG_SENDING=true

// Control logging levels
frontendLogger.setEnabled(true);
```

## Benefits

### 1. **Cost Optimization**
- **Accurate Tracking**: Real token usage eliminates cost estimation errors
- **Provider Comparison**: Compare costs across different LLM providers
- **Model Optimization**: Identify most cost-effective models for specific tasks
- **Budget Monitoring**: Track spending in real-time with alerts

### 2. **Performance Insights**
- **Agent Efficiency**: Identify high-performing vs. struggling agents
- **Bottleneck Detection**: Find performance bottlenecks in workflows
- **Resource Optimization**: Optimize system resources based on usage patterns
- **Quality Metrics**: Track success rates and error patterns

### 3. **Operational Excellence**
- **Comprehensive Monitoring**: Full visibility into system health and performance
- **Proactive Alerts**: Early warning system for potential issues
- **Audit Trails**: Complete audit trails for compliance and debugging
- **Data-Driven Decisions**: Make informed decisions based on real usage data

### 4. **Developer Experience**
- **Rich Analytics**: Comprehensive dashboards and reports
- **Easy Integration**: Simple APIs for accessing all logging data
- **Export Capabilities**: Export data for external analysis
- **Real-time Monitoring**: Live monitoring of system status and performance

## Next Steps

The enhanced logging system provides a solid foundation for:

1. **Advanced Analytics Dashboard**: Build comprehensive dashboards for cost and performance analysis
2. **Predictive Analytics**: Use historical data to predict costs and performance
3. **Automated Optimization**: Implement automated model and provider selection based on cost/performance metrics
4. **Integration with External Tools**: Connect with business intelligence and monitoring tools
5. **Machine Learning Insights**: Apply ML to identify patterns and optimization opportunities

This enhanced logging system transforms CGSRef from a basic content generation tool into a sophisticated, enterprise-ready platform with comprehensive observability and cost management capabilities.

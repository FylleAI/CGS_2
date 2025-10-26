/**
 * Enhanced frontend logging system for comprehensive user interaction tracking.
 */

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL'
}

export enum EventType {
  USER_ACTION = 'user_action',
  API_REQUEST = 'api_request',
  API_RESPONSE = 'api_response',
  API_ERROR = 'api_error',
  NAVIGATION = 'navigation',
  FORM_INTERACTION = 'form_interaction',
  COMPONENT_RENDER = 'component_render',
  PERFORMANCE = 'performance',
  ERROR_BOUNDARY = 'error_boundary',
  WORKFLOW_START = 'workflow_start',
  WORKFLOW_COMPLETE = 'workflow_complete',
  WORKFLOW_ERROR = 'workflow_error'
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: LogLevel;
  eventType: EventType;
  message: string;
  data?: Record<string, any>;
  userId?: string;
  sessionId: string;
  url: string;
  userAgent: string;
  duration?: number;
  stackTrace?: string;
}

export interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  apiResponseTime: number;
  memoryUsage?: number;
  componentCount?: number;
}

export interface WorkflowMetrics {
  workflowId: string;
  workflowType: string;
  startTime: string;
  endTime?: string;
  duration?: number;
  success: boolean;
  totalCost?: number;
  totalTokens?: number;
  agentsUsed?: number;
  errorMessage?: string;
}

class FrontendLogger {
  private logs: LogEntry[] = [];
  private sessionId: string;
  private maxLogs: number = 1000;
  private performanceMetrics: PerformanceMetrics[] = [];
  private workflowMetrics: WorkflowMetrics[] = [];
  private isEnabled: boolean = true;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.initializeLogger();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private initializeLogger(): void {
    // Log session start
    this.info(EventType.USER_ACTION, 'Frontend session started', {
      sessionId: this.sessionId,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    });

    // Set up error handling
    window.addEventListener('error', (event) => {
      this.error(EventType.ERROR_BOUNDARY, 'Global error caught', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack
      });
    });

    // Set up unhandled promise rejection handling
    window.addEventListener('unhandledrejection', (event) => {
      this.error(EventType.ERROR_BOUNDARY, 'Unhandled promise rejection', {
        reason: event.reason,
        stack: event.reason?.stack
      });
    });

    // Set up performance monitoring
    this.setupPerformanceMonitoring();
  }

  private setupPerformanceMonitoring(): void {
    // Monitor page load performance
    window.addEventListener('load', () => {
      setTimeout(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        if (navigation) {
          const metrics: PerformanceMetrics = {
            loadTime: navigation.loadEventEnd - navigation.loadEventStart,
            renderTime: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
            apiResponseTime: 0
          };

          this.performanceMetrics.push(metrics);
          this.info(EventType.PERFORMANCE, 'Page load performance', metrics);
        }
      }, 1000);
    });

    // Monitor memory usage if available
    if ('memory' in performance) {
      setInterval(() => {
        const memory = (performance as any).memory;
        if (memory) {
          this.debug(EventType.PERFORMANCE, 'Memory usage', {
            usedJSHeapSize: memory.usedJSHeapSize,
            totalJSHeapSize: memory.totalJSHeapSize,
            jsHeapSizeLimit: memory.jsHeapSizeLimit
          });
        }
      }, 30000); // Every 30 seconds
    }
  }

  private createLogEntry(
    level: LogLevel,
    eventType: EventType,
    message: string,
    data?: Record<string, any>,
    duration?: number
  ): LogEntry {
    return {
      id: `log_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      level,
      eventType,
      message,
      data,
      sessionId: this.sessionId,
      url: window.location.href,
      userAgent: navigator.userAgent,
      duration
    };
  }

  private addLog(entry: LogEntry): void {
    if (!this.isEnabled) return;

    this.logs.push(entry);

    // Maintain max logs limit
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }

    // Console output for development
    if (process.env.NODE_ENV === 'development') {
      const consoleMethod = this.getConsoleMethod(entry.level);
      consoleMethod(
        `[${entry.level}] ${entry.eventType}: ${entry.message}`,
        entry.data || ''
      );
    }

    // Send critical errors to backend immediately
    if (entry.level === LogLevel.CRITICAL || entry.level === LogLevel.ERROR) {
      this.sendLogToBackend(entry);
    }
  }

  private getConsoleMethod(level: LogLevel): (...args: any[]) => void {
    switch (level) {
      case LogLevel.DEBUG:
        return console.debug;
      case LogLevel.INFO:
        return console.info;
      case LogLevel.WARN:
        return console.warn;
      case LogLevel.ERROR:
      case LogLevel.CRITICAL:
        return console.error;
      default:
        return console.log;
    }
  }

  private async sendLogToBackend(entry: LogEntry): Promise<void> {
    try {
      // Only send in production or when explicitly enabled
      if (process.env.NODE_ENV !== 'production' && !process.env.REACT_APP_ENABLE_LOG_SENDING) {
        return;
      }

      await fetch('/api/v1/logs/frontend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(entry),
      });
    } catch (error) {
      console.error('Failed to send log to backend:', error);
    }
  }

  // Public logging methods
  debug(eventType: EventType, message: string, data?: Record<string, any>): void {
    this.addLog(this.createLogEntry(LogLevel.DEBUG, eventType, message, data));
  }

  info(eventType: EventType, message: string, data?: Record<string, any>): void {
    this.addLog(this.createLogEntry(LogLevel.INFO, eventType, message, data));
  }

  warn(eventType: EventType, message: string, data?: Record<string, any>): void {
    this.addLog(this.createLogEntry(LogLevel.WARN, eventType, message, data));
  }

  error(eventType: EventType, message: string, data?: Record<string, any>): void {
    this.addLog(this.createLogEntry(LogLevel.ERROR, eventType, message, data));
  }

  critical(eventType: EventType, message: string, data?: Record<string, any>): void {
    this.addLog(this.createLogEntry(LogLevel.CRITICAL, eventType, message, data));
  }

  // Specialized logging methods
  logUserAction(action: string, component: string, data?: Record<string, any>): void {
    this.info(EventType.USER_ACTION, `User ${action} in ${component}`, {
      action,
      component,
      ...data
    });
  }

  logApiRequest(method: string, url: string, data?: Record<string, any>): string {
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.info(EventType.API_REQUEST, `API ${method} ${url}`, {
      requestId,
      method,
      url,
      ...data
    });
    return requestId;
  }

  logApiResponse(requestId: string, status: number, duration: number, data?: Record<string, any>): void {
    this.info(EventType.API_RESPONSE, `API response ${status}`, {
      requestId,
      status,
      duration,
      ...data
    });
  }

  logApiError(requestId: string, error: any, duration: number): void {
    this.error(EventType.API_ERROR, `API request failed`, {
      requestId,
      error: error.message || error,
      status: error.response?.status,
      duration,
      stack: error.stack
    });
  }

  logWorkflowStart(workflowType: string, parameters: Record<string, any>): string {
    const workflowId = `workflow_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const metrics: WorkflowMetrics = {
      workflowId,
      workflowType,
      startTime: new Date().toISOString(),
      success: false
    };

    this.workflowMetrics.push(metrics);

    this.info(EventType.WORKFLOW_START, `Workflow started: ${workflowType}`, {
      workflowId,
      workflowType,
      parameters
    });

    return workflowId;
  }

  logWorkflowComplete(workflowId: string, result: any, backendMetrics?: any): void {
    const metrics = this.workflowMetrics.find(m => m.workflowId === workflowId);
    if (metrics) {
      metrics.endTime = new Date().toISOString();
      metrics.duration = new Date(metrics.endTime).getTime() - new Date(metrics.startTime).getTime();
      metrics.success = true;
      
      if (backendMetrics) {
        metrics.totalCost = backendMetrics.total_cost;
        metrics.totalTokens = backendMetrics.total_tokens;
        metrics.agentsUsed = backendMetrics.agents_used;
      }
    }

    this.info(EventType.WORKFLOW_COMPLETE, `Workflow completed: ${workflowId}`, {
      workflowId,
      result,
      metrics: backendMetrics
    });
  }

  logWorkflowError(workflowId: string, error: any): void {
    const metrics = this.workflowMetrics.find(m => m.workflowId === workflowId);
    if (metrics) {
      metrics.endTime = new Date().toISOString();
      metrics.duration = new Date(metrics.endTime).getTime() - new Date(metrics.startTime).getTime();
      metrics.success = false;
      metrics.errorMessage = error.message || error;
    }

    this.error(EventType.WORKFLOW_ERROR, `Workflow failed: ${workflowId}`, {
      workflowId,
      error: error.message || error,
      stack: error.stack
    });
  }

  // Utility methods
  getLogs(level?: LogLevel, eventType?: EventType): LogEntry[] {
    return this.logs.filter(log => {
      if (level && log.level !== level) return false;
      if (eventType && log.eventType !== eventType) return false;
      return true;
    });
  }

  getWorkflowMetrics(): WorkflowMetrics[] {
    return this.workflowMetrics;
  }

  getPerformanceMetrics(): PerformanceMetrics[] {
    return this.performanceMetrics;
  }

  exportLogs(): string {
    return JSON.stringify({
      sessionId: this.sessionId,
      logs: this.logs,
      workflowMetrics: this.workflowMetrics,
      performanceMetrics: this.performanceMetrics,
      exportedAt: new Date().toISOString()
    }, null, 2);
  }

  clearLogs(): void {
    this.logs = [];
    this.workflowMetrics = [];
    this.performanceMetrics = [];
  }

  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }
}

// Create and export singleton instance
export const frontendLogger = new FrontendLogger();
export default frontendLogger;

"""
System-level monitoring and health tracking for CGSRef application.
"""

import logging
import psutil
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    active_connections: int = 0
    process_count: int = 0
    load_average: Optional[float] = None


@dataclass
class ApplicationHealth:
    """Application health status."""
    timestamp: datetime
    status: str  # healthy, degraded, unhealthy
    response_time_ms: float
    error_rate: float
    active_workflows: int
    total_requests: int
    failed_requests: int
    uptime_seconds: float
    version: str = "1.0.0"


@dataclass
class ErrorSummary:
    """Error tracking summary."""
    timestamp: datetime
    error_count_1h: int
    error_count_24h: int
    critical_errors: int
    most_common_errors: List[Dict[str, Any]]
    error_rate_trend: str  # increasing, stable, decreasing


class SystemMonitor:
    """
    Comprehensive system monitoring for application health and performance.
    
    This monitor tracks system resources, application health, error rates,
    and provides alerts for critical issues.
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.start_time = datetime.utcnow()
        self.metrics_history: List[SystemMetrics] = []
        self.health_history: List[ApplicationHealth] = []
        self.error_history: List[Dict[str, Any]] = []
        
        self.monitoring_enabled = True
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'error_rate': 0.05,  # 5%
            'response_time_ms': 5000.0
        }
        
        logger.info("🔍 System monitor initialized")
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous system monitoring."""
        logger.info(f"📊 Starting system monitoring (interval: {interval_seconds}s)")
        
        while self.monitoring_enabled:
            try:
                # Collect system metrics
                metrics = self.collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Collect application health
                health = await self.collect_application_health()
                self.health_history.append(health)
                
                # Check for alerts
                await self.check_alerts(metrics, health)
                
                # Cleanup old data (keep last 24 hours)
                self.cleanup_old_data()
                
                # Save metrics to file
                await self.save_metrics()
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"❌ Error in system monitoring: {e}")
                await asyncio.sleep(interval_seconds)
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            
            # Process count
            process_count = len(psutil.pids())
            
            # Load average (Unix-like systems)
            load_average = None
            try:
                load_average = psutil.getloadavg()[0]
            except (AttributeError, OSError):
                pass  # Not available on Windows
            
            # Network connections
            active_connections = len(psutil.net_connections())
            
            metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_gb=memory_used_gb,
                memory_total_gb=memory_total_gb,
                disk_percent=disk_percent,
                disk_used_gb=disk_used_gb,
                disk_total_gb=disk_total_gb,
                active_connections=active_connections,
                process_count=process_count,
                load_average=load_average
            )
            
            logger.debug(
                f"📊 System metrics: CPU {cpu_percent:.1f}%, "
                f"Memory {memory_percent:.1f}%, "
                f"Disk {disk_percent:.1f}%"
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_gb=0.0,
                memory_total_gb=0.0,
                disk_percent=0.0,
                disk_used_gb=0.0,
                disk_total_gb=0.0
            )
    
    async def collect_application_health(self) -> ApplicationHealth:
        """Collect application health metrics."""
        try:
            # Calculate uptime
            uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
            
            # Get error rate from recent history
            recent_errors = [
                e for e in self.error_history
                if datetime.fromisoformat(e['timestamp']) > datetime.utcnow() - timedelta(hours=1)
            ]
            
            # Simulate request metrics (in real implementation, get from request tracker)
            total_requests = len(self.health_history) * 10  # Rough estimate
            failed_requests = len(recent_errors)
            error_rate = failed_requests / max(total_requests, 1)
            
            # Determine health status
            status = "healthy"
            if error_rate > 0.1 or (self.metrics_history and self.metrics_history[-1].cpu_percent > 90):
                status = "unhealthy"
            elif error_rate > 0.05 or (self.metrics_history and self.metrics_history[-1].cpu_percent > 80):
                status = "degraded"
            
            # Simulate response time (in real implementation, track actual response times)
            response_time_ms = 150.0 + (error_rate * 1000)
            
            health = ApplicationHealth(
                timestamp=datetime.utcnow(),
                status=status,
                response_time_ms=response_time_ms,
                error_rate=error_rate,
                active_workflows=0,  # Would be tracked by workflow reporter
                total_requests=total_requests,
                failed_requests=failed_requests,
                uptime_seconds=uptime_seconds
            )
            
            logger.debug(
                f"💚 Application health: {status}, "
                f"Error rate: {error_rate:.3f}, "
                f"Response time: {response_time_ms:.1f}ms"
            )
            
            return health
            
        except Exception as e:
            logger.error(f"❌ Error collecting application health: {e}")
            return ApplicationHealth(
                timestamp=datetime.utcnow(),
                status="unknown",
                response_time_ms=0.0,
                error_rate=0.0,
                active_workflows=0,
                total_requests=0,
                failed_requests=0,
                uptime_seconds=0.0
            )
    
    async def check_alerts(self, metrics: SystemMetrics, health: ApplicationHealth):
        """Check for alert conditions and log warnings."""
        alerts = []
        
        # CPU alert
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        
        # Memory alert
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append(f"High memory usage: {metrics.memory_percent:.1f}%")
        
        # Disk alert
        if metrics.disk_percent > self.alert_thresholds['disk_percent']:
            alerts.append(f"High disk usage: {metrics.disk_percent:.1f}%")
        
        # Error rate alert
        if health.error_rate > self.alert_thresholds['error_rate']:
            alerts.append(f"High error rate: {health.error_rate:.3f}")
        
        # Response time alert
        if health.response_time_ms > self.alert_thresholds['response_time_ms']:
            alerts.append(f"High response time: {health.response_time_ms:.1f}ms")
        
        # Application health alert
        if health.status in ['degraded', 'unhealthy']:
            alerts.append(f"Application health: {health.status}")
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"🚨 ALERT: {alert}")
    
    def log_error(self, error_type: str, message: str, details: Dict[str, Any] = None):
        """Log an application error for tracking."""
        error_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': error_type,
            'message': message,
            'details': details or {}
        }
        
        self.error_history.append(error_entry)
        
        # Keep only recent errors (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.error_history = [
            e for e in self.error_history
            if datetime.fromisoformat(e['timestamp']) > cutoff
        ]
    
    def cleanup_old_data(self):
        """Remove old monitoring data to prevent memory buildup."""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        self.metrics_history = [
            m for m in self.metrics_history
            if m.timestamp > cutoff
        ]
        
        self.health_history = [
            h for h in self.health_history
            if h.timestamp > cutoff
        ]
    
    async def save_metrics(self):
        """Save current metrics to file."""
        try:
            metrics_file = self.log_dir / f"system_metrics_{datetime.utcnow().strftime('%Y%m%d')}.json"
            
            data = {
                'last_updated': datetime.utcnow().isoformat(),
                'latest_metrics': asdict(self.metrics_history[-1]) if self.metrics_history else None,
                'latest_health': asdict(self.health_history[-1]) if self.health_history else None,
                'recent_errors': self.error_history[-10:],  # Last 10 errors
                'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds()
            }
            
            with open(metrics_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"❌ Error saving metrics: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current system status summary."""
        latest_metrics = self.metrics_history[-1] if self.metrics_history else None
        latest_health = self.health_history[-1] if self.health_history else None
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
            'system_metrics': asdict(latest_metrics) if latest_metrics else None,
            'application_health': asdict(latest_health) if latest_health else None,
            'recent_errors': len(self.error_history),
            'monitoring_enabled': self.monitoring_enabled
        }
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring_enabled = False
        logger.info("🛑 System monitoring stopped")


# Global system monitor instance
system_monitor = SystemMonitor()

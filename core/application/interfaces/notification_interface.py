"""Notification interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum


class NotificationType(Enum):
    """Types of notifications."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationInterface(ABC):
    """
    Abstract interface for notification services.

    This interface defines the contract for sending notifications
    about system events, progress updates, and alerts.
    """

    @abstractmethod
    async def send_notification(
        self,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        recipient: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send a notification.

        Args:
            message: The notification message
            notification_type: Type of notification
            recipient: Optional recipient identifier
            metadata: Additional notification metadata

        Returns:
            True if notification was sent successfully
        """
        pass

    @abstractmethod
    async def send_progress_update(
        self,
        task_id: str,
        progress: float,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send a progress update notification.

        Args:
            task_id: Identifier for the task
            progress: Progress percentage (0.0 to 1.0)
            message: Progress message
            metadata: Additional metadata

        Returns:
            True if update was sent successfully
        """
        pass

    @abstractmethod
    async def send_completion_notification(
        self,
        task_id: str,
        success: bool,
        result_summary: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send a task completion notification.

        Args:
            task_id: Identifier for the completed task
            success: Whether the task completed successfully
            result_summary: Summary of the result
            metadata: Additional metadata

        Returns:
            True if notification was sent successfully
        """
        pass

import pytest
from unittest.mock import Mock

from core.infrastructure.logging.agent_logger import AgentLogger


def test_agent_logger_thinking_saved_to_tracker():
    tracker = Mock()
    logger = AgentLogger(tracker=tracker, run_id="run1")
    session_id = logger.start_agent_session("a1", "agent", "t1", "run1", "desc")
    logger.log_agent_thinking(session_id, "thought")
    tracker.add_log.assert_called_once_with("run1", "THINK", "thought", "agent")

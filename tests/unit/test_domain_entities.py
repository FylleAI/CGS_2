"""Unit tests for domain entities."""

import pytest
from uuid import uuid4
from datetime import datetime

from core.domain.entities.agent import Agent, AgentRole
from core.domain.entities.content import (
    Content,
    ContentType,
    ContentFormat,
    ContentStatus,
)
from core.domain.entities.task import Task, TaskStatus, TaskPriority, TaskResult
from core.domain.entities.workflow import Workflow, WorkflowType, WorkflowStatus
from core.domain.value_objects.provider_config import ProviderConfig, LLMProvider


class TestAgent:
    """Test Agent entity."""

    def test_agent_creation(self):
        """Test agent creation with default values."""
        agent = Agent(name="test_agent", role=AgentRole.COPYWRITER)

        assert agent.name == "test_agent"
        assert agent.role == AgentRole.COPYWRITER
        assert agent.is_active is True
        assert len(agent.tools) == 0
        assert agent.goal != ""  # Should have default goal

    def test_agent_with_tools(self):
        """Test agent with tools."""
        agent = Agent(
            name="test_agent",
            role=AgentRole.RESEARCHER,
            tools=["web_search", "rag_tool"],
        )

        assert agent.can_use_tool("web_search")
        assert agent.can_use_tool("rag_tool")
        assert not agent.can_use_tool("unknown_tool")

    def test_add_remove_tools(self):
        """Test adding and removing tools."""
        agent = Agent(name="test", role=AgentRole.EDITOR)

        agent.add_tool("new_tool")
        assert agent.can_use_tool("new_tool")

        agent.remove_tool("new_tool")
        assert not agent.can_use_tool("new_tool")

    def test_agent_serialization(self):
        """Test agent to/from dict conversion."""
        original = Agent(
            name="test_agent",
            role=AgentRole.COPYWRITER,
            goal="Test goal",
            tools=["tool1", "tool2"],
        )

        data = original.to_dict()
        restored = Agent.from_dict(data)

        assert restored.name == original.name
        assert restored.role == original.role
        assert restored.goal == original.goal
        assert restored.tools == original.tools


class TestContent:
    """Test Content entity."""

    def test_content_creation(self):
        """Test content creation."""
        content = Content(
            title="Test Article",
            body="This is test content.",
            content_type=ContentType.ARTICLE,
        )

        assert content.title == "Test Article"
        assert content.content_type == ContentType.ARTICLE
        assert content.status == ContentStatus.DRAFT
        assert content.version == 1

    def test_content_metrics_calculation(self):
        """Test automatic metrics calculation."""
        content = Content(
            title="Test", body="This is a test article with multiple words for testing."
        )

        assert content.metrics.word_count == 10
        assert content.metrics.character_count > 0
        assert content.metrics.reading_time_minutes > 0

    def test_content_status_transitions(self):
        """Test valid status transitions."""
        content = Content(title="Test", body="Test content")

        # Draft -> Review
        content.change_status(ContentStatus.REVIEW)
        assert content.status == ContentStatus.REVIEW

        # Review -> Approved
        content.change_status(ContentStatus.APPROVED)
        assert content.status == ContentStatus.APPROVED

        # Approved -> Published
        content.change_status(ContentStatus.PUBLISHED)
        assert content.status == ContentStatus.PUBLISHED
        assert content.published_at is not None

    def test_invalid_status_transition(self):
        """Test invalid status transitions."""
        content = Content(title="Test", body="Test content")

        # Cannot go directly from Draft to Published
        with pytest.raises(ValueError):
            content.change_status(ContentStatus.PUBLISHED)

    def test_content_update(self):
        """Test content update."""
        content = Content(title="Original", body="Original content")
        original_version = content.version
        original_updated = content.updated_at

        content.update_content(title="Updated", body="Updated content")

        assert content.title == "Updated"
        assert content.body == "Updated content"
        assert content.version == original_version + 1
        assert content.updated_at > original_updated

    def test_content_tags(self):
        """Test content tagging."""
        content = Content(title="Test", body="Test content")

        content.add_tag("python")
        content.add_tag("testing")

        assert "python" in content.tags
        assert "testing" in content.tags

        content.remove_tag("python")
        assert "python" not in content.tags
        assert "testing" in content.tags

    def test_content_excerpt(self):
        """Test content excerpt generation."""
        long_content = "This is a very long piece of content. " * 20
        content = Content(title="Test", body=long_content)

        excerpt = content.get_excerpt(100)
        assert len(excerpt) <= 103  # 100 + "..."
        assert excerpt.endswith("...")

    def test_content_excerpt_edge_cases(self):
        """Test content excerpt edge cases."""
        # Test short content (should not add ...)
        short_content = "Short content."
        content = Content(title="Test", body=short_content)
        excerpt = content.get_excerpt(100)
        assert excerpt == short_content
        assert not excerpt.endswith("...")

        # Test content that ends exactly at sentence boundary
        sentence_content = "First sentence. Second sentence. Third sentence."
        content = Content(title="Test", body=sentence_content)
        excerpt = content.get_excerpt(30)  # Should break at first sentence
        assert excerpt.endswith("...")

        # Test content without sentence boundaries
        no_sentence_content = (
            "This is content without proper sentence boundaries and spaces"
        )
        content = Content(title="Test", body=no_sentence_content)
        excerpt = content.get_excerpt(20)
        assert excerpt.endswith("...")
        assert len(excerpt) <= 23  # 20 + "..."


class TestTask:
    """Test Task entity."""

    def test_task_creation(self):
        """Test task creation."""
        task = Task(
            name="test_task",
            description="Test task description",
            expected_output="Test output",
        )

        assert task.name == "test_task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM

    def test_task_dependencies(self):
        """Test task dependencies."""
        task1 = Task(name="task1", description="First task")
        task2 = Task(name="task2", description="Second task")

        task2.add_dependency(task1.id)

        assert task1.id in task2.dependencies
        assert not task2.can_start([])  # task1 not completed
        assert task2.can_start([task1.id])  # task1 completed

    def test_task_execution_flow(self):
        """Test task execution flow."""
        task = Task(name="test", description="Test task")

        # Start task
        task.start()
        assert task.status == TaskStatus.RUNNING
        assert task.started_at is not None

        # Complete task
        result = TaskResult(output="Task completed successfully")
        task.complete(result)
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert task.result.output == "Task completed successfully"

    def test_task_failure(self):
        """Test task failure."""
        task = Task(name="test", description="Test task")
        task.start()

        task.fail("Something went wrong")
        assert task.status == TaskStatus.FAILED
        assert task.result.error_message == "Something went wrong"

    def test_task_serialization(self):
        """Test task serialization."""
        original = Task(
            name="test_task",
            description="Test description",
            expected_output="Test output",
            priority=TaskPriority.HIGH,
        )

        data = original.to_dict()
        restored = Task.from_dict(data)

        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.priority == original.priority


class TestWorkflow:
    """Test Workflow entity."""

    def test_workflow_creation(self):
        """Test workflow creation."""
        workflow = Workflow(name="test_workflow", workflow_type=WorkflowType.BASIC)

        assert workflow.name == "test_workflow"
        assert workflow.workflow_type == WorkflowType.BASIC
        assert workflow.status == WorkflowStatus.DRAFT

    def test_workflow_with_tasks(self):
        """Test workflow with tasks."""
        workflow = Workflow(name="test", workflow_type=WorkflowType.BASIC)

        task1 = Task(name="task1", description="First task")
        task2 = Task(name="task2", description="Second task")
        task2.add_dependency(task1.id)

        workflow.add_task(task1)
        workflow.add_task(task2)

        assert len(workflow.tasks) == 2
        assert workflow.get_task_by_id(task1.id) == task1

    def test_workflow_ready_tasks(self):
        """Test getting ready tasks."""
        workflow = Workflow(name="test", workflow_type=WorkflowType.BASIC)

        task1 = Task(name="task1", description="First task")
        task2 = Task(name="task2", description="Second task")
        task2.add_dependency(task1.id)

        workflow.add_task(task1)
        workflow.add_task(task2)

        ready_tasks = workflow.get_ready_tasks()
        assert len(ready_tasks) == 1
        assert ready_tasks[0] == task1  # Only task1 has no dependencies

    def test_workflow_validation(self):
        """Test workflow validation."""
        workflow = Workflow(name="test", workflow_type=WorkflowType.BASIC)

        # Empty workflow should have errors
        errors = workflow.validate()
        assert len(errors) > 0

        # Add a task
        task = Task(name="task1", description="Test task")
        workflow.add_task(task)

        errors = workflow.validate()
        assert len(errors) == 0  # Should be valid now

    def test_workflow_circular_dependency_detection(self):
        """Test circular dependency detection."""
        workflow = Workflow(name="test", workflow_type=WorkflowType.BASIC)

        task1 = Task(name="task1", description="First task")
        task2 = Task(name="task2", description="Second task")

        # Create circular dependency
        task1.add_dependency(task2.id)
        task2.add_dependency(task1.id)

        workflow.add_task(task1)
        workflow.add_task(task2)

        errors = workflow.validate()
        assert any("circular" in error.lower() for error in errors)

    def test_workflow_progress(self):
        """Test workflow progress calculation."""
        workflow = Workflow(name="test", workflow_type=WorkflowType.BASIC)

        task1 = Task(name="task1", description="First task")
        task2 = Task(name="task2", description="Second task")

        workflow.add_task(task1)
        workflow.add_task(task2)

        assert workflow.get_progress() == 0.0

        # Complete one task
        task1.start()
        task1.complete(TaskResult(output="Done"))

        assert workflow.get_progress() == 0.5

        # Complete second task
        task2.start()
        task2.complete(TaskResult(output="Done"))

        assert workflow.get_progress() == 1.0
        assert workflow.is_completed()

"""Unit tests for PlanAgent."""

import pytest
from src.intelligence.sdd.plan_agent import PlanAgent
from src.intelligence.sdd.context import SDDContext
from src.intelligence.sdd.data_models import Plan, Task, Artifact


class TestPlanAgent:
    """Test suite for PlanAgent."""

    def test_agent_name(self):
        """Test agent name property."""
        agent = PlanAgent()
        assert agent.name == "plan"

    def test_can_handle_with_spec_artifact(self):
        """Test can_handle returns True when spec artifact exists."""
        context = SDDContext("create plan")
        # Add spec artifact
        context.add_artifact("spec", "# Spec\nRequirements...", {"source": "test"})
        agent = PlanAgent()

        assert agent.can_handle(context) is True

    def test_can_handle_without_spec(self):
        """Test can_handle returns False without spec artifact."""
        context = SDDContext("create plan")
        agent = PlanAgent()

        assert agent.can_handle(context) is False

    def test_can_handle_needs_clarification(self):
        """Test can_handle returns True for needs_clarification state."""
        context = SDDContext("create plan")
        context.workflow_state = "needs_clarification"
        agent = PlanAgent()

        assert agent.can_handle(context) is True

    def test_execute_generates_plan(self):
        """Test execute generates plan from spec."""
        context = SDDContext("create plan")
        context.add_artifact("spec", "# User Auth\nFR-001: Login\nFR-002: Registration", {"source": "test"})
        agent = PlanAgent()

        plan = agent.execute(context)

        assert isinstance(plan, Plan)
        assert plan.title
        assert isinstance(plan.tasks, list)

    def test_execute_stores_artifact(self):
        """Test execute stores plan artifact."""
        context = SDDContext("create plan")
        context.add_artifact("spec", "# System\nRequirements", {"source": "test"})
        agent = PlanAgent()

        agent.execute(context)

        assert "plan" in context.artifacts
        artifact = context.get_latest_artifact("plan")
        assert artifact is not None

    def test_execute_raises_without_spec(self):
        """Test execute raises error without spec."""
        context = SDDContext("create plan")
        agent = PlanAgent()

        with pytest.raises(ValueError, match="Specification artifact not found"):
            agent.execute(context)

    def test_generate_plan_title(self):
        """Test plan title generation."""
        agent = PlanAgent()

        title = agent._generate_plan_title("create user authentication with JWT")

        assert "Implementation Plan:" in title
        assert len(title) > 0

    def test_determine_architecture_rest(self):
        """Test architecture detection for REST API."""
        agent = PlanAgent()

        arch = agent._determine_architecture("REST API with endpoints", [])

        assert arch == "REST API"

    def test_determine_architecture_database(self):
        """Test architecture detection for database."""
        agent = PlanAgent()

        arch = agent._determine_architecture("database schema with PostgreSQL", [])

        assert arch == "Database-driven"

    def test_determine_architecture_ui(self):
        """Test architecture detection for UI."""
        agent = PlanAgent()

        arch = agent._determine_architecture("UI with React frontend", [])

        assert arch == "Web application"

    def test_determine_architecture_default(self):
        """Test default architecture."""
        agent = PlanAgent()

        arch = agent._determine_architecture("generic system", [])

        assert arch == "Modular service"

    def test_generate_tasks_creates_tasks(self):
        """Test task generation from spec."""
        context = SDDContext("create plan")
        agent = PlanAgent()

        tasks = agent._generate_tasks(context, "FR-001: User login\nFR-002: User registration")

        assert isinstance(tasks, list)
        assert len(tasks) > 0
        assert all(isinstance(t, Task) for t in tasks)

    def test_generate_tasks_includes_architecture(self):
        """Test task generation includes architecture task."""
        context = SDDContext("create plan")
        agent = PlanAgent()

        tasks = agent._generate_tasks(context, "REST API with authentication")

        # Should include ARCH task
        assert any(t.id == "ARCH" for t in tasks)

    def test_generate_tasks_includes_documentation(self):
        """Test task generation includes documentation task."""
        context = SDDContext("create plan")
        agent = PlanAgent()

        tasks = agent._generate_tasks(context, "create system")

        # Should include DOC task
        assert any(t.id == "DOC" for t in tasks)

    def test_execute_updates_workflow(self):
        """Test execute logs events."""
        context = SDDContext("create plan")
        context.add_artifact("spec", "# Spec\nRequirements", {"source": "test"})
        agent = PlanAgent()

        agent.execute(context)

        # Should have logged plan generation
        assert any("sdd_plan_generated" in e for e in context.events)

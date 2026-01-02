"""Unit tests for SpecAgent."""

import pytest
from src.intelligence.sdd.spec_agent import SpecAgent
from src.intelligence.sdd.context import SDDContext
from src.intelligence.sdd.data_models import Intent, IntentType, Spec


class TestSpecAgent:
    """Test suite for SpecAgent."""

    def test_agent_name(self):
        """Test agent name property."""
        agent = SpecAgent()
        assert agent.name == "spec"

    def test_can_handle_with_specify_intent(self):
        """Test can_handle returns True with SPECIFY intent."""
        context = SDDContext("create spec")
        context.intent = Intent(
            type=IntentType.SPECIFY,
            description="create a spec for user authentication"
        )
        agent = SpecAgent()

        assert agent.can_handle(context) is True

    def test_can_handle_with_plan_intent(self):
        """Test can_handle returns False with PLAN intent."""
        context = SDDContext("create plan")
        context.intent = Intent(
            type=IntentType.PLAN,
            description="create a plan"
        )
        agent = SpecAgent()

        assert agent.can_handle(context) is False

    def test_can_handle_with_clarification_state(self):
        """Test can_handle returns False when waiting for clarification."""
        context = SDDContext("create spec")
        context.workflow_state = "clarification"
        context.intent = Intent(
            type=IntentType.SPECIFY,
            description="create spec"
        )
        agent = SpecAgent()

        assert agent.can_handle(context) is False

    def test_execute_generates_spec(self):
        """Test execute generates specification."""
        context = SDDContext("create spec")
        context.intent = Intent(
            type=IntentType.SPECIFY,
            description="create a user authentication system with login and registration"
        )
        agent = SpecAgent()

        spec = agent.execute(context)

        assert isinstance(spec, Spec)
        assert spec.title
        assert spec.description
        assert context.workflow_state == "specification"

    def test_execute_stores_artifact(self):
        """Test execute stores spec artifact in context."""
        context = SDDContext("create spec")
        context.intent = Intent(
            type=IntentType.SPECIFY,
            description="create a REST API"
        )
        agent = SpecAgent()

        agent.execute(context)

        assert "spec" in context.artifacts
        artifact = context.get_latest_artifact("spec")
        assert artifact is not None
        assert artifact.artifact_type == "spec"

    def test_generate_title(self):
        """Test title generation from input."""
        agent = SpecAgent()

        title = agent._generate_title("create a user authentication system with JWT")

        assert "Create A User Authentication System With Jwt" in title
        assert len(title) > 0

    def test_generate_spec_includes_sections(self):
        """Test generated spec includes required sections."""
        context = SDDContext("create spec")
        context.intent = Intent(
            type=IntentType.SPECIFY,
            description="create a todo app"
        )
        agent = SpecAgent()

        spec_content = agent._generate_spec(
            context,
            "create a todo app with task management",
            agent._load_spec_template()
        )

        assert "# Feature Specification:" in spec_content
        assert "## Overview" in spec_content
        assert "## Requirements" in spec_content
        assert "## Acceptance Criteria" in spec_content
        assert "## Architecture Notes" in spec_content

    def test_extract_requirements_from_template(self):
        """Test requirement extraction from template."""
        agent = SpecAgent()
        template = agent._load_spec_template()

        requirements = agent._extract_requirements("create REST API", template)

        # Should extract requirements from template
        assert isinstance(requirements, list)

    def test_parse_template_sections(self):
        """Test template section parsing."""
        agent = SpecAgent()
        template = agent._load_spec_template()

        sections = agent._parse_template_sections(template)

        assert isinstance(sections, list)
        # Should find common sections
        assert any("Overview" in s or "Requirements" in s for s in sections)

    def test_execute_with_user_input(self):
        """Test execute with user input override."""
        context = SDDContext("create spec")
        context.intent = Intent(
            type=IntentType.SPECIFY,
            description="original"
        )
        agent = SpecAgent()

        spec = agent.execute(context, user_input="create authentication system")

        assert spec.description == "create authentication system"

    def test_execute_updates_workflow_state(self):
        """Test execute transitions workflow state."""
        context = SDDContext("create spec")
        context.intent = Intent(
            type=IntentType.SPECIFY,
            description="create system"
        )
        context.workflow_state = "initialized"
        agent = SpecAgent()

        agent.execute(context)

        assert context.workflow_state == "specification"

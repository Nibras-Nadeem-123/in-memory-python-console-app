"""Unit tests for GuideAgent."""

import pytest
from src.intelligence.sdd.guide_agent import GuideAgent
from src.intelligence.sdd.context import SDDContext
from src.intelligence.sdd.data_models import Guide


class TestGuideAgent:
    """Test suite for GuideAgent."""

    def test_agent_name(self):
        """Test agent name property."""
        agent = GuideAgent()
        assert agent.name == "guide"

    def test_can_handle_with_plan_and_spec(self):
        """Test can_handle returns True with plan and spec artifacts."""
        context = SDDContext("create guide")
        context.add_artifact("spec", "# Spec", {"source": "test"})
        context.add_artifact("plan", "# Plan", {"source": "test"})
        agent = GuideAgent()

        assert agent.can_handle(context) is True

    def test_can_handle_without_plan(self):
        """Test can_handle returns False without plan."""
        context = SDDContext("create guide")
        context.add_artifact("spec", "# Spec", {"source": "test"})
        agent = GuideAgent()

        assert agent.can_handle(context) is False

    def test_can_handle_without_spec(self):
        """Test can_handle returns False without spec."""
        context = SDDContext("create guide")
        context.add_artifact("plan", "# Plan", {"source": "test"})
        agent = GuideAgent()

        assert agent.can_handle(context) is False

    def test_execute_generates_guide(self):
        """Test execute generates guide."""
        context = SDDContext("create guide")
        context.add_artifact("spec", "# User Auth Spec", {"source": "test"})
        context.add_artifact("plan", "# Implementation Plan", {"source": "test"})
        agent = GuideAgent()

        guide = agent.execute(context)

        assert isinstance(guide, Guide)
        assert guide.title
        assert guide.getting_started
        assert guide.implementation_order
        assert guide.code_patterns
        assert guide.testing_recommendations

    def test_execute_stores_artifact(self):
        """Test execute stores guide artifact."""
        context = SDDContext("create guide")
        context.add_artifact("spec", "# Spec", {"source": "test"})
        context.add_artifact("plan", "# Plan", {"source": "test"})
        agent = GuideAgent()

        agent.execute(context)

        assert "guide" in context.artifacts
        artifact = context.get_latest_artifact("guide")
        assert artifact is not None

    def test_execute_raises_without_plan(self):
        """Test execute raises error without plan."""
        context = SDDContext("create guide")
        agent = GuideAgent()

        with pytest.raises(ValueError, match="Plan artifact required"):
            agent.execute(context)

    def test_generate_guide_title(self):
        """Test guide title generation."""
        agent = GuideAgent()

        title = agent._generate_guide_title("User Authentication System")

        assert "Implementation Guide:" in title
        assert "User" in title

    def test_get_started_section(self):
        """Test getting started section generation."""
        agent = GuideAgent()

        section = agent._get_started_section("REST API")

        assert "Review" in section
        assert "specification" in section
        assert isinstance(section, str)
        assert len(section) > 0

    def test_determine_implementation_order_database(self):
        """Test implementation order for database system."""
        agent = GuideAgent()

        order = agent._determine_implementation_order("database with PostgreSQL")

        assert "Data layer" in order or "models" in order

    def test_determine_implementation_order_api(self):
        """Test implementation order for API system."""
        agent = GuideAgent()

        order = agent._determine_implementation_order("REST API with endpoints")

        assert "API" in order

    def test_determine_implementation_order_default(self):
        """Test default implementation order."""
        agent = GuideAgent()

        order = agent._determine_implementation_order("generic system")

        assert "Models" in order or "Services" in order

    def test_generate_code_patterns(self):
        """Test code pattern generation."""
        agent = GuideAgent()

        patterns = agent._generate_code_patterns("Python REST API")

        assert isinstance(patterns, str)
        assert len(patterns) > 0
        # Should include best practices
        assert "dataclass" in patterns or "REST" in patterns

    def test_generate_testing_recommendations(self):
        """Test testing recommendation generation."""
        agent = GuideAgent()

        recommendations = agent._generate_testing_recommendations("system")

        assert isinstance(recommendations, str)
        assert "test" in recommendations.lower()
        assert "coverage" in recommendations.lower()

    def test_generate_guide_includes_sections(self):
        """Test generated guide includes all sections."""
        context = SDDContext("create guide")
        agent = GuideAgent()

        guide_content = agent._generate_guide(context, "User Authentication")

        assert "# Implementation Guide:" in guide_content
        assert "## Getting Started" in guide_content
        assert "## Implementation Order" in guide_content
        assert "## Code Patterns" in guide_content
        assert "## Testing Recommendations" in guide_content

    def test_execute_logs_events(self):
        """Test execute logs events."""
        context = SDDContext("create guide")
        context.add_artifact("spec", "# Spec", {"source": "test"})
        context.add_artifact("plan", "# Plan", {"source": "test"})
        agent = GuideAgent()

        agent.execute(context)

        # Should have logged guide generation
        assert any("sdd_guide_generated" in e for e in context.events)

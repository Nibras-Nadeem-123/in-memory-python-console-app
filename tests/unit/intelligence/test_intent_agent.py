"""Test Intent Agent for Spec-Driven Development system."""
import pytest
from src.intelligence.sdd.intent_agent import IntentAgent
from src.intelligence.sdd.data_models import Intent, IntentType
from src.intelligence.sdd.context import SDDContext


class TestIntentAgent:
    """Tests for Intent parsing agent."""

    def test_can_handle_no_intent(self):
        """Agent should NOT handle context with no intent."""
        context = SDDContext(execution_id="test_no_intent")
        assert not IntentAgent().can_handle(context)

    def test_can_handle_with_intent(self):
        """Agent should handle context with parsed intent."""
        context = SDDContext(execution_id="test_with_intent")
        context.intent = Intent(type=IntentType.SPECIFY, description="Create a spec for todo app")

        assert IntentAgent().can_handle(context)

    def test_can_handle_waiting_for_clarification(self):
        """Agent should handle context waiting for clarification."""
        context = SDDContext(execution_id="test_clarification")
        context.workflow_state = "needs_clarification"

        assert IntentAgent().can_handle(context)

    def test_intent_type_classification(self):
        """Test intent type classification logic."""
        # Clarify intent type
        assert IntentAgent()._classify_intent_type("clarify the requirements") == IntentType.CLARIFY

        # Spec intent type
        assert IntentAgent()._classify_intent_type("create a spec") == IntentType.SPECIFY

        # Plan intent type
        assert IntentAgent()._classify_intent_type("create implementation plan") == IntentType.PLAN

        # Guide intent type
        assert IntentAgent()._classify_intent_type("help me implement this") == IntentType.GUIDE

        # Default
        assert IntentAgent()._classify_intent_type("I want to build something") == IntentType.SPECIFY

    def test_confidence_calculation(self):
        """Test confidence scoring logic."""
        agent = IntentAgent()

        # Detailed text (high confidence)
        assert agent._calculate_confidence("Create a comprehensive specification for the todo application with user authentication, database integration, and a REST API") == 1.0
        assert agent._calculate_confidence("I need to implement a user login system") == 0.95

        # Question (lower confidence)
        assert agent._calculate_confidence("What do you want?") == 0.4

        # Ambiguous (medium-low confidence)
        assert agent._calculate_confidence("Make it more clear") == 0.6

        # Short text (low confidence)
        assert agent._calculate_confidence("Fix the bug") == 0.7

    def test_metadata_extraction(self):
        """Test metadata extraction."""
        agent = IntentAgent()

        # Entities extracted
        result = agent._extract_metadata("Create a User model with authentication and authorization using OAuth2. The system should support role-based access control.")
        assert "User model" in result["entities"]
        assert result["keywords"] is not None

    def test_clarification_keywords(self):
        """Test clarification keyword detection."""
        agent = IntentAgent()

        # Contains "clarify" - should be detected
        result = agent._classify_intent_type("Can you clarify the requirements?")
        assert result == IntentType.CLARIFY
        assert "clarify" in result["keywords"]

    def test_spec_keywords(self):
        """Test spec keyword detection."""
        agent = IntentAgent()

        # Contains "spec", "create" - should be detected
        result = agent._classify_intent_type("I want to create a new spec")
        assert result == IntentType.SPECIFY

    def test_execute_with_user_input(self):
        """Test execute with provided user input."""
        context = SDDContext("test")
        agent = IntentAgent()

        intent = agent.execute(context, user_input="create a specification for user login")

        assert intent is not None
        assert intent.type == IntentType.SPECIFY
        assert intent.description == "create a specification for user login"
        assert context.intent == intent

    def test_execute_raises_on_no_input(self):
        """Test execute raises error when no input available."""
        context = SDDContext("test")
        context.intent = None
        agent = IntentAgent()

        with pytest.raises(ValueError, match="No user input or intent available"):
            agent.execute(context, user_input=None)

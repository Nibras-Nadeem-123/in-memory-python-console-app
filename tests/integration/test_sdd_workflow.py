"""Integration tests for SDD workflow."""

import pytest
from src.intelligence.sdd.engine import SDDEngine, get_sdd_engine
from src.intelligence.sdd.context import SDDContext
from src.intelligence.sdd.workflow_manager import WorkflowManager, WorkflowStage
from src.intelligence.sdd.data_models import IntentType


class TestSDDWorkflow:
    """Integration tests for full SDD workflow."""

    def test_full_pipeline_intent_to_guide(self):
        """Test complete pipeline from intent to guide."""
        engine = get_sdd_engine()

        results = engine.execute(
            "create a user authentication system with login and registration",
            start_stage="intent",
            end_stage="guide"
        )

        # Should have all artifacts
        assert "intent" in results
        assert "artifacts" in results
        assert "spec" in results["artifacts"]
        assert "plan" in results["artifacts"]
        assert "guide" in results["artifacts"]

        # Intent should be parsed
        assert results["intent"]["type"] == IntentType.SPECIFY.value
        assert results["intent"]["confidence"] > 0.0

    def test_pipeline_intent_to_spec(self):
        """Test pipeline from intent to spec only."""
        engine = get_sdd_engine()

        results = engine.execute(
            "create a REST API for todo management",
            start_stage="intent",
            end_stage="spec"
        )

        # Should have intent and spec
        assert "intent" in results
        assert "spec" in results["artifacts"]
        # Should not have plan or guide
        assert "plan" not in results["artifacts"]
        assert "guide" not in results["artifacts"]

    def test_pipeline_spec_to_plan(self):
        """Test pipeline from spec to plan."""
        context = SDDContext("test")
        # Add spec artifact
        context.add_artifact("spec", "# User System\nFR-001: User login\nFR-002: User registration", {"source": "test"})

        engine = get_sdd_engine()

        # Execute from spec stage
        result = engine.execute_stage(context, "plan")

        # Should have plan artifact
        assert "plan" in context.artifacts

    def test_pipeline_validates_stages(self):
        """Test pipeline validates stage names."""
        engine = get_sdd_engine()

        with pytest.raises(Exception):  # WorkflowError
            engine.execute(
                "test input",
                start_stage="invalid_stage",
                end_stage="guide"
            )

    def test_workflow_manager_stage_transitions(self):
        """Test workflow manager handles stage transitions."""
        context = SDDContext("create a system")
        workflow = WorkflowManager()

        # Register agents
        from src.intelligence.sdd.intent_agent import IntentAgent
        from src.intelligence.sdd.spec_agent import SpecAgent

        workflow.register_agent(WorkflowStage.INTENT, IntentAgent())
        workflow.register_agent(WorkflowStage.SPEC, SpecAgent())

        # Execute workflow
        result = workflow.execute_workflow(
            context,
            start_stage=WorkflowStage.INTENT,
            end_stage=WorkflowStage.SPEC
        )

        # Should have updated context
        assert result.intent is not None
        assert "spec" in result.artifacts

    def test_workflow_creates_checkpoints(self):
        """Test workflow creates checkpoints after stages."""
        context = SDDContext("create a system")
        workflow = WorkflowManager()

        # Register agent
        from src.intelligence.sdd.intent_agent import IntentAgent
        workflow.register_agent(WorkflowStage.INTENT, IntentAgent())

        # Execute
        workflow.execute_workflow(
            context,
            start_stage=WorkflowStage.INTENT,
            end_stage=WorkflowStage.INTENT
        )

        # Should have checkpoints
        checkpoints = workflow.get_checkpoints()
        assert len(checkpoints) > 0

    def test_engine_can_handle_check(self):
        """Test engine can_handle method."""
        engine = get_sdd_engine()

        result = engine.can_handle("create a specification for user login")

        assert "can_handle" in result
        assert "intent_type" in result
        assert "confidence" in result
        assert "suggested_workflow" in result
        assert result["intent_type"] == IntentType.SPECIFY.value

    def test_engine_get_agent(self):
        """Test engine retrieves registered agents."""
        engine = get_sdd_engine()

        intent_agent = engine.get_agent("intent")
        spec_agent = engine.get_agent("spec")
        plan_agent = engine.get_agent("plan")
        guide_agent = engine.get_agent("guide")

        assert intent_agent is not None
        assert spec_agent is not None
        assert plan_agent is not None
        assert guide_agent is not None

    def test_engine_get_registered_agents(self):
        """Test engine lists registered agents."""
        engine = get_sdd_engine()

        agents = engine.get_registered_agents()

        assert "intent" in agents
        assert "spec" in agents
        assert "plan" in agents
        assert "guide" in agents

    def test_context_artifact_management(self):
        """Test context manages artifacts correctly."""
        context = SDDContext("test")

        # Add artifacts
        artifact_id1 = context.add_artifact("spec", "# Spec content", {"source": "test"})
        artifact_id2 = context.add_artifact("plan", "# Plan content", {"source": "test"})

        # Retrieve artifacts
        spec_artifact = context.get_latest_artifact("spec")
        plan_artifact = context.get_latest_artifact("plan")

        assert spec_artifact is not None
        assert plan_artifact is not None
        assert spec_artifact.artifact_type == "spec"
        assert plan_artifact.artifact_type == "plan"
        assert spec_artifact.content == "# Spec content"

    def test_context_workflow_state_transitions(self):
        """Test context workflow state transitions."""
        context = SDDContext("test")

        # Initial state
        assert context.workflow_state == "initialized"

        # Transition states
        context.transition_to("clarification")
        assert context.workflow_state == "clarification"

        context.transition_to("specification")
        assert context.workflow_state == "specification"

        context.transition_to("planning")
        assert context.workflow_state == "planning"

    def test_full_workflow_with_events(self):
        """Test full workflow logs events correctly."""
        engine = get_sdd_engine()

        results = engine.execute(
            "create a simple todo app",
            start_stage="intent",
            end_stage="spec"
        )

        # Should have logged events
        assert "events" in results
        assert len(results["events"]) > 0

        # Should have stage events
        events = results["events"]
        assert any("intent" in str(e).lower() for e in events)

    def test_pipeline_error_handling(self):
        """Test pipeline handles errors gracefully."""
        context = SDDContext("test")
        # Don't add required artifacts

        engine = get_sdd_engine()

        # Should raise error for missing spec
        with pytest.raises(Exception):
            engine.execute_stage(context, "plan")

    def test_singleton_engine_instance(self):
        """Test get_sdd_engine returns singleton."""
        engine1 = get_sdd_engine()
        engine2 = get_sdd_engine()

        # Should be same instance
        assert engine1 is engine2

    def test_workflow_stage_order(self):
        """Test workflow executes stages in correct order."""
        engine = get_sdd_engine()

        results = engine.execute(
            "create authentication",
            start_stage="intent",
            end_stage="plan"
        )

        # Should execute: intent → spec → plan
        assert "intent" in results
        assert "spec" in results["artifacts"]
        assert "plan" in results["artifacts"]

        # Artifacts should be created in order
        spec_artifact = results["artifacts"]["spec"]
        plan_artifact = results["artifacts"]["plan"]

        # Plan timestamp should be after spec timestamp
        assert spec_artifact["timestamp"] <= plan_artifact["timestamp"]

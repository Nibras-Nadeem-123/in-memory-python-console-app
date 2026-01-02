"""SDD Engine for Spec-Driven Development.

Orchestrates all agents in sequence to transform natural language
into structured artifacts (spec, plan, guide).
"""

from typing import Dict, Any, Optional, List
from .agent_base import Agent
from .context import SDDContext
from .data_models import Intent, Spec, Plan, Guide, Artifact
from .workflow_manager import WorkflowManager, WorkflowStage
from .sdd_errors import WorkflowError, SDDError
from ..utils import log_event


class SDDEngine:
    """Main orchestrator for Spec-Driven Development pipeline.

    Coordinates execution through:
    - Agent registration and routing
    - Stage transitions
    - Error handling
    - Artifact collection
    """

    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self.workflow = WorkflowManager()
        self._register_builtin_agents()

    def _register_builtin_agents(self) -> None:
        """Register built-in SDD agents."""
        # Import agents to avoid circular imports
        from .intent_agent import IntentAgent
        from .spec_agent import SpecAgent
        from .plan_agent import PlanAgent
        from .guide_agent import GuideAgent

        # Register agents
        self.register_agent(IntentAgent())
        self.register_agent(SpecAgent())
        self.register_agent(PlanAgent())
        self.register_agent(GuideAgent())

        # Register with workflow manager
        self.workflow.register_agent(WorkflowStage.INTENT, IntentAgent())
        self.workflow.register_agent(WorkflowStage.SPEC, SpecAgent())
        self.workflow.register_agent(WorkflowStage.PLAN, PlanAgent())
        self.workflow.register_agent(WorkflowStage.GUIDE, GuideAgent())

    def register_agent(self, agent: Agent) -> None:
        """Register an agent with the engine.

        Args:
            agent: The agent instance to register.
        """
        self._agents[agent.name] = agent

    def execute(
        self,
        user_input: str,
        start_stage: str = "intent",
        end_stage: str = "guide"
    ) -> Dict[str, Any]:
        """Execute SDD pipeline from user input.

        Args:
            user_input: Natural language user request.
            start_stage: Stage to start from (default: "intent").
            end_stage: Stage to end at (default: "guide").

        Returns:
            Dictionary with generated artifacts and execution metadata.

        Raises:
            WorkflowError: If pipeline execution fails.
        """
        # Create context
        context = SDDContext(user_input)

        log_event(context, "engine_start", {
            "input_length": len(user_input),
            "start_stage": start_stage,
            "end_stage": end_stage
        })

        # Determine workflow stages
        try:
            workflow_start = WorkflowStage(start_stage)
            workflow_end = WorkflowStage(end_stage)
        except ValueError as e:
            raise WorkflowError(f"Invalid stage: {e}")

        # Execute workflow
        try:
            context = self.workflow.execute_workflow(
                context,
                start_stage=workflow_start,
                end_stage=workflow_end
            )
        except WorkflowError as e:
            log_event(context, "engine_error", {"error": str(e)})
            raise

        # Collect results
        results = self._collect_results(context)

        log_event(context, "engine_complete", {
            "artifacts_count": len(results),
            "workflow_state": context.workflow_state
        })

        return results

    def execute_stage(
        self,
        context: SDDContext,
        stage: str
    ) -> SDDContext:
        """Execute a single workflow stage.

        Args:
            context: The execution context.
            stage: The stage to execute.

        Returns:
            Updated context.

        Raises:
            WorkflowError: If stage execution fails.
        """
        # Determine workflow stage
        try:
            workflow_stage = WorkflowStage(stage)
        except ValueError as e:
            raise WorkflowError(f"Invalid stage: {e}")

        # Get agent for stage
        agent = self._agents.get(stage)
        if agent is None:
            raise WorkflowError(f"No agent registered for stage: {stage}")

        # Execute agent
        try:
            result = agent.execute(context)
            log_event(context, f"stage_{stage}_completed", {
                "result_type": type(result).__name__
            })
            return context
        except Exception as e:
            log_event(context, f"stage_{stage}_error", {
                "error": str(e)
            })
            raise WorkflowError(f"Stage {stage} failed: {e}")

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get a registered agent by name.

        Args:
            name: The agent name.

        Returns:
            Agent instance or None if not found.
        """
        return self._agents.get(name)

    def get_registered_agents(self) -> List[str]:
        """Get list of registered agent names.

        Returns:
            List of agent names.
        """
        return list(self._agents.keys())

    def _collect_results(self, context: SDDContext) -> Dict[str, Any]:
        """Collect artifacts from context.

        Args:
            context: The execution context.

        Returns:
            Dictionary with all generated artifacts.
        """
        results = {
            "workflow_state": context.workflow_state,
            "artifacts": {}
        }

        # Collect artifacts
        for name, artifact in context.artifacts.items():
            results["artifacts"][name] = {
                "artifact_id": artifact.artifact_id,
                "content": artifact.content,
                "metadata": artifact.metadata,
                "timestamp": artifact.timestamp
            }

        # Add intent if available
        if context.intent:
            results["intent"] = {
                "type": context.intent.type.value,
                "description": context.intent.description,
                "confidence": context.intent.confidence,
                "metadata": context.intent.metadata
            }

        # Add events log
        results["events"] = context.events

        return results

    def can_handle(self, user_input: str) -> Dict[str, Any]:
        """Check if SDD can handle the input and determine intent.

        Args:
            user_input: Natural language input.

        Returns:
            Dictionary with intent analysis.
        """
        # Use IntentAgent to analyze
        intent_agent = self._agents.get("intent")
        if not intent_agent:
            return {"can_handle": False, "reason": "No intent agent registered"}

        # Create temporary context
        context = SDDContext(user_input)

        # Check if agent can handle
        can_handle = intent_agent.can_handle(context)

        # Parse intent
        intent = intent_agent.execute(context, user_input)

        return {
            "can_handle": can_handle,
            "intent_type": intent.type.value,
            "confidence": intent.confidence,
            "suggested_workflow": self._suggest_workflow(intent)
        }

    def _suggest_workflow(self, intent: Intent) -> List[str]:
        """Suggest workflow based on intent type.

        Args:
            intent: Parsed intent.

        Returns:
            List of suggested stages.
        """
        workflows = {
            "clarify": ["intent"],
            "specify": ["intent", "spec"],
            "plan": ["intent", "spec", "plan"],
            "guide": ["intent", "spec", "plan", "guide"]
        }

        return workflows.get(intent.type.value, ["intent"])


# Singleton instance
_sdd_engine_instance: Optional[SDDEngine] = None


def get_sdd_engine() -> SDDEngine:
    """Get singleton SDD Engine instance.

    Returns:
        The shared SDDEngine instance.
    """
    global _sdd_engine_instance

    if _sdd_engine_instance is None:
        _sdd_engine_instance = SDDEngine()

    return _sdd_engine_instance

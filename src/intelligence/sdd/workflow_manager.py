"""Workflow Manager for Spec-Driven Development.

Coordinates multi-stage execution with checkpoints and human intervention.
"""

from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass

from .context import SDDContext
from .agent_base import Agent
from .sdd_errors import WorkflowError, AmbiguityError
from ..utils import log_event


class WorkflowStage(str, Enum):
    """Workflow stages in SDD pipeline."""
    INTENT = "intent"
    SPEC = "spec"
    PLAN = "plan"
    GUIDE = "guide"
    REVIEW = "review"


@dataclass
class Checkpoint:
    """Checkpoint for resuming workflow."""
    stage: WorkflowStage
    context_data: Dict[str, Any]
    status: str
    timestamp: str


class WorkflowManager:
    """Manages SDD workflow execution.

    Coordinates:
    - Stage transitions
    - Human intervention points
    - Checkpoint creation and resumption
    - Error handling and recovery
    """

    def __init__(self):
        self._checkpoints: Dict[str, Checkpoint] = {}
        self._stage_handlers: Dict[WorkflowStage, Agent] = {}
        self._intervention_callbacks: Dict[WorkflowStage, Callable] = {}

    def register_agent(self, stage: WorkflowStage, agent: Agent) -> None:
        """Register an agent for a workflow stage.

        Args:
            stage: The workflow stage.
            agent: The agent to handle this stage.
        """
        self._stage_handlers[stage] = agent

    def register_intervention_callback(
        self,
        stage: WorkflowStage,
        callback: Callable[[SDDContext], bool]
    ) -> None:
        """Register callback for human intervention point.

        Args:
            stage: The workflow stage.
            callback: Function returning True to continue, False to halt.
        """
        self._intervention_callbacks[stage] = callback

    def execute_workflow(
        self,
        context: SDDContext,
        start_stage: WorkflowStage = WorkflowStage.INTENT,
        end_stage: WorkflowStage = WorkflowStage.GUIDE
    ) -> SDDContext:
        """Execute SDD workflow from start to end stage.

        Args:
            context: The SDD execution context.
            start_stage: Stage to start from (default: INTENT).
            end_stage: Stage to end at (default: GUIDE).

        Returns:
            Updated context with all generated artifacts.

        Raises:
            WorkflowError: If workflow execution fails.
        """
        # Get stage order
        stage_order = self._get_stage_order(start_stage, end_stage)

        # Execute each stage in sequence
        for stage in stage_order:
            context = self._execute_stage(context, stage)

            # Create checkpoint after each stage
            self._create_checkpoint(stage, context)

        return context

    def _execute_stage(self, context: SDDContext, stage: WorkflowStage) -> SDDContext:
        """Execute a single workflow stage.

        Args:
            context: The SDD execution context.
            stage: The stage to execute.

        Returns:
            Updated context.

        Raises:
            WorkflowError: If stage execution fails.
        """
        log_event(context, "stage_start", {"stage": stage.value})

        # Get agent for this stage
        agent = self._stage_handlers.get(stage)
        if agent is None:
            raise WorkflowError(f"No agent registered for stage: {stage.value}")

        # Check for human intervention
        if stage in self._intervention_callbacks:
            if not self._intervention_callbacks[stage](context):
                log_event(context, "intervention_halted", {"stage": stage.value})
                raise WorkflowError(f"Workflow halted at {stage.value} by intervention")

        # Execute agent
        try:
            result = agent.execute(context)
            context.add_event(f"{stage.value}_completed", {"result": str(type(result))})
        except Exception as e:
            log_event(context, "stage_error", {
                "stage": stage.value,
                "error": str(e)
            })
            raise WorkflowError(f"Stage {stage.value} failed: {e}")

        # Transition context to next stage
        self._transition_context(context, stage)

        log_event(context, "stage_complete", {"stage": stage.value})
        return context

    def _create_checkpoint(self, stage: WorkflowStage, context: SDDContext) -> None:
        """Create a checkpoint for workflow resumption.

        Args:
            stage: The current stage.
            context: The execution context.
        """
        import time

        checkpoint = Checkpoint(
            stage=stage,
            context_data={
                "workflow_state": context.workflow_state,
                "artifacts": {k: v.artifact_id for k, v in context.artifacts.items()},
                "events_count": len(context.events)
            },
            status="completed",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

        checkpoint_id = f"chkpt_{stage.value}_{int(time.time())}"
        self._checkpoints[checkpoint_id] = checkpoint

        log_event(context, "checkpoint_created", {
            "checkpoint_id": checkpoint_id,
            "stage": stage.value
        })

    def resume_from_checkpoint(self, checkpoint_id: str, context: SDDContext) -> SDDContext:
        """Resume workflow from a checkpoint.

        Args:
            checkpoint_id: ID of the checkpoint to resume from.
            context: The execution context to restore.

        Returns:
            Updated context for resumed execution.

        Raises:
            WorkflowError: If checkpoint not found.
        """
        if checkpoint_id not in self._checkpoints:
            raise WorkflowError(f"Checkpoint not found: {checkpoint_id}")

        checkpoint = self._checkpoints[checkpoint_id]

        # Restore context data
        context.workflow_state = checkpoint.context_data.get("workflow_state")

        log_event(context, "checkpoint_restored", {
            "checkpoint_id": checkpoint_id,
            "stage": checkpoint.stage.value
        })

        # Resume from next stage
        next_stage = self._get_next_stage(checkpoint.stage)
        if next_stage:
            return self.execute_workflow(context, start_stage=next_stage)

        return context

    def get_checkpoints(self) -> Dict[str, Checkpoint]:
        """Get all checkpoints.

        Returns:
            Dictionary mapping checkpoint IDs to Checkpoint objects.
        """
        return self._checkpoints.copy()

    def _get_stage_order(
        self,
        start_stage: WorkflowStage,
        end_stage: WorkflowStage
    ) -> List[WorkflowStage]:
        """Get ordered list of stages from start to end.

        Args:
            start_stage: Starting stage.
            end_stage: Ending stage.

        Returns:
            List of stages in execution order.
        """
        stages = list(WorkflowStage)
        start_idx = stages.index(start_stage)
        end_idx = stages.index(end_stage)

        return stages[start_idx:end_idx + 1]

    def _get_next_stage(self, current_stage: WorkflowStage) -> Optional[WorkflowStage]:
        """Get the next stage in the workflow.

        Args:
            current_stage: The current stage.

        Returns:
            Next stage or None if current is last.
        """
        stages = list(WorkflowStage)
        idx = stages.index(current_stage)

        if idx + 1 < len(stages):
            return stages[idx + 1]

        return None

    def _transition_context(self, context: SDDContext, stage: WorkflowStage) -> None:
        """Transition context to appropriate state after stage.

        Args:
            context: The execution context.
            stage: The completed stage.
        """
        transitions = {
            WorkflowStage.INTENT: "spec_generation",
            WorkflowStage.SPEC: "planning",
            WorkflowStage.PLAN: "guide_generation",
            WorkflowStage.GUIDE: "complete",
            WorkflowStage.REVIEW: "clarification"
        }

        context.transition_to(transitions.get(stage, "unknown"))

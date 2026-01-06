"""Phase 2 Workflow Manager.

Orchestrates the complete intelligence pipeline:
1. Intent Parsing & Clarification (ClarifierAgent)
2. Specification Generation & Planning (PlannerAgent)
3. Plan Validation (PlannerAgent)
4. Plan Review & Approval (ReviewerAgent)
5. Plan Execution (ExecutorAgent)

Provides a single interface for Phase 2 intelligence.
"""
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime

from .data_models import Phase2Context, Intent, ExecutionPlan
from .agents.clarifier_agent import ClarifierAgent
from .agents.planner_agent import PlannerAgent
from .agents.reviewer_agent import ReviewerAgent
from .agents.executor_agent import ExecutorAgent


class Phase2WorkflowManager:
    """Workflow manager for Phase 2 intelligence pipeline.

    Orchestrates the complete reasoning pipeline from user intent
    to plan execution using Phase 1 capabilities.
    """

    def __init__(self, phase1_executor=None):
        """Initialize workflow manager with all agents.

        Args:
            phase1_executor: Phase 1 TodoExecutor for plan execution.
        """
        self.clarifier = ClarifierAgent()
        self.planner = PlannerAgent()
        self.reviewer = ReviewerAgent()
        self.executor = ExecutorAgent(phase1_executor)

        # Track current workflow state
        self.current_context: Optional[Phase2Context] = None

    def process_intent(
        self,
        user_input: str,
        existing_context: Optional[Phase2Context] = None,
        auto_approve: bool = True
    ) -> Dict[str, Any]:
        """Process user intent through complete intelligence pipeline.

        Args:
            user_input: Natural language user intent.
            existing_context: Existing Phase2Context to resume (optional).
            auto_approve: If True, auto-approve plans for testing.

        Returns:
            Dictionary with processing results:
            - status: Current workflow state
            - context: Phase2Context with all artifacts
            - intent: Parsed intent
            - specification: Generated specification
            - plan: Generated plan
            - execution_result: Execution result if executed
            - message: Human-readable status message
        """
        # Create or resume context
        if existing_context:
            self.current_context = existing_context
            self.current_context.user_input = user_input
        else:
            execution_id = f"exec_{uuid.uuid4().hex[:12]}"
            self.current_context = Phase2Context(execution_id)
            self.current_context.user_input = user_input
            self.current_context.transition_to("initialized")

        try:
            # Stage 1: Intent Parsing & Clarification
            intent_result = self._run_clarification_stage()
            if intent_result["needs_clarification"]:
                return {
                    "status": "needs_clarification",
                    "context": self.current_context,
                    "intent": self.current_context.intent,
                    "clarifications": intent_result["clarifications"],
                    "message": "Clarification needed to proceed"
                }

            # Stage 2 & 3: Specification & Planning
            planning_result = self._run_planning_stage()
            if planning_result["failed"]:
                return {
                    "status": "planning_failed",
                    "context": self.current_context,
                    "error": planning_result["error"],
                    "message": f"Planning failed: {planning_result['error']}"
                }

            # Stage 4: Plan Review & Approval
            review_result = self._run_review_stage(auto_approve=auto_approve)
            if review_result["status"] in ["REJECTED", "REJECTED_WITH_FEEDBACK"]:
                return {
                    "status": "plan_rejected",
                    "context": self.current_context,
                    "review_result": review_result,
                    "message": "Plan was rejected by reviewer"
                }

            # Stage 5: Plan Execution
            execution_result = self._run_execution_stage()

            return {
                "status": "completed",
                "context": self.current_context,
                "intent": self.current_context.intent,
                "specification": self.current_context.specification,
                "plan": self.current_context.plan,
                "execution_result": execution_result,
                "message": self._generate_completion_message(execution_result)
            }

        except Exception as e:
            # Log error and return failure
            self.current_context.transition_to("failed")
            self.current_context.add_reasoning_step(
                stage="workflow",
                action="error",
                details={"error": str(e), "error_type": type(e).__name__}
            )

            return {
                "status": "error",
                "context": self.current_context,
                "error": str(e),
                "message": f"Error processing intent: {e}"
            }

    def continue_with_clarification(
        self,
        clarification_response: str,
        auto_approve: bool = True
    ) -> Dict[str, Any]:
        """Continue workflow after user provides clarification.

        Args:
            clarification_response: User's response to clarification question.
            auto_approve: If True, auto-approve plans.

        Returns:
            Dictionary with processing results (same format as process_intent).
        """
        if not self.current_context:
            raise ValueError("No active context to resume")

        # Store user response in clarifications
        for clarification in self.current_context.clarifications:
            if not clarification.response:
                clarification.response = clarification_response
                break

        # Log clarification response
        self.current_context.add_reasoning_step(
            stage="clarifier",
            action="clarification_response_received",
            details={
                "response_length": len(clarification_response),
                "responded_to": clarification.question_id
            }
        )

        # Continue from planning stage (intent should be updated now)
        return self.process_intent(
            self.current_context.user_input,
            existing_context=self.current_context,
            auto_approve=auto_approve
        )

    def _run_clarification_stage(self) -> Dict[str, Any]:
        """Run Stage 1: Intent Parsing & Clarification."""
        self.current_context.transition_to("clarifying")

        intent = self.clarifier.execute(
            context=self.current_context,
            user_input=self.current_context.user_input
        )

        # Check if clarification needed
        needs_clarification = (
            len(intent.ambiguities) > 0 or
            len([c for c in self.current_context.clarifications if not c.response]) > 0
        )

        return {
            "intent": intent,
            "needs_clarification": needs_clarification,
            "clarifications": self.current_context.clarifications,
            "ambiguities": intent.ambiguities
        }

    def _run_planning_stage(self) -> Dict[str, Any]:
        """Run Stage 2 & 3: Specification & Planning."""
        self.current_context.transition_to("planning")

        try:
            specification = self.planner.execute(
                context=self.current_context,
                target_operations=None,  # Use default Phase 1 operations
                complexity_level="MODERATE",
                max_depth=5
            )

            return {
                "specification": specification,
                "failed": False
            }

        except Exception as e:
            return {
                "failed": True,
                "error": str(e),
                "specification": None
            }

    def _run_review_stage(self, auto_approve: bool = True) -> Any:
        """Run Stage 4: Plan Review & Approval."""
        self.current_context.transition_to("reviewing")

        # For testing, we'll auto-approve
        # In real implementation, this would involve user interaction
        review_result = self.reviewer.execute(
            context=self.current_context,
            auto_approve=auto_approve
        )

        return review_result

    def _run_execution_stage(self) -> Any:
        """Run Stage 5: Plan Execution."""
        # Get approved plan
        approved_plan = self.current_context.plan

        if not approved_plan:
            raise ValueError("No plan available for execution")

        if approved_plan.validation_status != "PASS":
            raise ValueError(f"Plan not validated: {approved_plan.validation_status}")

        # Execute plan
        execution_result = self.executor.execute(
            context=self.current_context,
            approved_plan=approved_plan
        )

        return execution_result

    def _generate_completion_message(self, execution_result: Any) -> str:
        """Generate human-readable completion message."""
        if execution_result.status == "COMPLETED":
            message = (
                f"Plan executed successfully! "
                f"Completed {execution_result.steps_completed}/{execution_result.steps_total} steps "
                f"in {execution_result.total_duration_seconds:.1f}s"
            )
            if execution_result.tasks_added > 0:
                message += f"\nTasks added: {execution_result.tasks_added}"
            if execution_result.tasks_completed > 0:
                message += f"\nTasks completed: {execution_result.tasks_completed}"
            if execution_result.tasks_modified > 0:
                message += f"\nTasks modified: {execution_result.tasks_modified}"
            if execution_result.tasks_deleted > 0:
                message += f"\nTasks deleted: {execution_result.tasks_deleted}"

        elif execution_result.status == "PARTIAL":
            message = (
                f"Plan partially completed. "
                f"Completed {execution_result.steps_completed}/{execution_result.steps_total} steps "
                f"({execution_result.completion_percentage:.1f}%)"
            )
            if execution_result.errors:
                message += f"\nErrors encountered: {len(execution_result.errors)}"

        else:
            message = f"Plan execution {execution_result.status.lower()}"
            if execution_result.errors:
                message += f"\nErrors: {len(execution_result.errors)}"

        return message

    def get_workflow_state(self) -> Dict[str, Any]:
        """Get current workflow state information.

        Returns:
            Dictionary with current workflow state.
        """
        if not self.current_context:
            return {"status": "not_initialized"}

        return {
            "execution_id": self.current_context.execution_id,
            "workflow_state": self.current_context.workflow_state,
            "has_intent": self.current_context.intent is not None,
            "has_specification": self.current_context.specification is not None,
            "has_plan": self.current_context.plan is not None,
            "has_execution_results": self.current_context.execution_results is not None,
            "clarifications_pending": len([c for c in self.current_context.clarifications if not c.response]),
            "reasoning_steps": len(self.current_context.reasoning_trace)
        }

    def reset_workflow(self) -> None:
        """Reset workflow manager for new intent."""
        self.current_context = None

"""Reviewer Agent for Phase 2 intelligence.

Responsible for Stage 4: Plan Review & Approval.
Facilitates user review and approval of generated artifacts.
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from ..phase2.data_models import Specification, ExecutionPlan, ReviewResult, Phase2Context


class ReviewerAgent:
    """Agent for Plan Review and Approval.

    Responsibilities:
    - Present specification to user for review
    - Present plan to user for review
    - Collect user feedback and modifications
    - Validate user-provided changes
    - Request explicit approval before execution
    - Generate approval checkpoints
    """

    def __init__(self):
        """Initialize ReviewerAgent."""
        pass

    @property
    def name(self) -> str:
        """Unique agent identifier."""
        return "reviewer_phase2"

    def execute(
        self,
        context: Phase2Context,
        **kwargs: Any
    ) -> ReviewResult:
        """Execute review and approval process.

        Args:
            context: Phase 2 execution context.
            **kwargs: Additional arguments (e.g., user modifications).

        Returns:
            ReviewResult with approval status and modified artifacts.

        Raises:
            ValueError: If specification or plan not available.
        """
        # Check for artifacts to review
        specification = context.specification
        plan = context.plan

        if not specification and not plan:
            raise ValueError("No specification or plan available for review")

        # Present artifacts for review (in real implementation, would display to user)
        # For this implementation, assume auto-approve for testing
        self._display_artifacts(specification, plan)

        # Collect user feedback (would be via CLI in real implementation)
        user_feedback = kwargs.get("user_feedback")
        modifications = kwargs.get("modifications", [])

        # Validate modifications if provided
        if modifications:
            validated = self._validate_modifications(modifications, specification, plan)
            if not validated:
                return ReviewResult(
                    status="REJECTED",
                    specification=specification,
                    plan=plan,
                    user_feedback=user_feedback or "Invalid modifications",
                    modifications=modifications,
                    validation_result="FAIL",
                    metadata={"rejected_reason": "modifications_invalid"}
                )

        # Determine approval status
        if self._should_approve(specification, plan):
            # User approved
            final_spec = self._apply_modifications(specification, modifications) if modifications else specification
            final_plan = self._apply_plan_modifications(plan, modifications) if modifications else plan

            result = ReviewResult(
                status="APPROVED" if not modifications else "MODIFIED",
                specification=final_spec,
                plan=final_plan,
                user_feedback=user_feedback or "Approved",
                modifications=modifications,
                validation_result="PASS",
                metadata={
                    "approved_at": self._get_timestamp(),
                    "modification_count": len(modifications)
                }
            )
        else:
            # User rejected or needs changes
            result = ReviewResult(
                status="REJECTED_WITH_FEEDBACK" if user_feedback else "REJECTED",
                specification=specification,
                plan=plan,
                user_feedback=user_feedback or "Rejected by user",
                modifications=[],
                validation_result="PASS",
                metadata={
                    "rejected_at": self._get_timestamp()
                }
            )

        # Update context
        if result.status in ["APPROVED", "MODIFIED"]:
            context.transition_to("plan_approved")
        else:
            context.transition_to("plan_rejected")

        context.add_reasoning_step(
            stage="reviewer",
            action="review_completed",
            details={
                "review_status": result.status,
                "has_modifications": len(result.modifications) > 0,
                "validation_result": result.validation_result
            }
        )

        return result

    def _display_artifacts(self, specification: Specification = None, plan: ExecutionPlan = None) -> None:
        """Display artifacts for user review.

        In real implementation, this would format and print
        specification and plan to CLI for user review.

        For this implementation, we just log the display.
        """
        messages = []

        if specification:
            messages.append("\n=== Specification ===")
            messages.append(f"Title: {specification.title}")
            messages.append(f"Description: {specification.description}")
            messages.append(f"Requirements: {len(specification.requirements)}")
            for i, req in enumerate(specification.requirements, 1):
                messages.append(f"  {i}. {req.description}")
            messages.append(f"Acceptance Criteria: {len(specification.acceptance_criteria)}")
            for i, criteria in enumerate(specification.acceptance_criteria, 1):
                messages.append(f"  {i}. {criteria}")
            messages.append(f"Constraints: {len(specification.constraints)}")
            for constraint in specification.constraints:
                messages.append(f"  - {constraint}")

        if plan:
            messages.append("\n=== Execution Plan ===")
            messages.append(f"Title: {plan.title}")
            messages.append(f"Description: {plan.description}")
            messages.append(f"Steps: {len(plan.steps)}")
            for step in plan.steps:
                dep_str = f" (depends: {', '.join(step.dependencies)})" if step.dependencies else ""
                messages.append(f"  [{step.id}] {step.description}{dep_str}")
                messages.append(f"      Command: {step.command}")
                messages.append(f"      Priority: {step.priority}")
                messages.append(f"      Estimated: {step.estimated_seconds}s")
            messages.append(f"\nTotal estimated duration: {plan.total_estimated_seconds}s")
            messages.append(f"Risk level: {plan.risk_level}")
            messages.append(f"Validation status: {plan.validation_status}")

        # In real implementation, would print messages to CLI
        # For now, just format as string for logging
        display_text = "\n".join(messages)
        print(f"\n[REVIEW MODE]\n{display_text}\n")

    def _validate_modifications(
        self,
        modifications: List[Any],
        specification: Specification = None,
        plan: ExecutionPlan = None
    ) -> bool:
        """Validate user-provided modifications."""
        if not modifications:
            return True

        # Check modification validity
        valid = True
        for mod in modifications:
            if not self._is_valid_modification(mod, specification, plan):
                valid = False
                break

        return valid

    def _is_valid_modification(self, modification: Any, specification: Specification, plan: ExecutionPlan) -> bool:
        """Check if a single modification is valid."""
        # Simplified validation - in real implementation would be more sophisticated
        if not isinstance(modification, dict):
            return False

        # Check required fields
        if "artifact_type" not in modification:
            return False

        if "target" not in modification:
            return False

        # Check if target exists in artifacts
        artifact_type = modification.get("artifact_type")
        target = modification.get("target")

        if artifact_type == "specification" and specification:
            # Validate specification modification
            if target not in ["title", "description", "requirements"]:
                return False
        elif artifact_type == "plan" and plan:
            # Validate plan modification
            valid_ids = [s.id for s in plan.steps]
            if target not in valid_ids:
                return False

        return True

    def _should_approve(self, specification: Specification, plan: ExecutionPlan) -> bool:
        """Determine if artifacts should be auto-approved.

        In real implementation, this would present to user and collect response.
        For this implementation, auto-approve for testing.
        """
        # Check validation status
        if plan and plan.validation_status == "FAIL":
            return False  # Don't approve invalid plans

        # Auto-approve for testing
        return True

    def _apply_modifications(self, specification: Specification, modifications: List[Any]) -> Specification:
        """Apply user modifications to specification."""
        if not modifications:
            return specification

        # Create copy to modify
        import copy
        modified_spec = copy.deepcopy(specification)

        # Apply modifications
        for mod in modifications:
            if mod.get("artifact_type") == "specification":
                target = mod.get("target")
                if target == "title":
                    modified_spec.title = mod.get("new_value")
                elif target == "description":
                    modified_spec.description = mod.get("new_value")

        return modified_spec

    def _apply_plan_modifications(self, plan: ExecutionPlan, modifications: List[Any]) -> ExecutionPlan:
        """Apply user modifications to execution plan."""
        if not modifications:
            return plan

        # Create copy to modify
        import copy
        modified_plan = copy.deepcopy(plan)

        # Apply modifications
        for mod in modifications:
            if mod.get("artifact_type") == "plan":
                step_id = mod.get("target")
                for step in modified_plan.steps:
                    if step.id == step_id:
                        # Apply modification to step
                        new_value = mod.get("new_value")
                        if mod.get("field") == "description":
                            step.description = new_value
                        elif mod.get("field") == "priority":
                            step.priority = new_value

        return modified_plan

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

"""Result Evaluation Skill for Phase 2 intelligence.

Assesses execution results against original intent and specification
to determine success, quality, and next actions.
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from ..skills.skill_interface import Skill, SkillError, SkillValidationError, SkillExecutionError
from ..phase2.data_models import ExecutionResult, EvaluationResult, Intent, Specification


class ResultEvaluationSkill(Skill):
    """Skill for evaluating execution results.

    Assesses:
    - Completion metrics (steps, rate, time)
    - Error analysis (total, fatal, recoverable)
    - Intent alignment (satisfied, score, unfulfilled requirements)
    - Acceptance criteria (met, failed, rate)
    - Recommendations (proceed, retry, fallback)
    """

    @property
    def name(self) -> str:
        return "result_evaluation_phase2"

    @property
    def description(self) -> str:
        return "Assesses execution results against original intent and specification"

    @property
    def version(self) -> str:
        return "1.0.0"

    def validate_inputs(
        self,
        execution_result: ExecutionResult,
        **kwargs: Any
    ) -> None:
        """Validate inputs before execution."""
        if not execution_result:
            raise SkillValidationError("execution_result must be provided")

    def execute(
        self,
        context: Any,
        execution_result: ExecutionResult,
        original_intent: Intent = None,
        specification: Specification = None,
        plan: Any = None,
        acceptance_criteria: List[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Evaluate execution result.

        Args:
            context: The current execution context.
            execution_result: Results from ExecutorAgent.
            original_intent: Original parsed intent.
            specification: Generated specification (optional).
            plan: Execution plan (optional).
            acceptance_criteria: Success criteria (optional).
            **kwargs: Additional arguments.

        Returns:
            Dictionary containing evaluation results.

        Raises:
            SkillExecutionError: If evaluation fails.
        """
        # Determine success
        success = execution_result.status == "COMPLETED"

        # Calculate completion metrics
        steps_completed = execution_result.steps_completed
        steps_total = execution_result.steps_total
        completion_rate = (steps_completed / steps_total * 100.0) if steps_total > 0 else 0.0
        completion_time = execution_result.total_duration_seconds
        efficiency_score = self._calculate_efficiency(completion_rate, completion_time, execution_result)

        # Analyze errors
        error_analysis = self._analyze_errors(execution_result)

        # Assess intent alignment
        intent_alignment = self._assess_intent_alignment(execution_result, original_intent, specification)

        # Evaluate acceptance criteria
        acceptance_assessment = self._evaluate_acceptance_criteria(
            execution_result,
            acceptance_criteria,
            intent_alignment
        )

        # Determine overall quality score
        overall_quality = self._calculate_quality_score(
            completion_rate,
            error_analysis["total_errors"],
            intent_alignment["alignment_score"],
            efficiency_score
        )

        # Determine quality level
        quality_level = self._determine_quality_level(overall_quality, success)

        # Generate recommendations
        recommendation = self._determine_recommendation(
            success,
            error_analysis,
            intent_alignment,
            overall_quality
        )

        # Generate human-readable report
        human_report = self._generate_report(
            success,
            completion_rate,
            execution_result,
            error_analysis,
            intent_alignment,
            acceptance_assessment,
            overall_quality,
            quality_level,
            recommendation
        )

        # Generate summary
        summary = self._generate_summary(success, completion_rate, execution_result, error_analysis)

        return {
            "evaluation_result": EvaluationResult(
                success=success,
                overall_quality_score=overall_quality,
                quality_level=quality_level,
                steps_completed=steps_completed,
                steps_total=steps_total,
                completion_rate=completion_rate,
                completion_time_seconds=completion_time,
                efficiency_score=efficiency_score,
                total_errors=error_analysis["total_errors"],
                fatal_errors=error_analysis["fatal_errors"],
                recoverable_errors=error_analysis["recoverable_errors"],
                error_categories=error_analysis["categories"],
                intent_satisfied=intent_alignment["satisfied"],
                intent_alignment_score=intent_alignment["alignment_score"],
                unfulfilled_requirements=intent_alignment["unfulfilled"],
                acceptance_criteria_met=acceptance_assessment["met"],
                acceptance_criteria_failed=acceptance_assessment["failed"],
                acceptance_rate=acceptance_assessment["rate"],
                recommended_action=recommendation["action"],
                retry_probability=recommendation["retry_probability"],
                retry_suggestions=recommendation["suggestions"],
                human_readable_report=human_report,
                summary=summary
            )
        }

    def _calculate_efficiency(
        self,
        completion_rate: float,
        completion_time: float,
        execution_result: ExecutionResult
    ) -> float:
        """Calculate efficiency score based on completion and time."""
        # Base efficiency from completion rate
        efficiency = completion_rate / 100.0

        # Time bonus: faster than estimate is better
        if execution_result.metadata.get("estimated_duration"):
            estimated = execution_result.metadata["estimated_duration"]
            if estimated > 0:
                time_ratio = min(completion_time / estimated, 2.0)  # Cap at 2x
                if time_ratio < 0.8:  # 20% faster
                    efficiency += 0.1
                elif time_ratio < 1.2:  # Within 20%
                    efficiency += 0.05

        return min(efficiency, 1.0)

    def _analyze_errors(self, execution_result: ExecutionResult) -> Dict[str, Any]:
        """Analyze errors from execution result."""
        errors = execution_result.errors or []

        total_errors = len(errors)

        # Categorize errors
        fatal_errors = sum(1 for e in errors if getattr(e, "fatal", False))
        recoverable_errors = sum(1 for e in errors if getattr(e, "recoverable", True))

        # Categorize by type
        categories = {}
        for error in errors:
            error_type = getattr(error, "error_type", "UNKNOWN")
            categories[error_type] = categories.get(error_type, 0) + 1

        return {
            "total_errors": total_errors,
            "fatal_errors": fatal_errors,
            "recoverable_errors": recoverable_errors,
            "categories": categories
        }

    def _assess_intent_alignment(
        self,
        execution_result: ExecutionResult,
        original_intent: Intent = None,
        specification: Specification = None
    ) -> Dict[str, Any]:
        """Assess how well execution aligned with original intent."""
        alignment_score = 0.0
        satisfied = False
        unfulfilled_requirements = []

        # If no original intent, assume alignment
        if not original_intent:
            return {
                "satisfied": True,
                "alignment_score": 1.0,
                "unfulfilled_requirements": []
            }

        # Check if intent was satisfied based on execution type
        if original_intent.type == "ORGANIZE":
            # Organize intent satisfied if tasks were added/modified
            if execution_result.tasks_added > 0:
                alignment_score = 0.9
                satisfied = True
            elif execution_result.tasks_modified > 0:
                alignment_score = 0.8
                satisfied = True
            else:
                alignment_score = 0.3
                satisfied = False
                unfulfilled_requirements.append("No tasks were created or modified")

        elif original_intent.type == "PRIORITIZE":
            # Prioritize intent satisfied if high-priority tasks identified
            if execution_result.tasks_completed > 0:
                alignment_score = 0.9
                satisfied = True
            else:
                alignment_score = 0.5
                satisfied = False
                unfulfilled_requirements.append("No tasks were completed")

        elif original_intent.type == "QUERY":
            # Query intent satisfied if results returned
            if execution_result.status == "COMPLETED":
                alignment_score = 0.95
                satisfied = True
            else:
                alignment_score = 0.4
                satisfied = False

        # Check against specification if available
        if specification and specification.requirements:
            for req in specification.requirements:
                # Simplified check: assume tasks created implies requirements met
                # In real implementation, would check against requirement specifics
                if execution_result.tasks_added > 0:
                    alignment_score += 0.05

        # Cap alignment score
        alignment_score = min(alignment_score, 1.0)

        return {
            "satisfied": satisfied,
            "alignment_score": alignment_score,
            "unfulfilled_requirements": unfulfilled_requirements
        }

    def _evaluate_acceptance_criteria(
        self,
        execution_result: ExecutionResult,
        acceptance_criteria: List[str] = None,
        intent_alignment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate against acceptance criteria if provided."""
        if not acceptance_criteria:
            return {
                "met": [],
                "failed": [],
                "rate": 1.0  # No criteria to evaluate
            }

        met = []
        failed = []

        # Simplified acceptance criteria evaluation
        for criterion in acceptance_criteria:
            # Check if completion criteria met
            if "completed" in criterion.lower() and execution_result.steps_completed > 0:
                met.append(criterion)
            elif "no errors" in criterion.lower() and execution_result.total_errors == 0:
                met.append(criterion)
            else:
                failed.append(criterion)

        rate = len(met) / len(acceptance_criteria) if acceptance_criteria else 1.0

        return {
            "met": met,
            "failed": failed,
            "rate": rate
        }

    def _calculate_quality_score(
        self,
        completion_rate: float,
        total_errors: int,
        alignment_score: float,
        efficiency_score: float
    ) -> float:
        """Calculate overall quality score."""
        # Weight each component
        completion_weight = 0.4
        error_weight = 0.3
        alignment_weight = 0.2
        efficiency_weight = 0.1

        # Normalize scores
        completion_score = completion_rate / 100.0

        # Error score (fewer errors = higher score)
        error_score = 1.0 / (1.0 + total_errors) if total_errors > 0 else 1.0

        # Weighted sum
        quality_score = (
            completion_score * completion_weight +
            error_score * error_weight +
            alignment_score * alignment_weight +
            efficiency_score * efficiency_weight
        )

        return min(quality_score, 1.0)

    def _determine_quality_level(self, score: float, success: bool) -> str:
        """Determine quality level from score."""
        if not success:
            return "FAILED"
        elif score >= 0.9:
            return "EXCELLENT"
        elif score >= 0.75:
            return "GOOD"
        elif score >= 0.5:
            return "ACCEPTABLE"
        else:
            return "POOR"

    def _determine_recommendation(
        self,
        success: bool,
        error_analysis: Dict[str, Any],
        intent_alignment: Dict[str, Any],
        overall_quality: float
    ) -> Dict[str, Any]:
        """Determine recommended next action."""
        action = "PROCEED"
        retry_probability = 0.0
        suggestions = []

        # Check for fatal errors
        if error_analysis["fatal_errors"] > 0:
            action = "RETRY"
            retry_probability = 0.7
            suggestions.append("Fix fatal errors before retrying")
            suggestions.append("Review execution logs for details")

        # Check for low intent alignment
        elif not intent_alignment["satisfied"] and overall_quality < 0.5:
            action = "FALLBACK"
            retry_probability = 0.3
            suggestions.append("Intent not clearly understood - please rephrase")
            suggestions.append("Consider providing more detail")

        # Check for many recoverable errors
        elif error_analysis["recoverable_errors"] >= 3:
            action = "RETRY"
            retry_probability = 0.6
            suggestions.append("Multiple errors encountered - review input")
            suggestions.append("Consider breaking into smaller steps")

        # Check for partial completion
        elif 60.0 <= overall_quality < 90.0:
            action = "PROCEED_WITH_WARNINGS"
            retry_probability = 0.8
            suggestions.append("Execution completed with issues")
            suggestions.append("Review results before proceeding")

        return {
            "action": action,
            "retry_probability": retry_probability,
            "suggestions": suggestions
        }

    def _generate_report(
        self,
        success: bool,
        completion_rate: float,
        execution_result: ExecutionResult,
        error_analysis: Dict[str, Any],
        intent_alignment: Dict[str, Any],
        acceptance_assessment: Dict[str, Any],
        overall_quality: float,
        quality_level: str,
        recommendation: Dict[str, Any]
    ) -> str:
        """Generate human-readable evaluation report."""
        lines = [
            "Execution Summary:",
            f"- Status: {execution_result.status}",
            f"- Steps completed: {execution_result.steps_completed}/{execution_result.steps_total} ({completion_rate:.1f}%)",
            f"- Time taken: {execution_result.total_duration_seconds:.1f}s"
        ]

        # Add error section
        if error_analysis["total_errors"] > 0:
            lines.append("")
            lines.append("Error Analysis:")
            lines.append(f"- Total errors: {error_analysis['total_errors']}")
            lines.append(f"- Fatal errors: {error_analysis['fatal_errors']}")
            lines.append(f"- Recoverable errors: {error_analysis['recoverable_errors']}")
            if error_analysis["categories"]:
                lines.append("- Error breakdown:")
                for error_type, count in error_analysis["categories"].items():
                    lines.append(f"  {error_type}: {count}")

        # Add intent alignment section
        lines.append("")
        lines.append("Intent Alignment:")
        lines.append(f"- Satisfied: {'Yes' if intent_alignment['satisfied'] else 'No'}")
        lines.append(f"- Alignment score: {intent_alignment['alignment_score']:.2f}")
        if intent_alignment["unfulfilled_requirements"]:
            lines.append("- Unfulfilled requirements:")
            for req in intent_alignment["unfulfilled_requirements"]:
                lines.append(f"  - {req}")

        # Add acceptance criteria section
        if acceptance_assessment["met"] or acceptance_assessment["failed"]:
            lines.append("")
            lines.append("Acceptance Criteria:")
            lines.append(f"- Met: {len(acceptance_assessment['met'])}")
            lines.append(f"- Failed: {len(acceptance_assessment['failed'])}")
            lines.append(f"- Rate: {acceptance_assessment['rate']:.1%}")

        # Add quality assessment section
        lines.append("")
        lines.append("Quality Assessment:")
        lines.append(f"- Overall score: {overall_quality:.2f}/1.00 ({quality_level})")
        lines.append(f"- Recommendation: {recommendation['action']}")

        # Add suggestions if any
        if recommendation["suggestions"]:
            lines.append("")
            lines.append("Suggestions:")
            for suggestion in recommendation["suggestions"]:
                lines.append(f"- {suggestion}")

        return "\n".join(lines)

    def _generate_summary(
        self,
        success: bool,
        completion_rate: float,
        execution_result: ExecutionResult,
        error_analysis: Dict[str, Any]
    ) -> str:
        """Generate one-sentence summary."""
        if not success:
            if execution_result.status == "CANCELLED":
                return "Execution was cancelled by user"
            elif error_analysis["fatal_errors"] > 0:
                return f"Execution failed with {error_analysis['fatal_errors']} fatal error(s)"
            else:
                return f"Execution failed with {error_analysis['total_errors']} error(s)"
        else:
            return f"All {execution_result.steps_completed} steps completed successfully in {execution_result.total_duration_seconds:.1f}s with {error_analysis['total_errors']} error(s)"

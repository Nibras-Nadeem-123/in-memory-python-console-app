"""Planner Agent for Phase 2 intelligence.

Responsible for Stage 2 & 3: Specification Generation & Planning.
Transforms clarified intent into validated execution plan.
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from ..phase2.data_models import Intent, Specification, ExecutionPlan, Phase2Context
from ..skills.intent_analysis_skill import IntentAnalysisSkill
from ..skills.ambiguity_detection_skill import AmbiguityDetectionSkill
from ..skills.task_decomposition_skill import TaskDecompositionSkill
from ..skills.plan_validation_skill import PlanValidationSkill


class PlannerAgent:
    """Agent for Specification Generation and Planning.

    Responsibilities:
    - Generate formal specification from clarified intent
    - Decompose specification into actionable steps
    - Resolve dependencies between steps
    - Validate plan for soundness and executability
    """

    def __init__(self):
        """Initialize PlannerAgent with required skills."""
        self.intent_skill = IntentAnalysisSkill()
        self.decomposition_skill = TaskDecompositionSkill()
        self.validation_skill = PlanValidationSkill()

        # Phase 1 operation schema (for command mapping)
        self.phase1_schema = {
            "valid_commands": ["add", "list", "complete", "delete", "update", "help", "exit"],
            "command_patterns": {
                "add": r"^add task[:\s]*(.+?)\s*(?:with|for)\s*(priority\s+(\w+))?",
                "list": r"^list tasks?$",
                "complete": r"^complete[:\s]*(.+)$",
                "delete": r"^delete[:\s]*(.+)$",
                "update": r"^update[:\s]*(.+?)\s*to\s*(.+)$",
                "help": r"^help$",
                "exit": r"^(exit|quit|bye|goodbye)$"
            }
        }

    @property
    def name(self) -> str:
        """Unique agent identifier."""
        return "planner_phase2"

    def execute(
        self,
        context: Phase2Context,
        target_operations: List[str] = None,
        complexity_level: str = "MODERATE",
        max_depth: int = 5,
        **kwargs: Any
    ) -> Specification:
        """Generate specification and execution plan from clarified intent.

        Args:
            context: Phase 2 execution context.
            target_operations: Available Phase 1 operations.
            complexity_level: Complexity level (SIMPLE, MODERATE, COMPLEX).
            max_depth: Maximum decomposition depth.

        Returns:
            Generated specification object.

        Raises:
            ValueError: If intent is not clarified.
        """
        # Check for clarified intent
        if not context.intent or context.intent.completeness < 0.8:
            raise ValueError("Intent must be clarified before planning")

        # Step 1: Generate specification from intent
        specification = self._generate_specification(context)

        # Step 2: Decompose specification into steps
        decomposition_result = self.decomposition_skill.execute(
            requirements=self._extract_requirements(specification),
            target_operations=target_operations or self.phase1_schema["valid_commands"],
            existing_tasks=self._get_existing_tasks(context),
            complexity_level=complexity_level,
            max_depth=max_depth
        )

        # Step 3: Validate plan
        validation_result = self.validation_skill.execute(
            plan=ExecutionPlan(
                title=f"Plan: {specification.title}",
                description=specification.description,
                steps=decomposition_result["steps"],
                total_estimated_seconds=decomposition_result["total_estimated_duration"],
                risk_level=decomposition_result.get("risk_level", "LOW"),
                validation_status="PENDING"
            ),
            phase1_schema=self.phase1_schema
        )

        # Step 4: Handle validation result
        if validation_result["validation_report"].status == "FAIL":
            # Plan invalid - need to replan or request constraints
            context.add_reasoning_step(
                stage="planner",
                action="plan_validation_failed",
                details={
                    "validation_status": validation_result["validation_report"].status,
                    "issues_count": len(validation_result["validation_report"].issues),
                    "critical_issues": len(validation_result["validation_report"].critical_issues)
                }
            )

        # Store specification and plan in context
        context.add_specification(specification)
        context.add_plan(ExecutionPlan(
            title=f"Plan: {specification.title}",
            description=specification.description,
            steps=decomposition_result["steps"],
            total_estimated_seconds=decomposition_result["total_estimated_duration"],
            risk_level=validation_result["validation_report"].risk_level,
            validation_status=validation_result["validation_report"].status
        ))

        # Update context
        context.add_reasoning_step(
            stage="planner",
            action="spec_and_plan_generated",
            details={
                "specification_title": specification.title,
                "requirements_count": len(specification.requirements),
                "plan_steps_count": len(decomposition_result["steps"]),
                "validation_status": validation_result["validation_report"].status,
                "risk_level": validation_result["validation_report"].risk_level
            }
        )

        return specification

    def _generate_specification(self, context: Phase2Context) -> Specification:
        """Generate formal specification from clarified intent."""
        intent = context.intent

        # Extract requirements from intent
        requirements = []
        if intent.parameters:
            tasks = intent.parameters.get("tasks", [])
            for task in tasks:
                requirements.append(f"Create task: {task}")

        # Extract priorities if mentioned
        if intent.parameters:
            priorities = intent.parameters.get("priorities", [])
            if priorities:
                requirements.append("Support task prioritization")

        # Extract timeframes if mentioned
        timeframes = intent.parameters.get("timeframes", [])
        if timeframes:
            for timeframe in timeframes:
                requirements.append(f"Filter tasks by timeframe: {timeframe}")

        # Extract constraints
        constraints = intent.parameters.get("constraints", [])

        # Generate acceptance criteria
        acceptance_criteria = []
        if intent.type == "organize":
            acceptance_criteria.append("All specified tasks created in task store")
            acceptance_criteria.append("Dependencies between tasks resolved")

        # Create specification
        specification = Specification(
            title=self._generate_title(intent.description),
            description=intent.description,
            requirements=[self._create_requirement(i, req) for i, req in enumerate(requirements, 1)],
            acceptance_criteria=acceptance_criteria,
            constraints=constraints,
            assumptions=["No persistence - in-memory only"],
            metadata={
                "generated_by": "planner_agent",
                "intent_type": intent.type.value,
                "intent_confidence": intent.confidence,
                "generated_at": self._get_timestamp()
            }
        )

        return specification

    def _create_requirement(self, index: int, description: str) -> Any:
        """Create requirement object."""
        from ..phase2.data_models import Requirement

        return Requirement(
            id=f"FR-{index:03d}",
            description=description,
            priority="P1" if index <= 3 else "P2",
            source="derived"
        )

    def _extract_requirements(self, specification: Specification) -> List[str]:
        """Extract requirement descriptions from specification."""
        return [req.description for req in specification.requirements]

    def _get_existing_tasks(self, context: Phase2Context) -> List[Any]:
        """Get existing task state from context (optional)."""
        # In Phase 2, task state is in Phase 1 executor
        # This is a placeholder - in real implementation would read from task_store
        return context.execution_results if context.execution_results else []

    def _generate_title(self, description: str) -> str:
        """Generate specification title from description."""
        # Take first 10 words
        words = description.split()[:10]
        return " ".join(words).title()

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

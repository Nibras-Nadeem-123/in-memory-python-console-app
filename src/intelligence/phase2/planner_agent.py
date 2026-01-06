"""Planner Agent for Phase 2 intelligence.

Responsible for Stage 2 & 3: Specification & Planning.
Generates executable plans from clarified intent.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class StepStatus(str, Enum):
    """Status of a plan step."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class Priority(str, Enum):
    """Priority levels for steps."""
    P0 = "P0"  # Critical
    P1 = "P1"  # High
    P2 = "P2"  # Medium
    P3 = "P3"  # Low


class ValidationStatus(str, Enum):
    """Validation status of plan."""
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass
class Requirement:
    """A requirement for the specification."""
    description: str
    is_must_have: bool = False
    is_nice_to_have: bool = False
    acceptance_criteria: List[str] = field(default_factory=list)


@dataclass
class Specification:
    """Generated specification from intent."""
    title: str
    description: str
    requirements: List[Requirement] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    estimated_effort: Optional[str] = None
    created_at: str = ""
    version: str = "1.0"


@dataclass
class PlanStep:
    """A single step in an execution plan."""
    id: str
    description: str
    command: str
    command_type: str  # ADD, UPDATE, DELETE, COMPLETE, LIST
    dependencies: List[str] = field(default_factory=list)
    priority: Priority = Priority.P2
    estimated_seconds: float = 5.0
    status: StepStatus = StepStatus.PENDING


@dataclass
class ExecutionPlan:
    """Complete execution plan for Phase 1."""
    title: str
    description: str
    steps: List[PlanStep] = field(default_factory=list)
    validation_status: ValidationStatus = ValidationStatus.PASS
    validation_report: Optional[Dict[str, Any]] = None
    total_estimated_seconds: float = 0.0
    risk_level: str = "LOW"
    created_at: str = ""
    version: str = "1.0"


class PlannerAgent:
    """Agent for Specification and Planning.

    Responsibilities:
    - Generate specification from intent
    - Decompose into actionable steps
    - Map steps to Phase 1 commands
    - Validate plan is executable
    """

    def __init__(self):
        """Initialize PlannerAgent."""
        pass

    @property
    def name(self) -> str:
        """Unique agent identifier."""
        return "planner_phase2"

    def execute(
        self,
        intent: Any,
        context: Optional[Any] = None,
        target_operations: Optional[List[str]] = None,
        complexity_level: str = "MODERATE",
        max_depth: int = 5,
        **kwargs: Any
    ) -> Specification:
        """Generate specification and execution plan from intent.

        Args:
            intent: Parsed user intent from ClarifierAgent.
            context: Execution context.
            target_operations: Available Phase 1 operations.
            complexity_level: SIMPLE, MODERATE, COMPLEX.
            max_depth: Maximum decomposition depth.

        Returns:
            Specification with embedded execution plan.

        Raises:
            ValueError: If intent is missing or invalid.
        """
        if not intent or not hasattr(intent, 'description'):
            raise ValueError("Valid intent is required")

        # Generate specification
        specification = self._generate_specification(intent)

        # Generate execution plan
        plan = self._generate_execution_plan(specification, target_operations)

        # Validate plan
        validation_result = self._validate_plan(plan)
        plan.validation_status = validation_result["status"]
        plan.validation_report = validation_result

        # Store plan in specification metadata
        specification.execution_plan = plan

        return specification

    def _generate_specification(self, intent: Any) -> Specification:
        """Generate specification from parsed intent."""
        # Create title from intent description
        title = self._extract_title(intent.description)

        # Extract requirements
        requirements = self._extract_requirements(intent)

        # Generate acceptance criteria
        acceptance_criteria = self._generate_acceptance_criteria(requirements)

        # Identify constraints
        constraints = self._identify_constraints(intent)

        specification = Specification(
            title=title,
            description=intent.description,
            requirements=requirements,
            acceptance_criteria=acceptance_criteria,
            constraints=constraints,
            estimated_effort=self._estimate_effort(requirements),
            created_at=datetime.now().isoformat()
        )

        return specification

    def _extract_title(self, description: str) -> str:
        """Extract title from intent description."""
        # Use first sentence as title
        sentences = description.split('.')
        if sentences:
            return sentences[0].strip()[:60]  # Limit to 60 chars
        return description[:60]

    def _extract_requirements(self, intent: Any) -> List[Requirement]:
        """Extract requirements from intent."""
        requirements = []
        description = intent.description.lower()

        # Task-based requirements
        if "add" in description or "create" in description or "task:" in description:
            # Extract task text
            import re
            task_match = re.search(r'(?:add|create|task:)\s+(.+)', description, re.IGNORECASE)
            if task_match:
                task_text = task_match.group(1).strip()
                if task_text:
                    requirements.append(Requirement(
                        description=f"Add task: {task_text}",
                        is_must_have=True
                    ))

        # Organization-based requirements
        elif "organize" in description or "arrange" in description or "sort" in description:
            requirements.append(Requirement(
                description="Review and organize existing tasks",
                is_must_have=True
            ))

        # Prioritization-based requirements
        elif "prioritize" in description or "important" in description:
            requirements.append(Requirement(
                description="Identify high-priority tasks",
                is_must_have=True
            ))

        # Default: generic plan requirement
        if not requirements:
            requirements.append(Requirement(
                description="Process user request",
                is_must_have=True
            ))

        return requirements

    def _generate_acceptance_criteria(self, requirements: List[Requirement]) -> List[str]:
        """Generate acceptance criteria from requirements."""
        criteria = []

        for req in requirements:
            if req.is_must_have:
                criteria.append(f"{req.description} completed successfully")

        # Add general criteria
        criteria.append("All tasks stored in system")
        criteria.append("No errors reported")

        return criteria

    def _identify_constraints(self, intent: Any) -> List[str]:
        """Identify constraints from intent."""
        constraints = []
        description = intent.description.lower()

        # Time-based constraints
        if "today" in description:
            constraints.append("Must complete within current day")
        elif "this week" in description:
            constraints.append("Must complete within current week")

        # Priority constraints
        if "urgent" in description or "asap" in description:
            constraints.append("High priority tasks first")

        return constraints

    def _estimate_effort(self, requirements: List[Requirement]) -> str:
        """Estimate effort for requirements."""
        if not requirements:
            return "Unknown"

        req_count = len(requirements)

        if req_count <= 2:
            return "Small (1-2 tasks)"
        elif req_count <= 5:
            return "Medium (3-5 tasks)"
        else:
            return "Large (6+ tasks)"

    def _generate_execution_plan(
        self,
        specification: Specification,
        target_operations: Optional[List[str]] = None
    ) -> ExecutionPlan:
        """Generate execution plan from specification."""
        steps = []
        step_counter = 1

        # Map requirements to steps
        for req in specification.requirements:
            step_id = f"S{step_counter:03d}"

            # Determine command type
            command, command_type = self._map_to_command(req.description)

            # Create step
            step = PlanStep(
                id=step_id,
                description=req.description,
                command=command,
                command_type=command_type,
                priority=self._determine_priority(step_counter, len(specification.requirements)),
                estimated_seconds=self._estimate_step_duration(req.description)
            )

            steps.append(step)
            step_counter += 1

        # Calculate total estimate
        total_estimate = sum(s.estimated_seconds for s in steps)

        plan = ExecutionPlan(
            title=f"Plan: {specification.title}",
            description=f"Generated plan with {len(steps)} steps",
            steps=steps,
            validation_status=ValidationStatus.PASS,
            total_estimated_seconds=total_estimate,
            created_at=datetime.now().isoformat()
        )

        return plan

    def _map_to_command(self, description: str) -> tuple[str, str]:
        """Map requirement description to Phase 1 command."""
        lower_desc = description.lower()

        # Add task mapping
        if "add task:" in lower_desc:
            task_title = lower_desc.replace("add task:", "").strip()
            return f"add task: {task_title}", "ADD"

        # Complete task mapping
        elif "complete" in lower_desc:
            return "list tasks", "COMPLETE"  # Will show tasks for user to complete

        # Organize mapping
        elif "organize" in lower_desc or "review" in lower_desc:
            return "list tasks", "LIST"

        # Prioritize mapping
        elif "prioritize" in lower_desc:
            return "list tasks", "LIST"

        # Default mapping
        return description, "ADD"

    def _determine_priority(self, index: int, total: int) -> Priority:
        """Determine step priority based on position."""
        if index <= 1:
            return Priority.P1
        elif index <= 3:
            return Priority.P2
        else:
            return Priority.P3

    def _estimate_step_duration(self, description: str) -> float:
        """Estimate duration for a step."""
        base = 2.0

        # Add time for complex operations
        if "organize" in description.lower():
            base += 3.0
        elif "prioritize" in description.lower():
            base += 2.0

        return min(base, 10.0)

    def _validate_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Validate execution plan."""
        issues = []
        warnings = []

        # Check for empty plan
        if not plan.steps:
            issues.append("Plan has no steps")
            return {
                "status": ValidationStatus.FAIL,
                "issues": issues,
                "warnings": warnings
            }

        # Check for valid commands
        for step in plan.steps:
            if not step.command:
                issues.append(f"Step {step.id} has no command")

        # Determine overall status
        if issues:
            status = ValidationStatus.FAIL
        elif warnings:
            status = ValidationStatus.WARN
        else:
            status = ValidationStatus.PASS

        return {
            "status": status,
            "issues": issues,
            "warnings": warnings,
            "checks_performed": len(issues) + len(warnings)
        }

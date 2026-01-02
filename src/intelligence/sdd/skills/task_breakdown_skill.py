"""Task Breakdown Skill for Spec-Driven Development.

Breaks down requirements into actionable implementation tasks.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from src.intelligence.sdd.data_models import Spec, Task
from src.intelligence.skills.skill_interface import Skill, SkillInput, SkillOutput
from src.intelligence.sdd.context import SDDContext


class TaskBreakdownSkill(Skill):
    """Skill for breaking down specs into actionable tasks.

    Analyzes requirements to create:
    - Implementation tasks
    - Test tasks
    - Documentation tasks
    - Task priorities and estimates
    """

    @property
    def name(self) -> str:
        return "task_breakdown"

    @property
    def description(self) -> str:
        return "Breaks down specifications into actionable implementation tasks."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def input_schema(self) -> SkillInput:
        return SkillInput(
            name="spec",
            type=Spec,
            description="Specification document with requirements",
            required=True
        )

    @property
    def output_schema(self) -> SkillOutput:
        return SkillOutput(
            name="tasks",
            type=List[Task],
            description="List of implementation tasks with dependencies and estimates"
        )

    def execute(self, context: SDDContext, spec: Spec = None, **kwargs: Any) -> List[Task]:
        """Break down spec into tasks.

        Args:
            context: The SDD execution context.
            spec: Spec object with requirements.
            **kwargs: Additional arguments.

        Returns:
            List of Task objects with priorities, dependencies, and estimates.
        """
        if spec is None:
            return []

        tasks = []
        task_id_counter = 1

        # Task generation by requirement type
        for i, req in enumerate(spec.requirements, 1):
            # Implementation task
            impl_task = Task(
                id=f"T{task_id_counter:03d}",
                description=f"Implement: {req}",
                status="pending",
                priority=self._determine_priority(i, len(spec.requirements)),
                dependencies=[],
                estimated_hours=self._estimate_hours(req)
            )
            tasks.append(impl_task)
            task_id_counter += 1

            # Test task
            test_task = Task(
                id=f"T{task_id_counter:03d}",
                description=f"Test: {req}",
                status="pending",
                priority=self._determine_priority(i, len(spec.requirements), is_test=True),
                dependencies=[impl_task.id],
                estimated_hours=self._estimate_hours(req) * 0.3
            )
            tasks.append(test_task)
            task_id_counter += 1

        # Add integration task
        integration_task = Task(
            id=f"T{task_id_counter:03d}",
            description="Integrate all components and verify end-to-end flow",
            status="pending",
            priority="P1",
            dependencies=[t.id for t in tasks if "Test" not in t.description],
            estimated_hours=2.0
        )
        tasks.append(integration_task)
        task_id_counter += 1

        # Add documentation task
        doc_task = Task(
            id=f"T{task_id_counter:03d}",
            description="Document implementation and update README",
            status="pending",
            priority="P2",
            dependencies=[integration_task.id],
            estimated_hours=1.0
        )
        tasks.append(doc_task)

        # Log breakdown
        context._log_event("tasks_broken_down", {
            "task_count": len(tasks),
            "req_count": len(spec.requirements)
        })

        return tasks

    def _determine_priority(self, index: int, total: int, is_test: bool = False) -> str:
        """Determine task priority based on position and type.

        Args:
            index: Position of requirement (1-based)
            total: Total number of requirements
            is_test: Whether this is a test task

        Returns:
            Priority string (P1, P2, P3)
        """
        # First 3 requirements are P1
        if index <= 3:
            base_priority = "P1"
        elif index <= 6:
            base_priority = "P2"
        else:
            base_priority = "P3"

        # Test tasks are one level lower priority
        if is_test and base_priority == "P1":
            return "P2"
        elif is_test and base_priority == "P2":
            return "P3"

        return base_priority

    def _estimate_hours(self, requirement: str) -> float:
        """Estimate implementation hours for a requirement.

        Simple heuristic based on requirement complexity.
        """
        # Base estimate
        hours = 1.0

        # Increase for complex words
        complexity_keywords = [
            "integrate", "connect", "synchronize", "real-time",
            "authentication", "authorization", "encryption",
            "database", "migration", "transaction",
            "API", "REST", "GraphQL", "webhook"
        ]

        for keyword in complexity_keywords:
            if keyword.lower() in requirement.lower():
                hours += 1.0

        # Cap at reasonable maximum
        return min(hours, 8.0)

"""Plan Generation Agent for Spec-Driven Development.

Transforms a specification into a structured implementation plan
with tasks, dependencies, and execution order.
"""

from typing import Dict, Any, Optional, List
from .agent_base import Agent
from .data_models import Plan, Task
from .context import SDDContext
from .templates.spec_template import SPEC_TEMPLATE
from ..utils import format_output, log_event


class PlanAgent(Agent):
    """Agent responsible for Stage 3: Planning.

    Transforms a specification into an implementation plan with:
    - Task breakdown
    - Dependency resolution
    - Effort estimation
    - Architecture considerations
    """

    @property
    def name(self) -> str:
        return "plan"

    def can_handle(self, context: SDDContext) -> bool:
        """Return True if this agent should handle current context.

        PlanAgent handles:
        - Context with spec artifact (Stage 2 complete)
        - Context requiring planning (clarification complete)

        Args:
            context: The SDD execution context.

        Returns:
            bool: True if agent should process this context.
        """
        # Check for spec artifact
        spec = context.get_latest_artifact("spec")
        if spec is not None:
            return True

        # Check if we're waiting for clarification
        if context.workflow_state == "needs_clarification":
            return True

        # Not our responsibility otherwise
        return False

    def execute(self, context: SDDContext, **kwargs: Any) -> Plan:
        """Generate implementation plan from specification.

        Args:
            context: The SDD execution context containing the spec.
            **kwargs: Additional arguments (e.g., task priorities, complexity level).

        Returns:
            Plan: Generated implementation plan with tasks.
        """
        # Get spec from context
        spec = context.get_latest_artifact("spec")
        if spec is None:
            log_event(context, "spec_missing", {
                "message": "No spec artifact found for planning"
            })
            raise ValueError("Specification artifact not found")

        # Extract spec content for analysis
        spec_content = spec.content if isinstance(spec.content, str) else str(spec.content)

        # Generate task breakdown
        tasks = self._generate_tasks(context, spec_content)

        # Create plan object
        plan = Plan(
            title=self._generate_plan_title(spec_content),
            architecture=self._determine_architecture(spec_content, tasks),
            tasks=tasks
        )

        # Store artifact
        spec_artifact_id = None
        for aid, artifact in context.artifacts.items():
            if artifact.artifact_type == "spec":
                spec_artifact_id = aid
                break

        context.add_artifact("plan", plan.content, {
            "spec_id": spec_artifact_id,
            "source": "spec"
        })

        log_event(context, "plan_generated", {
            "title": plan.title,
            "task_count": len(tasks)
        })

        return plan

    def _generate_plan_title(self, spec_content: str) -> str:
        """Generate plan title from spec description."""
        # Extract first meaningful phrase (10 words)
        words = spec_content.split()[:10]
        return f"Implementation Plan: {' '.join(words).title()}"

    def _determine_architecture(self, spec_content: str, tasks: List[Task]) -> str:
        """Determine architecture from spec content and tasks."""
        # Simple heuristics
        if "REST" in spec_content.upper() or "API" in spec_content.upper():
            return "REST API"
        elif "database" in spec_content.upper():
            return "Database-driven"
        elif "UI" in spec_content.upper() or "frontend" in spec_content.upper():
            return "Web application"
        else:
            return "Modular service"

    def _generate_tasks(self, context: SDDContext, spec_content: str) -> List[Task]:
        """Generate tasks from specification.

        This is a simplified version - in full implementation, this would
        be more sophisticated with actual requirement parsing.
        """
        tasks = []

        # Extract requirements (very basic parsing)
        requirements = self._extract_requirements(spec_content)

        # Generate tasks from requirements
        task_id = "T001"
        for i, req in enumerate(requirements, 1):
            task = Task(
                id=task_id,
                description=req,
                status="pending",
                priority="P1" if i <= 3 else f"P{i-2}",
                dependencies=[]
            )
            tasks.append(task)
            task_id = f"T{str(i + 1).zfill(3)}"

        # Add architecture task
        arch_task = Task(
            id="ARCH",
            description=f"Implement {self._determine_architecture(spec_content, tasks)}",
            status="pending",
            priority="P1",
            dependencies=[]
        )
        tasks.append(arch_task)

        # Add documentation task
        doc_task = Task(
            id="DOC",
            description=f"Document {self._determine_architecture(spec_content, tasks)}",
            status="pending",
            priority="P2",
            dependencies=[task_id]
        )
        tasks.append(doc_task)

        return tasks

    def _extract_requirements(self, spec_content: str) -> List[str]:
        """Extract requirements from specification content.

        Very basic extraction - looks for FR-XXX patterns and bullet points.

        Args:
            spec_content: The specification content to parse.

        Returns:
            List of requirement descriptions.
        """
        requirements = []

        # Split by lines
        lines = spec_content.split('\n')

        for line in lines:
            line = line.strip()
            # Look for requirement patterns (FR-XXX, bullet points, numbered lists)
            if line.startswith('FR-') or line.startswith('- ') or line.startswith('* '):
                # Extract the requirement text
                req_text = line.lstrip('FR-0123456789:- *').strip()
                if req_text and len(req_text) > 5:  # Minimum meaningful length
                    requirements.append(req_text)

        # If no formal requirements found, extract from general content
        if not requirements:
            # Take first few sentences as basic requirements
            sentences = [s.strip() for s in spec_content.split('.') if s.strip()]
            requirements = sentences[:5]  # Take first 5 sentences as requirements

        return requirements


def log_event(context: SDDContext, event_type: str, details: Dict[str, Any]) -> None:
    """Log an event to the context and display output."""
    context.add_event(f"sdd_{event_type}", details)
    format_output(context, event_type, details)

"""Task Decomposition Skill for Phase 2 intelligence.

Breaks down high-level goals into actionable, executable steps
with dependencies and command mappings.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from ..skills.skill_interface import Skill, SkillError, SkillValidationError, SkillExecutionError
from ..phase2.data_models import PlanStep, ExecutionPlan, Requirement


class TaskDecompositionSkill(Skill):
    """Skill for decomposing requirements into actionable steps.

    Analyzes requirements to create:
    - Implementation tasks
    - Dependency resolution
    - Priority assignment
    - Command mapping to Phase 1
    """

    @property
    def name(self) -> str:
        return "task_decomposition_phase2"

    @property
    def description(self) -> str:
        return "Breaks down requirements into actionable execution steps with dependencies"

    @property
    def version(self) -> str:
        return "1.0.0"

    def validate_inputs(
        self,
        requirements: List[str],
        **kwargs: Any
    ) -> None:
        """Validate inputs before execution."""
        if not requirements:
            raise SkillValidationError("requirements must be non-empty list")
        if len(requirements) > 100:
            raise SkillValidationError("too many requirements (>100)")

    def execute(
        self,
        context: Any,
        requirements: List[str],
        target_operations: List[str],
        existing_tasks: List[Any] = None,
        complexity_level: str = "MODERATE",
        max_depth: int = 5,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Decompose requirements into executable steps.

        Args:
            context: The current execution context.
            requirements: List of requirements to decompose.
            target_operations: Available Phase 1 operations.
            existing_tasks: Current task state (optional).
            complexity_level: SIMPLE, MODERATE, COMPLEX.
            max_depth: Maximum decomposition depth.

        Returns:
            Dictionary containing:
            - steps: List of PlanStep objects
            - dependency_graph: Step ID -> dependent step IDs
            - has_circular_dependencies: Boolean
            - critical_path: List of step IDs
            - total_estimated_duration: Total time estimate
            - confidence: Estimation confidence score

        Raises:
            SkillExecutionError: If decomposition fails.
        """
        # Generate step ID counter
        step_counter = 1
        steps = []

        # Process each requirement
        for i, req in enumerate(requirements, 1):
            # Create step for requirement
            step = PlanStep(
                id=f"S{step_counter:03d}",
                description=req,
                command=self._map_requirement_to_command(req, target_operations),
                command_type=self._get_command_type(req, target_operations),
                dependencies=[],
                priority=self._determine_priority(i, len(requirements)),
                estimated_seconds=self._estimate_duration(req, complexity_level)
            )
            steps.append(step)
            step_counter += 1

        # Add dependency resolution step if needed
        if len(steps) > 1:
            dep_step = PlanStep(
                id=f"S{step_counter:03d}",
                description="Verify task dependencies are resolved",
                command="list tasks",
                command_type="LIST",
                dependencies=[s.id for s in steps],
                priority="P1",
                estimated_seconds=2.0
            )
            steps.append(dep_step)
            step_counter += 1

        # Build dependency graph
        dependency_graph = self._build_dependency_graph(steps)

        # Check for circular dependencies
        has_circular = self._detect_circular_dependencies(dependency_graph)

        # Find critical path (longest dependency chain)
        critical_path = self._find_critical_path(dependency_graph, steps)

        # Calculate total estimated duration
        total_duration = sum(s.estimated_seconds for s in steps)

        # Calculate confidence
        confidence = self._calculate_confidence(requirements, complexity_level)

        return {
            "steps": steps,
            "dependency_graph": dependency_graph,
            "has_circular_dependencies": has_circular,
            "critical_path": critical_path,
            "total_estimated_duration": total_duration,
            "confidence": confidence
        }

    def _map_requirement_to_command(
        self,
        requirement: str,
        target_operations: List[str]
    ) -> str:
        """Map abstract requirement to concrete Phase 1 command."""
        # Simple keyword-based mapping
        req_lower = requirement.lower()

        # Check for task creation patterns
        if "create task" in req_lower or "add task" in req_lower:
            # Extract task title
            if ":" in req_lower:
                task_title = req_lower.split(":")[1].strip()
                return f"add task: {task_title}"
            elif '"' in req_lower:
                task_title = req_lower.split('"')[1]
                return f'add task: "{task_title}"'
            else:
                # Use requirement as task title
                return f"add task: {requirement}"

        # Check for task update patterns
        elif "update task" in req_lower or "modify task" in req_lower:
            return requirement  # Already has task ID in it

        # Check for completion patterns
        elif "complete task" in req_lower or "finish task" in req_lower:
            return requirement  # Already has task ID

        # Check for deletion patterns
        elif "delete task" in req_lower or "remove task" in req_lower:
            return requirement  # Already has task ID

        # Default: treat as task creation
        return f"add task: {requirement}"

    def _get_command_type(
        self,
        requirement: str,
        target_operations: List[str]
    ) -> str:
        """Determine command type from requirement."""
        req_lower = requirement.lower()

        # Map requirement keywords to command types
        if any(kw in req_lower for kw in ["add", "create", "new"]):
            return "ADD"
        elif any(kw in req_lower for kw in ["update", "modify", "change", "set"]):
            return "UPDATE"
        elif any(kw in req_lower for kw in ["complete", "finish", "done", "mark"]):
            return "COMPLETE"
        elif any(kw in req_lower for kw in ["delete", "remove", "drop"]):
            return "DELETE"
        else:
            return "ADD"  # Default

    def _determine_priority(self, index: int, total: int) -> str:
        """Determine step priority based on position."""
        # First 3 requirements are P1
        if index <= 3:
            return "P1"
        elif index <= 6:
            return "P2"
        else:
            return "P3"

    def _estimate_duration(self, requirement: str, complexity_level: str) -> float:
        """Estimate execution duration for a requirement."""
        # Base estimate based on complexity
        base_estimates = {
            "SIMPLE": 2.0,
            "MODERATE": 5.0,
            "COMPLEX": 10.0
        }
        base_duration = base_estimates.get(complexity_level, 5.0)

        # Adjust based on requirement complexity keywords
        complexity_keywords = [
            "integrate", "synchronize", "connect", "database", "api",
            "authentication", "encryption", "migration", "transaction"
        ]

        for keyword in complexity_keywords:
            if keyword.lower() in requirement.lower():
                base_duration += 2.0  # More time for complex operations

        # Cap at reasonable maximum
        return min(base_duration, 30.0)

    def _build_dependency_graph(self, steps: List[PlanStep]) -> Dict[str, List[str]]:
        """Build dependency graph from steps."""
        graph = {}

        for step in steps:
            graph[step.id] = step.dependencies

        return graph

    def _detect_circular_dependencies(self, graph: Dict[str, List[str]]) -> bool:
        """Detect if dependency graph has circular dependencies."""
        visited = set()
        recursion_stack = set()

        def visit(node: str) -> bool:
            if node in recursion_stack:
                return True  # Circular dependency found
            if node in visited:
                return False

            visited.add(node)
            recursion_stack.add(node)

            for neighbor in graph.get(node, []):
                if visit(neighbor):
                    return True

            recursion_stack.remove(node)
            return False

        # Check all nodes
        for node in graph:
            if visit(node):
                return True

        return False

    def _find_critical_path(
        self,
        graph: Dict[str, List[str]],
        steps: List[PlanStep]
    ) -> List[str]:
        """Find longest dependency chain (critical path)."""
        max_path = []
        max_length = 0

        for step in steps:
            path = self._dfs_path(step.id, graph, [])
            if len(path) > max_length:
                max_length = len(path)
                max_path = path

        return max_path

    def _dfs_path(self, node: str, graph: Dict[str, List[str]], visited: List[str]) -> List[str]:
        """Depth-first search to find path from node."""
        if node in visited:
            return []

        visited.append(node)
        max_path = [node]

        for neighbor in graph.get(node, []):
            path = self._dfs_path(neighbor, graph, visited.copy())
            if len(path) > len(max_path):
                max_path = path

        return max_path

    def _calculate_confidence(self, requirements: List[str], complexity_level: str) -> float:
        """Calculate confidence score for estimation."""
        confidence = 0.7  # Base confidence

        # Increase confidence for simple complexity
        if complexity_level == "SIMPLE":
            confidence += 0.1

        # Increase confidence for fewer requirements
        if len(requirements) <= 3:
            confidence += 0.1
        elif len(requirements) <= 5:
            confidence += 0.05

        # Cap at 1.0
        return min(confidence, 1.0)

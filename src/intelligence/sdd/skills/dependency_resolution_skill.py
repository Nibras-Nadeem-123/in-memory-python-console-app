"""Dependency Resolution Skill for Spec-Driven Development.

Identifies task dependencies and execution order.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from src.intelligence.sdd.data_models import Task
from src.intelligence.skills.skill_interface import Skill, SkillInput, SkillOutput
from src.intelligence.sdd.context import SDDContext


class DependencyResolutionSkill(Skill):
    """Skill for resolving task dependencies and execution order.

    Analyzes tasks to:
    - Identify implicit dependencies
    - Detect circular dependencies
    - Suggest execution order
    - Optimize parallel execution
    """

    @property
    def name(self) -> str:
        return "dependency_resolution"

    @property
    def description(self) -> str:
        return "Identifies task dependencies and optimal execution order."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def input_schema(self) -> SkillInput:
        return SkillInput(
            name="tasks",
            type=List[Task],
            description="List of implementation tasks",
            required=True
        )

    @property
    def output_schema(self) -> SkillOutput:
        return SkillOutput(
            name="resolved_tasks",
            type=List[Task],
            description="Tasks with updated dependencies and execution order"
        )

    def execute(self, context: SDDContext, tasks: List[Task], **kwargs: Any) -> List[Task]:
        """Resolve dependencies between tasks.

        Args:
            context: The SDD execution context.
            tasks: List of Task objects.
            **kwargs: Additional arguments.

        Returns:
            List of Task objects with resolved dependencies.
        """
        if not tasks:
            return []

        # Create a copy to avoid modifying original
        resolved_tasks = [Task(**task.__dict__) for task in tasks]

        # Identify implicit dependencies
        self._identify_implicit_dependencies(resolved_tasks)

        # Check for circular dependencies
        cycles = self._detect_cycles(resolved_tasks)
        if cycles:
            context._log_event("circular_dependencies", {
                "cycles": cycles
            })

        # Calculate execution order
        execution_order = self._topological_sort(resolved_tasks)

        # Log resolution
        context._log_event("dependencies_resolved", {
            "task_count": len(resolved_tasks),
            "total_dependencies": sum(len(t.dependencies) for t in resolved_tasks),
            "execution_order": execution_order
        })

        return resolved_tasks

    def _identify_implicit_dependencies(self, tasks: List[Task]) -> None:
        """Identify implicit dependencies based on task descriptions.

        Modifies tasks in-place to add discovered dependencies.
        """
        task_map = {task.id: task for task in tasks}

        # Patterns indicating dependencies
        dependency_patterns = {
            "test": ["test", "verify", "validate", "check"],
            "documentation": ["document", "readme", "comment", "guide"],
            "integration": ["integrate", "connect", "merge", "combine"],
            "deployment": ["deploy", "release", "publish"]
        }

        for task in tasks:
            desc_lower = task.description.lower()

            # Test tasks depend on their corresponding implementation tasks
            if "test:" in task.description.lower():
                impl_id = task.id.replace("T", "T")
                # Look for implementation task with similar ID or description
                for potential_dep in tasks:
                    if (potential_dep.id == task.id and
                        "implement:" in potential_dep.description.lower()):
                        if potential_dep.id not in task.dependencies:
                            task.dependencies.append(potential_dep.id)

            # Documentation tasks depend on implementation
            if any(kw in desc_lower for kw in dependency_patterns["documentation"]):
                # Add all implementation tasks as dependencies
                for potential_dep in tasks:
                    if (potential_dep.id != task.id and
                        "implement:" in potential_dep.description.lower() and
                        potential_dep.id not in task.dependencies):
                        task.dependencies.append(potential_dep.id)

            # Integration tasks depend on all implementations
            if any(kw in desc_lower for kw in dependency_patterns["integration"]):
                for potential_dep in tasks:
                    if (potential_dep.id != task.id and
                        "implement:" in potential_dep.description.lower() and
                        potential_dep.id not in task.dependencies):
                        task.dependencies.append(potential_dep.id)

    def _detect_cycles(self, tasks: List[Task]) -> List[List[str]]:
        """Detect circular dependencies in task graph.

        Returns:
            List of cycles found (each cycle is a list of task IDs).
        """
        # Build adjacency list
        adj = {task.id: task.dependencies for task in tasks}

        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> None:
            """Depth-first search for cycles."""
            visited.add(node)
            rec_stack.add(node)

            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path + [node])
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.remove(node)

        for task_id in adj.keys():
            if task_id not in visited:
                dfs(task_id, [])

        return cycles

    def _topological_sort(self, tasks: List[Task]) -> List[str]:
        """Generate topological sort of tasks for execution order.

        Returns:
            List of task IDs in dependency order.
        """
        # Build adjacency list and in-degree count
        adj = {task.id: [] for task in tasks}
        in_degree = {task.id: 0 for task in tasks}

        task_map = {task.id: task for task in tasks}

        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in adj:
                    adj[dep_id].append(task.id)
                    in_degree[task.id] += 1

        # Kahn's algorithm for topological sort
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # If not all tasks processed, there's a cycle
        if len(result) != len(tasks):
            # Return whatever we have (partial order)
            pass

        return result

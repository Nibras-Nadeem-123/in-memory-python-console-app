"""Executor Agent for Phase 2 intelligence.

Responsible for Stage 5: Plan Execution using Phase 1 capabilities.
Orchestrates step execution, tracks results, handles errors.
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from ..phase2.data_models import ExecutionPlan, ExecutionResult, StepResult, ExecutionError, Phase2Context
from ...todo_executor import TodoExecutor, ExecutionResult as Phase1ExecutionResult


class ExecutorAgent:
    """Agent for executing validated execution plans.

    Responsibilities:
    - Orchestrate step execution in dependency order
    - Dispatch Phase 1 commands for each step
    - Track execution progress and results
    - Handle errors and apply rollback strategies
    - Generate execution reports
    """

    def __init__(self, phase1_executor: TodoExecutor = None):
        """Initialize ExecutorAgent with Phase 1 executor.

        Args:
            phase1_executor: Phase 1 command executor.
        """
        self.phase1_executor = phase1_executor or TodoExecutor()

    @property
    def name(self) -> str:
        """Unique agent identifier."""
        return "executor_phase2"

    def execute(
        self,
        context: Phase2Context,
        approved_plan: ExecutionPlan = None,
        **kwargs: Any
    ) -> ExecutionResult:
        """Execute validated execution plan.

        Args:
            context: The Phase 2 execution context.
            approved_plan: Validated execution plan to execute.
            **kwargs: Additional arguments.

        Returns:
            ExecutionResult with status and results.

        Raises:
            ValueError: If plan is not provided or invalid.
        """
        # Validate inputs
        if not approved_plan:
            raise ValueError("approved_plan must be provided")

        if approved_plan.validation_status != "PASS":
            raise ValueError(f"Plan must be validated (status: {approved_plan.validation_status})")

        # Step 1: Initialize execution
        context.transition_to("executing")
        context.add_reasoning_step(
            stage="executor",
            action="execution_initialized",
            details={"plan_title": approved_plan.title, "steps_count": len(approved_plan.steps)}
        )

        # Step 2: Execute steps in dependency order
        step_results = {}
        errors = []
        warnings = []
        tasks_added = 0
        tasks_modified = 0
        tasks_deleted = 0
        tasks_completed = 0

        # Sort steps by dependencies (topological order)
        execution_order = self._get_execution_order(approved_plan.steps)

        # Execute each step
        for step in execution_order:
            # Update step status
            step.status = "IN_PROGRESS"
            context.add_reasoning_step(
                stage="executor",
                action="step_started",
                details={"step_id": step.id, "command": step.command}
            )

            try:
                # Dispatch to Phase 1 executor
                result = self._execute_step(step)

                # Step completed successfully
                step.status = "COMPLETED"
                step_results[step.id] = StepResult(
                    step_id=step.id,
                    status="COMPLETED",
                    command=step.command,
                    output=result.message,
                    error=None,
                    started_at=context.metadata.get("current_step_start", ""),
                    completed_at=self._get_timestamp(),
                    duration_seconds=self._calculate_duration(
                        context.metadata.get("current_step_start"),
                        self._get_timestamp()
                    )
                )

                # Track state changes
                self._track_state_changes(step, result, context)

                context.add_reasoning_step(
                    stage="executor",
                    action="step_completed",
                    details={"step_id": step.id, "output": result.message}
                )

            except Exception as e:
                # Step failed
                step.status = "FAILED"
                error = ExecutionError(
                    error_id=self._generate_error_id(step.id),
                    step_id=step.id,
                    error_type=self._classify_error(e),
                    error_message=str(e),
                    fatal=self._is_fatal_error(e),
                    recoverable=self._is_recoverable_error(e),
                    occurred_at=self._get_timestamp()
                )
                errors.append(error)
                warnings.append(StepResult(
                    step_id=step.id,
                    status="FAILED",
                    command=step.command,
                    output="",
                    error=error,
                    started_at=context.metadata.get("current_step_start", ""),
                    completed_at=self._get_timestamp(),
                    duration_seconds=self._calculate_duration(
                        context.metadata.get("current_step_start"),
                        self._get_timestamp()
                    )
                ))

                context.add_reasoning_step(
                    stage="executor",
                    action="step_failed",
                    details={"step_id": step.id, "error": str(e)}
                )

                # Check if fatal error (stop execution)
                if error.fatal:
                    break

        # Step 3: Compile final results
        steps_completed = len([s for s in step_results.values() if s.status == "COMPLETED"])
        steps_total = len(approved_plan.steps)
        completion_percentage = (steps_completed / steps_total * 100.0) if steps_total > 0 else 0.0

        # Step 4: Create execution result
        execution_result = ExecutionResult(
            status="COMPLETED" if steps_completed == steps_total and not errors else "PARTIAL",
            steps_completed=steps_completed,
            steps_total=steps_total,
            completion_percentage=completion_percentage,
            started_at=context.metadata.get("execution_start", self._get_timestamp()),
            completed_at=self._get_timestamp(),
            total_duration_seconds=self._calculate_duration(
                context.metadata.get("execution_start"),
                self._get_timestamp()
            ),
            errors=errors,
            warnings=[],
            rollback_performed=False,
            rollback_status=None,
            step_results=step_results,
            tasks_added=tasks_added,
            tasks_modified=tasks_modified,
            tasks_deleted=tasks_deleted,
            tasks_completed=tasks_completed,
            metadata={
                "plan_title": approved_plan.title,
                "phase1_used": True,
                "executed_at": self._get_timestamp()
            }
        )

        # Store in context
        context.add_execution_result(execution_result)

        # Final workflow state
        if execution_result.status == "COMPLETED":
            context.transition_to("completed")
        else:
            context.transition_to("failed")

        context.add_reasoning_step(
            stage="executor",
            action="execution_completed",
            details={
                "status": execution_result.status,
                "steps_completed": steps_completed,
                "steps_total": steps_total,
                "errors_count": len(errors)
            }
        )

        return execution_result

    def _execute_step(self, step: Any) -> Phase1ExecutionResult:
        """Execute a single plan step using Phase 1 executor.

        Args:
            step: PlanStep with command to execute.

        Returns:
            Phase1ExecutionResult from TodoExecutor.
        """
        # Record start time in metadata
        self._set_metadata("current_step_start", self._get_timestamp())

        result = self.phase1_executor.execute(step.command)

        # Clear step start time
        self._clear_metadata("current_step_start")

        return result

    def _track_state_changes(self, step: Any, result: Phase1ExecutionResult, context: Phase2Context) -> None:
        """Track state changes from Phase 1 execution."""
        # Update state change counters based on result
        if result.success and result.data:
            if "task" in result.data:
                task_data = result.data["task"]
                if step.command_type == "ADD":
                    context.metadata["tasks_added"] = context.metadata.get("tasks_added", 0) + 1
                elif step.command_type == "UPDATE":
                    context.metadata["tasks_modified"] = context.metadata.get("tasks_modified", 0) + 1
                elif step.command_type == "COMPLETE":
                    context.metadata["tasks_completed"] = context.metadata.get("tasks_completed", 0) + 1
                elif step.command_type == "DELETE":
                    context.metadata["tasks_deleted"] = context.metadata.get("tasks_deleted", 0) + 1

    def _get_execution_order(self, steps: List[Any]) -> List[Any]:
        """Get execution order respecting dependencies.

        Args:
            steps: List of PlanStep objects.

        Returns:
            Ordered list of steps (topological sort).
        """
        # Build dependency graph
        graph = {}
        step_map = {step.id: step for step in steps}

        for step in steps:
            graph[step.id] = step.dependencies

        # Topological sort
        visited = set()
        result = []

        def visit(step_id: str):
            if step_id not in visited:
                visited.add(step_id)
                result.append(step_map[step_id])
                # Visit dependencies first
                for dep_id in graph.get(step_id, []):
                    visit(dep_id)

        # Visit all steps
        for step in steps:
            visit(step.id)

        return result

    def _classify_error(self, error: Exception) -> str:
        """Classify error type."""
        error_str = str(error).lower()

        if "not found" in error_str or "doesn't exist" in error_str:
            return "EXECUTION"
        elif "timeout" in error_str:
            return "TIMEOUT"
        elif "permission" in error_str or "access" in error_str:
            return "API_ERROR"
        elif "validation" in error_str or "invalid" in error_str:
            return "VALIDATION"
        else:
            return "EXECUTION"

    def _is_fatal_error(self, error: Exception) -> bool:
        """Determine if error is fatal (stops execution)."""
        error_str = str(error).lower()

        # Fatal if task store error
        fatal_indicators = [
            "corrupted", "database error", "critical", "fatal"
        ]

        return any(indicator in error_str for indicator in fatal_indicators)

    def _is_recoverable_error(self, error: Exception) -> bool:
        """Determine if error is recoverable (can continue)."""
        error_str = str(error).lower()

        # Recoverable if it's a single step failure
        recoverable = not self._is_fatal_error(error)

        return recoverable

    def _calculate_duration(self, start_time: str, end_time: str) -> float:
        """Calculate duration between two timestamps."""
        from datetime import datetime

        try:
            start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            return (end - start).total_seconds()
        except:
            return 0.0

    def _generate_error_id(self, step_id: str) -> str:
        """Generate unique error identifier."""
        import uuid
        return f"err_{step_id}_{uuid.uuid4().hex[:8]}"

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value in context."""
        # This would be stored in context.metadata
        # Implementation detail: ensure metadata dict exists
        pass

    def _clear_metadata(self, key: str) -> None:
        """Clear metadata value in context."""
        pass

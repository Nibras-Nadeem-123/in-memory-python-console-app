"""Skill Composition Utilities for Spec-Driven Development.

Combines multiple skills in sequence with output passing.
"""

from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass

from .context import SDDContext
from ..skills.skill_interface import Skill, SkillExecutionError
from ..utils import log_event


@dataclass
class SkillChainStep:
    """Single step in a skill chain."""
    skill: Skill
    output_key: str  # Key to store output in context
    error_handler: Optional[Callable] = None  # Optional error handler


@dataclass
class ChainResult:
    """Result of executing a skill chain."""
    success: bool
    outputs: Dict[str, Any]
    errors: List[Exception]
    execution_time: float


class SkillComposer:
    """Composes multiple skills into execution chains.

    Provides:
    - Sequential skill execution
    - Output passing between skills
    - Error handling and recovery
    - Parallel execution support
    """

    def __init__(self, context: SDDContext):
        """Initialize composer with execution context.

        Args:
            context: The SDD execution context.
        """
        self.context = context
        self._chains: Dict[str, List[SkillChainStep]] = {}

    def register_chain(self, name: str, steps: List[SkillChainStep]) -> None:
        """Register a named skill chain.

        Args:
            name: Chain identifier.
            steps: List of chain steps.
        """
        self._chains[name] = steps

    def execute_chain(
        self,
        chain_name: str,
        initial_input: Dict[str, Any] = None,
        fail_fast: bool = True
    ) -> ChainResult:
        """Execute a skill chain.

        Args:
            chain_name: Name of registered chain.
            initial_input: Input data for first skill.
            fail_fast: Stop on first error (default: True).

        Returns:
            ChainResult with outputs and errors.
        """
        if chain_name not in self._chains:
            raise SkillExecutionError(f"Chain not registered: {chain_name}")

        import time
        start_time = time.time()

        steps = self._chains[chain_name]
        outputs = initial_input or {}
        errors = []
        success = True

        log_event(self.context, "chain_start", {
            "chain_name": chain_name,
            "step_count": len(steps)
        })

        # Execute each step
        for i, step in enumerate(steps, 1):
            try:
                # Execute skill with accumulated outputs
                step_output = step.skill.execute(self.context, **outputs)

                # Store output
                outputs[step.output_key] = step_output

                log_event(self.context, "chain_step_complete", {
                    "chain_name": chain_name,
                    "step": i,
                    "skill": step.skill.name,
                    "output_key": step.output_key
                })

            except Exception as e:
                errors.append(e)

                log_event(self.context, "chain_step_error", {
                    "chain_name": chain_name,
                    "step": i,
                    "skill": step.skill.name,
                    "error": str(e)
                })

                # Try error handler if available
                if step.error_handler:
                    try:
                        step.error_handler(e, outputs)
                    except Exception as handler_error:
                        errors.append(handler_error)

                if fail_fast:
                    success = False
                    break

        # Calculate execution time
        execution_time = time.time() - start_time

        log_event(self.context, "chain_complete", {
            "chain_name": chain_name,
            "success": success,
            "steps_completed": i if errors and fail_fast else len(steps),
            "execution_time": execution_time
        })

        return ChainResult(
            success=success,
            outputs=outputs,
            errors=errors,
            execution_time=execution_time
        )

    def execute_parallel(
        self,
        skills: List[Skill],
        inputs: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute multiple skills in parallel.

        Args:
            skills: List of skills to execute.
            inputs: Optional list of inputs (one per skill).

        Returns:
            Dictionary mapping skill names to outputs.
        """
        if inputs is None:
            inputs = [{}] * len(skills)

        if len(inputs) != len(skills):
            raise SkillExecutionError("Inputs list length must match skills list length")

        log_event(self.context, "parallel_start", {
            "skill_count": len(skills)
        })

        outputs = {}
        errors = {}

        # Execute each skill
        for skill, skill_input in zip(skills, inputs):
            try:
                output = skill.execute(self.context, **skill_input)
                outputs[skill.name] = output
            except Exception as e:
                errors[skill.name] = e

        log_event(self.context, "parallel_complete", {
            "success_count": len(outputs),
            "error_count": len(errors)
        })

        return {
            "outputs": outputs,
            "errors": errors
        }

    def get_chains(self) -> List[str]:
        """Get list of registered chain names.

        Returns:
            List of chain names.
        """
        return list(self._chains.keys())


def create_sdd_chain(context: SDDContext) -> SkillComposer:
    """Create default SDD skill chain.

    Args:
        context: The SDD execution context.

    Returns:
        SkillComposer with SDD-specific chains.
    """
    from .skills import (
        IntentParsingSkill,
        AmbiguityDetectionSkill,
        RequirementExtractionSkill,
        TaskBreakdownSkill,
        DependencyResolutionSkill,
        CodeScaffoldingSkill,
        BestPracticesSkill
    )

    composer = SkillComposer(context)

    # Intent parsing chain
    composer.register_chain("parse_intent", [
        SkillChainStep(
            skill=IntentParsingSkill(),
            output_key="intent"
        ),
        SkillChainStep(
            skill=AmbiguityDetectionSkill(),
            output_key="ambiguities"
        )
    ])

    # Spec generation chain
    composer.register_chain("generate_spec", [
        SkillChainStep(
            skill=RequirementExtractionSkill(),
            output_key="requirements"
        )
    ])

    # Planning chain
    composer.register_chain("create_plan", [
        SkillChainStep(
            skill=TaskBreakdownSkill(),
            output_key="tasks"
        ),
        SkillChainStep(
            skill=DependencyResolutionSkill(),
            output_key="resolved_tasks"
        )
    ])

    # Guidance chain
    composer.register_chain("provide_guidance", [
        SkillChainStep(
            skill=CodeScaffoldingSkill(),
            output_key="scaffolding"
        ),
        SkillChainStep(
            skill=BestPracticesSkill(),
            output_key="practices"
        )
    ])

    return composer

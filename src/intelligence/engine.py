"""
Core Intelligence Engine for the Intelligence Framework.

This module provides the IntelligenceEngine that transforms user goals
into executable plans. It is the "thinking" layer of the system,
responsible for understanding intent and creating plans.

Key Components:
- Goal: Raw user input
- Intent: Structured interpretation of the goal
- IntelligenceEngine: Orchestrates goal-to-outcome transformation
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
import re

from src.intelligence.context import ExecutionContext
from src.intelligence.runtime import (
    RuntimeEngine,
    ExecutionPlan,
    Action,
    Outcome,
    ExecutionStatus,
)
from src.intelligence.skills.skill_registry import SkillRegistry


# =============================================================================
# Exceptions
# =============================================================================

class EngineError(Exception):
    """Base exception for engine errors."""
    pass


class PlanningError(EngineError):
    """Raised when plan generation fails."""
    pass


class AmbiguousIntentError(EngineError):
    """Raised when the intent cannot be determined."""
    pass


class IntentParsingError(EngineError):
    """Raised when intent parsing fails."""
    pass


# =============================================================================
# Data Structures
# =============================================================================

class IntentType(str, Enum):
    """Types of recognized intents."""
    READ = "read"
    WRITE = "write"
    TRANSFORM = "transform"
    ANALYZE = "analyze"
    SEARCH = "search"
    UNKNOWN = "unknown"


@dataclass
class Goal:
    """
    Raw user input representing what they want to accomplish.

    Attributes:
        description: Natural language description of the goal
        metadata: Additional context or constraints
        created_at: Timestamp when the goal was created
    """
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def from_string(cls, description: str) -> Goal:
        """Create a Goal from a simple string."""
        return cls(description=description)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


@dataclass
class Intent:
    """
    Structured interpretation of a user goal.

    Attributes:
        action: The primary action to perform
        target: The target of the action (e.g., file path)
        parameters: Additional parameters for the action
        intent_type: Classification of the intent
        confidence: Confidence score (0.0 to 1.0)
        original_goal: Reference to the original goal
    """
    action: str
    target: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    intent_type: IntentType = IntentType.UNKNOWN
    confidence: float = 1.0
    original_goal: Optional[Goal] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action": self.action,
            "target": self.target,
            "parameters": self.parameters,
            "intent_type": self.intent_type.value,
            "confidence": self.confidence,
        }


@dataclass
class EvaluationResult:
    """
    Result of evaluating an execution outcome against the original intent.

    Attributes:
        success: Whether the outcome matches the intent
        score: Evaluation score (0.0 to 1.0)
        feedback: Human-readable feedback
        suggestions: Suggestions for improvement
    """
    success: bool
    score: float = 1.0
    feedback: str = ""
    suggestions: List[str] = field(default_factory=list)


# =============================================================================
# Intent Parser
# =============================================================================

class IntentParser:
    """
    Parses natural language goals into structured intents.

    This is a simple rule-based parser. In a production system,
    this could be replaced with an LLM-based parser.
    """

    # Pattern definitions for common intents
    PATTERNS = [
        # Read/summarize patterns
        (r"(?:read|open|get|show|display)\s+(?:the\s+)?(.+)", IntentType.READ, "read"),
        (r"summarize\s+(?:the\s+)?(.+)", IntentType.TRANSFORM, "summarize"),
        (r"(?:what(?:'s| is) in|contents? of)\s+(?:the\s+)?(.+)", IntentType.READ, "read"),

        # Search patterns
        (r"(?:find|search|look for|locate)\s+(.+)", IntentType.SEARCH, "find"),
        (r"(?:list|show)\s+(?:all\s+)?(.+)(?:\s+files?)?", IntentType.SEARCH, "list"),

        # Transform patterns
        (r"(?:convert|transform|change)\s+(.+)\s+(?:to|into)\s+(.+)", IntentType.TRANSFORM, "convert"),

        # Analyze patterns
        (r"(?:analyze|check|examine|inspect)\s+(?:the\s+)?(.+)", IntentType.ANALYZE, "analyze"),

        # Write patterns
        (r"(?:write|create|save|output)\s+(.+)", IntentType.WRITE, "write"),
    ]

    def parse(self, goal: Goal) -> Intent:
        """
        Parse a goal into a structured intent.

        Args:
            goal: The goal to parse

        Returns:
            Structured intent

        Raises:
            AmbiguousIntentError: If the goal is too vague
        """
        description = goal.description.lower().strip()

        if not description:
            raise AmbiguousIntentError("Empty goal description")

        # Try to match against known patterns
        for pattern, intent_type, action in self.PATTERNS:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                target = match.group(1).strip() if match.groups() else None
                return Intent(
                    action=action,
                    target=target,
                    intent_type=intent_type,
                    confidence=0.8,
                    original_goal=goal,
                )

        # Default: treat the whole description as a generic action
        return Intent(
            action="execute",
            target=description,
            intent_type=IntentType.UNKNOWN,
            confidence=0.5,
            original_goal=goal,
        )


# =============================================================================
# Plan Generator
# =============================================================================

class PlanGenerator:
    """
    Generates execution plans from intents.

    Maps intents to sequences of skill invocations.
    """

    def __init__(self, skill_registry: SkillRegistry) -> None:
        self._skill_registry = skill_registry

    def generate(self, intent: Intent) -> ExecutionPlan:
        """
        Generate an execution plan for an intent.

        Args:
            intent: The intent to plan for

        Returns:
            An execution plan

        Raises:
            PlanningError: If no plan can be generated
        """
        actions: List[Action] = []

        # Map intent to actions based on action type
        if intent.action == "summarize":
            # Summarize requires reading then summarizing
            actions = self._plan_summarize(intent)
        elif intent.action == "read":
            actions = self._plan_read(intent)
        elif intent.action == "find" or intent.action == "list":
            actions = self._plan_search(intent)
        elif intent.action == "analyze":
            actions = self._plan_analyze(intent)
        else:
            # Try to find a matching skill
            actions = self._plan_generic(intent)

        return ExecutionPlan(
            actions=actions,
            metadata={
                "intent": intent.to_dict(),
                "generated_at": datetime.now().isoformat(),
            },
        )

    def _plan_summarize(self, intent: Intent) -> List[Action]:
        """Plan for summarize intent."""
        target = intent.target or ""

        # Determine file path from target
        file_path = self._extract_file_path(target)

        actions = []

        # Step 1: Read the file
        if self._skill_registry.has("read_file"):
            actions.append(Action(
                skill="read_file",
                args={"file_path": file_path},
                description=f"Read contents of {file_path}",
            ))

        # Step 2: Summarize
        if self._skill_registry.has("summarize_text"):
            actions.append(Action(
                skill="summarize_text",
                args={},  # Will use content from context state
                description="Summarize the file contents",
            ))

        return actions

    def _plan_read(self, intent: Intent) -> List[Action]:
        """Plan for read intent."""
        target = intent.target or ""
        file_path = self._extract_file_path(target)

        if self._skill_registry.has("read_file"):
            return [Action(
                skill="read_file",
                args={"file_path": file_path},
                description=f"Read {file_path}",
            )]
        return []

    def _plan_search(self, intent: Intent) -> List[Action]:
        """Plan for search/find intent."""
        # This is a placeholder - would need a find_files skill
        return []

    def _plan_analyze(self, intent: Intent) -> List[Action]:
        """Plan for analyze intent."""
        # This is a placeholder - would need analysis skills
        return []

    def _plan_generic(self, intent: Intent) -> List[Action]:
        """Generate a generic plan based on available skills."""
        # Check if there's a skill matching the action
        if self._skill_registry.has(intent.action):
            return [Action(
                skill=intent.action,
                args=intent.parameters,
                description=f"Execute {intent.action}",
            )]
        return []

    def _extract_file_path(self, target: str) -> str:
        """Extract a file path from a target description."""
        target = target.lower().strip()

        # Common file references
        if "readme" in target:
            return "README.md"
        if "license" in target:
            return "LICENSE"
        if "config" in target:
            return "config.json"
        if "package" in target:
            return "package.json"
        if "pyproject" in target:
            return "pyproject.toml"

        # If it looks like a path, use it directly
        if "/" in target or "." in target:
            return target

        # Default to treating target as filename
        return target


# =============================================================================
# Intelligence Engine
# =============================================================================

class IntelligenceEngine:
    """
    The core intelligence engine that transforms goals into outcomes.

    This is the main orchestrator that:
    1. Parses user goals into structured intents
    2. Generates execution plans
    3. Executes plans via the runtime
    4. Evaluates outcomes

    Example:
        engine = IntelligenceEngine(skill_registry)
        outcome = engine.process("summarize the readme file")
        print(outcome.result)
    """

    def __init__(
        self,
        skill_registry: SkillRegistry,
        runtime: Optional[RuntimeEngine] = None,
        intent_parser: Optional[IntentParser] = None,
        plan_generator: Optional[PlanGenerator] = None,
    ) -> None:
        """
        Initialize the intelligence engine.

        Args:
            skill_registry: Registry of available skills
            runtime: Optional runtime engine (created if not provided)
            intent_parser: Optional custom intent parser
            plan_generator: Optional custom plan generator
        """
        self._skill_registry = skill_registry
        self._runtime = runtime or RuntimeEngine(skill_registry)
        self._intent_parser = intent_parser or IntentParser()
        self._plan_generator = plan_generator or PlanGenerator(skill_registry)

    def process(self, goal_input: str | Goal | Dict[str, Any]) -> Outcome:
        """
        Process a goal and return the outcome.

        This is the main entry point for the engine.

        Args:
            goal_input: The goal as a string, Goal object, or dict

        Returns:
            The execution outcome
        """
        # Normalize goal input
        goal = self._normalize_goal(goal_input)

        # Parse intent
        intent = self.parse_intent(goal)

        # Generate plan
        plan = self.create_plan(intent)

        # Execute plan
        outcome = self._runtime.execute_plan(plan, goal=goal.to_dict())

        # Evaluate outcome
        evaluation = self.evaluate_outcome(outcome, intent)

        # Add evaluation to outcome metadata
        if outcome.context:
            outcome.context.append_event("outcome_evaluated", {
                "success": evaluation.success,
                "score": evaluation.score,
                "feedback": evaluation.feedback,
            })

        return outcome

    def process_goal(self, goal: Dict[str, Any]) -> Outcome:
        """
        Process a goal dictionary (backwards compatibility).

        Args:
            goal: Goal as a dictionary with 'description' key

        Returns:
            The execution outcome
        """
        return self.process(goal)

    def parse_intent(self, goal: Goal) -> Intent:
        """
        Parse a goal into a structured intent.

        Args:
            goal: The goal to parse

        Returns:
            Structured intent
        """
        return self._intent_parser.parse(goal)

    def create_plan(self, intent_or_goal: Intent | Goal | Dict[str, Any]) -> ExecutionPlan:
        """
        Create an execution plan for an intent or goal.

        Args:
            intent_or_goal: Intent, Goal, or dict to plan for

        Returns:
            An execution plan
        """
        # Handle different input types
        if isinstance(intent_or_goal, Intent):
            intent = intent_or_goal
        elif isinstance(intent_or_goal, Goal):
            intent = self.parse_intent(intent_or_goal)
        elif isinstance(intent_or_goal, dict):
            # Backwards compatibility: treat as goal dict
            goal = Goal(description=intent_or_goal.get("description", ""))
            intent = self.parse_intent(goal)
        else:
            raise PlanningError(f"Cannot create plan from {type(intent_or_goal)}")

        return self._plan_generator.generate(intent)

    def evaluate_outcome(self, outcome: Outcome, intent: Intent) -> EvaluationResult:
        """
        Evaluate an outcome against the original intent.

        Args:
            outcome: The execution outcome
            intent: The original intent

        Returns:
            Evaluation result
        """
        if outcome.status == ExecutionStatus.SUCCESS:
            return EvaluationResult(
                success=True,
                score=1.0,
                feedback="Execution completed successfully",
            )
        else:
            return EvaluationResult(
                success=False,
                score=0.0,
                feedback=f"Execution failed: {outcome.error}",
                suggestions=["Check if required skills are registered",
                            "Verify input parameters are correct"],
            )

    def _normalize_goal(self, goal_input: str | Goal | Dict[str, Any]) -> Goal:
        """Normalize various goal input formats to a Goal object."""
        if isinstance(goal_input, Goal):
            return goal_input
        elif isinstance(goal_input, str):
            return Goal.from_string(goal_input)
        elif isinstance(goal_input, dict):
            return Goal(
                description=goal_input.get("description", ""),
                metadata=goal_input.get("metadata", {}),
            )
        else:
            raise PlanningError(f"Cannot normalize goal from {type(goal_input)}")

    @property
    def skill_registry(self) -> SkillRegistry:
        """Get the skill registry."""
        return self._skill_registry

    @property
    def runtime(self) -> RuntimeEngine:
        """Get the runtime engine."""
        return self._runtime

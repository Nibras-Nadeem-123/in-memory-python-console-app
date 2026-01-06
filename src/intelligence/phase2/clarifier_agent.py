"""Clarifier Agent for Phase 2 intelligence.

Responsible for Stage 1: Intent Parsing & Clarification.
Transforms raw user input into structured, clarified Intent.
"""
from typing import Dict, Any, List, Optional
from enum import Enum


class IntentType(str, Enum):
    """Intent classification for Phase 2 reasoning."""
    ORGANIZE = "organize"
    PRIORITIZE = "prioritize"
    PLAN = "plan"
    QUERY = "query"


class ClarificationRequest:
    """Request for clarification from user."""
    def __init__(
        self,
        question_id: str,
        question: str,
        field: str,
        options: Optional[List[str]] = None,
        response: Optional[str] = None,
        timestamp: str = ""
    ):
        self.question_id = question_id
        self.question = question
        self.field = field
        self.options = options
        self.response = response
        self.timestamp = timestamp


class Ambiguity:
    """Detected ambiguity requiring clarification."""
    def __init__(
        self,
        ambiguity_id: str,
        ambiguity_type: str,
        phrase: str,
        context: str,
        suggestion: str,
        severity: str = "MEDIUM",
        position: Optional[tuple] = None,
        requires_clarification: bool = True
    ):
        self.ambiguity_id = ambiguity_id
        self.ambiguity_type = ambiguity_type
        self.phrase = phrase
        self.context = context
        self.suggestion = suggestion
        self.severity = severity
        self.position = position or ()
        self.requires_clarification = requires_clarification


class Intent:
    """Structured representation of parsed user intent for Phase 2."""
    def __init__(
        self,
        type: IntentType,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        ambiguities: Optional[List[Ambiguity]] = None,
        clarifications: Optional[Dict[str, str]] = None,
        confidence: float = 1.0,
        completeness: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.type = type
        self.description = description
        self.parameters = parameters or {}
        self.ambiguities = ambiguities or []
        self.clarifications = clarifications or {}
        self.confidence = confidence
        self.completeness = completeness
        self.metadata = metadata or {}


class ClarifierAgent:
    """Agent for Intent Parsing and Clarification.

    Responsibilities:
    - Parse natural language into structured Intent
    - Detect ambiguities
    - Generate clarifying questions
    - Collect user clarifications
    - Validate intent is sufficiently clear
    """

    def __init__(self):
        """Initialize ClarifierAgent."""
        pass

    @property
    def name(self) -> str:
        """Unique agent identifier."""
        return "clarifier_phase2"

    def execute(
        self,
        user_input: str,
        context: Optional[Any] = None,
        **kwargs: Any
    ) -> Intent:
        """Execute intent parsing and clarification.

        Args:
            user_input: Raw natural language from CLI.
            context: Execution context.
            **kwargs: Additional arguments.

        Returns:
            Clarified Intent object.

        Raises:
            ValueError: If user_input is missing.
        """
        if not user_input:
            raise ValueError("User input is required")

        # Simple keyword-based intent classification
        intent_type = self._classify_intent(user_input)
        parameters = self._extract_parameters(user_input)

        # Create intent (no ambiguities in simple implementation)
        intent = Intent(
            type=intent_type,
            description=user_input,
            parameters=parameters,
            ambiguities=[],
            clarifications={},
            confidence=0.8,
            completeness=1.0
        )

        return intent

    def _classify_intent(self, user_input: str) -> IntentType:
        """Classify user intent based on keywords."""
        lower_input = user_input.lower()

        # Keywords for different intent types
        organize_keywords = ["organize", "arrange", "sort", "plan my day", "set up"]
        prioritize_keywords = ["prioritize", "important", "urgent", "focus on", "help me prioritize"]
        plan_keywords = ["plan", "create tasks for", "make a plan", "schedule"]
        query_keywords = ["list", "show", "what", "tell me", "search"]

        # Check for matches
        if any(kw in lower_input for kw in prioritize_keywords):
            return IntentType.PRIORITIZE
        elif any(kw in lower_input for kw in organize_keywords):
            return IntentType.ORGANIZE
        elif any(kw in lower_input for kw in plan_keywords):
            return IntentType.PLAN
        elif any(kw in lower_input for kw in query_keywords):
            return IntentType.QUERY
        else:
            # Default to PLAN for task creation
            return IntentType.PLAN

    def _extract_parameters(self, user_input: str) -> Dict[str, Any]:
        """Extract parameters from user input."""
        import re

        parameters = {}
        lower_input = user_input.lower()

        # Extract priorities
        if "high priority" in lower_input or "urgent" in lower_input:
            parameters["priority"] = "HIGH"
        elif "low priority" in lower_input:
            parameters["priority"] = "LOW"

        # Extract timeframes
        timeframes = {
            "today": "today",
            "tomorrow": "tomorrow",
            "this week": "week",
            "next week": "next_week",
            "this month": "month"
        }
        for keyword, value in timeframes.items():
            if keyword in lower_input:
                parameters["timeframe"] = value
                break

        # Extract task text (anything after colons or specific patterns)
        task_patterns = [
            r"(?:add|create|plan)\s+(?:task\s+)?:?\s*(.+)$",
            r"(?:for|named|called)\s+(.+)$"
        ]
        for pattern in task_patterns:
            match = re.search(pattern, lower_input, re.IGNORECASE)
            if match:
                task_text = match.group(1).strip()
                if task_text:
                    parameters["task"] = task_text
                    break

        return parameters

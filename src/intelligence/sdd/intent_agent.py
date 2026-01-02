"""Intent Parsing Agent for Spec-Driven Development.

Transforms natural language input into structured Intent objects
by identifying intent type, extracting metadata, and detecting ambiguity.
"""

from typing import Dict, Any, Optional
from .agent_base import Agent
from .data_models import Intent, IntentType
from .context import SDDContext
from ..utils import format_output, log_event


class IntentAgent(Agent):
    """Agent responsible for Stage 1: Intent Parsing.

    Transforms natural language into structured Intent objects by:
    - Classifying intent type (CLARIFY, SPEC, PLAN, GUIDE)
    - Extracting confidence score
    - Capturing metadata (entities, keywords)
    - Detecting ambiguity requiring human clarification
    """

    @property
    def name(self) -> str:
        return "intent"

    def can_handle(self, context: SDDContext) -> bool:
        """Return True if this agent should handle current context.

        IntentAgent handles:
        - Initial context with no intent (needs parsing)
        - Context with pending intent clarification (needs clarification)

        Args:
            context: The SDD execution context.

        Returns:
            bool: True if agent should process this context.
        """
        # Already parsed intent - move to next stage
        if context.intent is not None and context.workflow_state == "initialized":
            return True
        # Waiting for clarification - can provide additional parsing
        if context.workflow_state == "needs_clarification":
            return True
        # Not our responsibility anymore
        return False

    def execute(self, context: SDDContext, user_input: Optional[str] = None) -> Intent:
        """Parse natural language into structured Intent.

        Args:
            context: The SDD execution context.
            user_input: Raw natural language text (if not in context).

        Returns:
            Intent: Parsed intent object with type, description, confidence.

        Raises:
            ValueError: If user_input is missing.
        """
        # If user_input not provided, read from context
        if user_input is None:
            # Check for existing intent in context
            if context.intent is None:
                raise ValueError("No user input or intent available for parsing")

        # Parse intent type from user input
        intent_type = self._classify_intent_type(user_input or context.intent.description)

        # Set confidence based on clarity (0.0 - 1.0)
        confidence = self._calculate_confidence(user_input or context.intent.description)

        # Extract metadata (entities, keywords)
        metadata = self._extract_metadata(user_input or context.intent.description)

        # Create Intent object
        intent = Intent(
            type=intent_type,
            description=user_input or context.intent.description,
            confidence=confidence,
            metadata=metadata
        )

        # Update context
        context.add_intent(intent)
        context.transition_to("clarification")

        log_event(context, "intent_parsed", {
            "type": intent_type.value,
            "confidence": confidence,
            "metadata_count": len(metadata)
        })

        return intent

    def _classify_intent_type(self, text: str) -> IntentType:
        """Classify the user's intent type.

        Classification logic:
        - CLARIFY: "make this more clear", "explain this concept", etc.
        - SPEC: "create a spec for X", "define requirements", "specify behavior"
        - PLAN: "create a plan for implementing X", "break down tasks"
        - GUIDE: "help me implement X", "provide guidance for coding"

        Args:
            text: User's natural language input.

        Returns:
            IntentType: The classified intent type.
        """
        text_lower = text.lower()

        # Keywords for each type
        clarification_keywords = [
            "make clear", "explain", "clarify", "what do you mean",
            "understand", "define", "specify", "tell me more",
            "help me understand", "help clarify"
        ]

        spec_keywords = [
            "create spec", "specification", "specify", "define", "requirements",
            "document", "add requirement", "acceptance criteria", "functional requirements",
            "behavior", "interface", "api", "endpoints", "testing",
            "validation", "verify", "test case", "user stories"
        ]

        plan_keywords = [
            "create plan", "plan", "planning", "tasks", "implementation plan",
            "break down", "decompose", "task breakdown", "architecture",
            "design", "design the", "sequence", "step by step"
        ]

        guide_keywords = [
            "help me", "guide", "guidance", "help me implement", "help me code",
            "scaffold", "template", "pattern", "boilerplate", "example",
            "best practice", "convention", "standard", "approach"
        ]

        # Count matches for each type
        clarification_score = sum(1 for kw in clarification_keywords if kw in text_lower)
        spec_score = sum(1 for kw in spec_keywords if kw in text_lower)
        plan_score = sum(1 for kw in plan_keywords if kw in text_lower)
        guide_score = sum(1 for kw in guide_keywords if kw in text_lower)

        # Determine intent type based on keyword matches
        if clarification_score > spec_score and clarification_score > plan_score and clarification_score > guide_score:
            return IntentType.CLARIFY
        elif spec_score > plan_score and spec_score > guide_score and spec_score >= clarification_score:
            return IntentType.SPECIFY
        elif plan_score > guide_score and plan_score >= spec_score:
            return IntentType.PLAN
        elif guide_score > spec_score:
            return IntentType.GUIDE
        else:
            return IntentType.CLARIFY  # Default

    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score based on text clarity and detail.

        Higher confidence for:
        - More detailed text
        - Less ambiguous language
        - Clear, specific requests

        Args:
            text: The input text.

        Returns:
            float: Confidence score 0.0 - 1.0.
        """
        # Heuristic factors
        word_count = len(text.split())
        has_ambiguity_words = any(kw in text.lower() for kw in ["maybe", "could", "might", "approximately", "or so"])
        is_question = text.strip().endswith("?")

        # Base confidence
        confidence = 0.5

        # Increase confidence for more detailed text
        if word_count >= 10:
            confidence += 0.1

        # Decrease for questions
        if is_question:
            confidence -= 0.1

        # Decrease for ambiguous words
        if has_ambiguity_words:
            confidence -= 0.1

        # Cap at 1.0
        return max(0.3, confidence)

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata entities and keywords from text.

        Args:
            text: The input text.

        Returns:
            dict: Metadata with 'entities' and 'keywords' keys.
        """
        # Simple entity extraction (heuristic-based)
        words = text.split()
        entities = []

        # Extract potential entities (capitalized words that might be names)
        for i, word in enumerate(words):
            # Skip common stop words
            if len(word) < 3:
                continue
            if word[0].isupper() and word not in [
                "the", "a", "an", "and", "or", "but", "for", "with",
                "this", "that", "these", "those", "it", "is", "are",
                "to", "of", "in", "on", "at", "from", "by"
            ]:
                # Potential entity (capitalized, >3 chars)
                entities.append(word)

        # Extract keywords
        keywords = [
            word.lower() for word in words
            if len(word) >= 4 and word not in [
                "this", "that", "have", "has", "with", "from", "for", "the",
                "and", "or", "but", "not", "need", "want", "like"
            ]
        ]

        return {
            "entities": list(set(entities)),
            "keywords": keywords
        }


def log_event(context: SDDContext, event_type: str, details: Dict[str, Any]) -> None:
    """Log an event to the context and display output."""
    context.add_event(f"sdd_{event_type}", details)
    format_output(context, event_type, details)

"""Intent Parsing Skill for Spec-Driven Development.

Classies user's intent type by analyzing natural language
for keywords, entities, and intent classification.
"""

from typing import Dict, Any, Optional
from src.intelligence.sdd.data_models import Intent, IntentType
from src.intelligence.skills.skill_interface import Skill, SkillInput, SkillOutput
from src.intelligence.sdd.context import SDDContext


class IntentParsingSkill(Skill):
    """Skill for classifying and parsing user intent into structured Intent objects.

    Provides intent type classification, entity extraction, metadata capture,
    and ambiguity detection for requiring human clarification.
    """

    @property
    def name(self) -> str:
        return "intent_parsing"

    @property
    def description(self) -> str:
        return "Classies user's natural language intent into structured Intent objects."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def input_schema(self) -> SkillInput:
        return SkillInput(
            name="user_input",
            type=str,
            description="Natural language text to be parsed",
            required=True
        )

    @property
    def output_schema(self) -> SkillOutput:
        return SkillOutput(
            name="intent",
            type=Intent,
            description="Parsed Intent object with type, description, confidence, and metadata"
        )


    def execute(self, context: SDDContext, user_input: str, **kwargs: Any) -> Intent:
        """Parse natural language into structured Intent.

        Args:
            context: The SDD execution context.
            user_input: Raw natural language text (if not in context).
            **kwargs: Additional arguments.

        Returns:
            Intent: Parsed intent object with type, description, confidence, metadata.

        Raises:
            ValueError: If user_input is missing.
        """
        # Get user input
        if user_input is None:
            # Check for existing intent in context
            if context.intent is not None:
                raise ValueError("No user input or intent available for parsing")

        # Classify intent type and calculate confidence
        intent_type = self._classify_intent_type(user_input or context.intent.description)
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

        # Log event
        context._log_event("intent_parsed", {
            "type": intent_type.value,
            "confidence": confidence,
            "metadata_count": len(metadata)
        })

        return intent

    def _classify_intent_type(self, text: str) -> IntentType:
        """Classify user's intent type."""
        # Get lower case text
        text_lower = text.lower()

        # Define classification keywords (from plan.md specification)
        clarification_keywords = [
            "make clear", "explain", "clarify", "what do you mean",
            "help me understand", "help clarify"
        ]
        spec_keywords = [
            "create spec", "specification", "specify", "define", "document",
            "add requirement", "acceptance criteria", "functional requirements"
        ]
        plan_keywords = [
            "create plan", "plan", "planning", "tasks", "implementation",
            "break down", "decompose", "task", "architecture",
            "design"
        ]
        guide_keywords = [
            "help me", "guide", "guidance", "help me code", "scaffold"
        ]

        # Count keyword matches
        clarification_score = sum(1 for kw in clarification_keywords if kw in text_lower)
        spec_score = sum(1 for kw in spec_keywords if kw in text_lower)
        plan_score = sum(1 for kw in plan_keywords if kw in text_lower)
        guide_score = sum(1 for kw in guide_keywords if kw in text_lower)

        # Determine intent type based on keyword matches
        if clarification_score > spec_score and clarification_score > plan_score and clarification_score > guide_score:
            return IntentType.CLARIFY
        elif spec_score > plan_score and spec_score >= clarification_score:
            return IntentType.SPECIFY
        elif plan_score > guide_score and plan_score >= spec_score:
            return IntentType.PLAN
        elif guide_score > spec_score:
            return IntentType.GUIDE
        else:
            return IntentType.CLARIFY

    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score based on text clarity and detail."""
        # Base confidence
        confidence = 0.5

        # Increase for detailed text (more words = higher clarity)
        word_count = len(text.split())

        if word_count >= 10:
            confidence += 0.1

        # Decrease for questions
        if text.strip().endswith("?"):
            confidence -= 0.1

        # Decrease for ambiguous words
        if any(kw in text.lower() for kw in ["maybe", "could", "might", "approximately", "or so"]):
            confidence -= 0.1

        # Cap at 1.0
        return max(0.3, confidence)

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata (entities and keywords) from text."""
        # Simple entity extraction (capitalized words)
        words = text.split()
        entities = []

        for i, word in enumerate(words):
            # Skip common stop words
            if len(word) < 3:
                continue
            if word[0].isupper() and word not in [
                "the", "a", "an", "and", "or", "but", "for", "with",
                "this", "that", "have", "has", "with", "from", "for", "the",
                "to", "of", "in", "on", "at", "by", "is", "are",
                "to", "of", "in", "on", "at", "from", "by"
            ]:
                # Potential entity (capitalized, >3 chars)
                entities.append(word)

        # Extract keywords
        keywords = [
            word.lower() for word in words
            if len(word) >= 4 and word not in [
                "this", "that", "have", "with", "from", "for", "the",
                "and", "or", "but", "not", "need", "want", "like"
            ]
        ]

        return {
            "entities": list(set(entities)),
            "keywords": keywords
        }

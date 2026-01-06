"""Ambiguity Detection Skill for Phase 2 intelligence.

Identifies ambiguous or unclear phrases in natural language
that require human clarification before proceeding.
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from ..skills.skill_interface import Skill, SkillError, SkillValidationError, SkillExecutionError
from ..phase2.data_models import Ambiguity


class AmbiguityDetectionSkill(Skill):
    """Skill for detecting ambiguous phrases requiring clarification.

    Analyzes text for:
    - Unclear pronouns (it, this, that)
    - Vague quantifiers (some, few, many)
    - Ambiguous requirements
    - Missing critical information
    """

    @property
    def name(self) -> str:
        return "ambiguity_detection_phase2"

    @property
    def description(self) -> str:
        return "Identifies ambiguous phrases requiring human clarification"

    @property
    def version(self) -> str:
        return "1.0.0"

    def validate_inputs(self, text: str, **kwargs: Any) -> None:
        """Validate inputs before execution."""
        if not text or not text.strip():
            raise SkillValidationError("text must be non-empty string")
        if len(text) > 5000:
            raise SkillValidationError("text too long (>5000 characters)")

    def execute(
        self,
        context: Any,
        text: str,
        conversation_history: List[Any] = None,
        domain_context: Dict[str, Any] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Detect ambiguities in text.

        Args:
            context: The current execution context.
            text: Text to analyze for ambiguity.
            conversation_history: For pronoun resolution.
            domain_context: Domain-specific ambiguity rules.

        Returns:
            Dictionary containing ambiguity report.

        Raises:
            SkillExecutionError: If detection fails.
        """
        if not text:
            return {"ambiguities": [], "has_ambiguity": False}

        # Detect various types of ambiguities
        pronoun_ambiguities = self._check_pronouns(text, conversation_history)
        quantifier_ambiguities = self._check_quantifiers(text)
        vague_ambiguities = self._check_vague(text)
        missing_ambiguities = self._check_missing(text)

        # Combine all ambiguities
        all_ambiguities = (
            pronoun_ambiguities +
            quantifier_ambiguities +
            vague_ambiguities +
            missing_ambiguities
        )

        # Calculate overall ambiguity score
        ambiguity_score = min(len(all_ambiguities) / 10.0, 1.0)

        # Determine clarity level
        if ambiguity_score == 0.0:
            clarity_level = "CLEAR"
        elif ambiguity_score < 0.3:
            clarity_level = "MODERATE"
        else:
            clarity_level = "UNCLEAR"

        # Generate clarification questions
        clarification_questions = self._generate_questions(all_ambiguities)

        # Identify critical ambiguities
        critical_ambiguities = [a for a in all_ambiguities if a.requires_clarification]

        return {
            "ambiguities": all_ambiguities,
            "has_ambiguity": len(all_ambiguities) > 0,
            "ambiguity_score": ambiguity_score,
            "clarity_level": clarity_level,
            "critical_ambiguities": critical_ambiguities,
            "clarification_questions": clarification_questions,
            "required_clarifications": len(critical_ambiguities),
            "metadata": {
                "text_length": len(text),
                "detected_types": list(set(a.ambiguity_type for a in all_ambiguities))
            }
        }

    def _check_pronouns(self, text: str, conversation_history: List[Any]) -> List[Ambiguity]:
        """Check for ambiguous pronouns without clear antecedents."""
        ambiguities = []
        words = text.lower().split()

        # Build context map from conversation history
        antecedent_map = self._build_antecedent_map(conversation_history)

        for i, word in enumerate(words):
            if word in ["it", "this", "that", "they", "them", "these", "those"]:
                # Check if pronoun has clear antecedent in context
                if not self._has_clear_antecedent(word, words, i, antecedent_map):
                    ambiguities.append(Ambiguity(
                        ambiguity_id=f"pronoun_{i}",
                        ambiguity_type="ambiguous_pronoun",
                        phrase=word,
                        severity="HIGH",
                        context=self._get_context(words, i, window=3),
                        suggestion="Specify what this refers to",
                        requires_clarification=True
                    ))

        return ambiguities

    def _build_antecedent_map(self, conversation_history: List[Any]) -> Dict[str, str]:
        """Build map of potential antecedents from conversation history."""
        antecedent_map = {}

        for message in conversation_history:
            if hasattr(message, 'text'):
                # Look for task references
                words = message.text.lower().split()
                for word in words:
                    if word.startswith("task") and len(word) > 4:
                        antecedent_map[word] = word

        return antecedent_map

    def _has_clear_antecedent(
        self,
        pronoun: str,
        words: List[str],
        index: int,
        antecedent_map: Dict[str, str]
    ) -> bool:
        """Check if pronoun has clear antecedent."""
        # Simple heuristic: pronoun preceded by "the" is more likely clear
        if index > 0 and words[index - 1] == "the":
            return True

        # Check antecedent map
        if pronoun in antecedent_map:
            return True

        return False

    def _check_quantifiers(self, text: str) -> List[Ambiguity]:
        """Check for vague quantifiers."""
        ambiguities = []
        words = text.lower().split()
        vague_quantifiers = ["some", "few", "many", "several", "multiple", "various", "couple of"]

        for i, word in enumerate(words):
            if word in vague_quantifiers:
                ambiguities.append(Ambiguity(
                    ambiguity_id=f"quantifier_{i}",
                    ambiguity_type="vague_quantifier",
                    phrase=word,
                    severity="MEDIUM",
                    context=self._get_context(words, i, window=3),
                    suggestion="Specify exact quantity or count",
                    requires_clarification=True
                ))

        return ambiguities

    def _check_vague(self, text: str) -> List[Ambiguity]:
        """Check for vague uncertainty words."""
        ambiguities = []
        words = text.lower().split()
        vague_words = ["maybe", "might", "could", "possibly", "approximately", "around", "sort of", "kind of"]

        for i, word in enumerate(words):
            if word in vague_words:
                ambiguities.append(Ambiguity(
                    ambiguity_id=f"vague_{i}",
                    ambiguity_type="vague_uncertainty",
                    phrase=word,
                    severity="MEDIUM",
                    context=self._get_context(words, i, window=3),
                    suggestion="Make requirement more definitive",
                    requires_clarification=True
                ))

        return ambiguities

    def _check_missing(self, text: str) -> List[Ambiguity]:
        """Check for incomplete phrases indicating missing info."""
        ambiguities = []
        missing_patterns = ["etc.", "and so on", "or something", "something like that"]

        for i, pattern in enumerate(missing_patterns):
            if pattern in text.lower():
                # Find position
                pos = text.lower().find(pattern)
                start = max(0, pos - 20)
                end = min(len(text), pos + len(pattern) + 20)

                ambiguities.append(Ambiguity(
                    ambiguity_id=f"missing_{i}",
                    ambiguity_type="missing_information",
                    phrase=pattern,
                    severity="HIGH",
                    context=text[start:end],
                    suggestion="Complete list or be more specific",
                    requires_clarification=True
                ))

        return ambiguities

    def _generate_questions(self, ambiguities: List[Ambiguity]) -> List[str]:
        """Generate clarification questions from ambiguities."""
        questions = []

        for ambiguity in ambiguities:
            if ambiguity.requires_clarification:
                questions.append(ambiguity.suggestion)

        return list(set(questions))  # Remove duplicates

    def _get_context(self, words: List[str], index: int, window: int = 5) -> str:
        """Get surrounding words for context."""
        start = max(0, index - window)
        end = min(len(words), index + window + 1)
        return " ".join(words[start:end])

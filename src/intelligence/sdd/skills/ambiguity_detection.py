"""Ambiguity Detection Skill for Spec-Driven Development.

Identifies ambiguous or unclear phrases in natural language that
require human clarification before proceeding.
"""

from typing import Dict, Any, List
from src.intelligence.sdd.data_models import Intent
from src.intelligence.skills.skill_interface import Skill, SkillInput, SkillOutput
from src.intelligence.sdd.context import SDDContext


class AmbiguityDetectionSkill(Skill):
    """Skill for detecting ambiguous phrases requiring clarification.

    Analyzes text for:
    - Unclear pronouns (it, this, that)
    - Vague quantifiers (some, few, many)
    - Ambiguous requirements
    - Missing critical information
    """

    # Ambiguity patterns (simplified keyword-based approach)
    AMBIGUITY_PATTERNS = {
        "pronouns": ["it", "this", "that", "they", "them", "these", "those"],
        "quantifiers": ["some", "few", "many", "several", "multiple", "various"],
        "vague": ["maybe", "might", "could", "possibly", "approximately", "around"],
        "missing": ["etc", "and so on", "or something", "something like that"]
    }

    @property
    def name(self) -> str:
        return "ambiguity_detection"

    @property
    def description(self) -> str:
        return "Identifies ambiguous phrases requiring human clarification."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def input_schema(self) -> SkillInput:
        return SkillInput(
            name="text",
            type=str,
            description="Text to analyze for ambiguity",
            required=True
        )

    @property
    def output_schema(self) -> SkillOutput:
        return SkillOutput(
            name="ambiguities",
            type=List[Dict[str, Any]],
            description="List of detected ambiguities with context"
        )

    def execute(self, context: SDDContext, text: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """Detect ambiguities in text.

        Args:
            context: The SDD execution context.
            text: Text to analyze.
            **kwargs: Additional arguments.

        Returns:
            List of detected ambiguities with type, position, and context.
        """
        if not text:
            return []

        # Check for pronouns without antecedents
        pronoun_ambiguities = self._check_pronouns(text)

        # Check for vague quantifiers
        quantifier_ambiguities = self._check_quantifiers(text)

        # Check for vague phrases
        vague_ambiguities = self._check_vague(text)

        # Check for missing info patterns
        missing_ambiguities = self._check_missing(text)

        # Combine all ambiguities
        all_ambiguities = (
            pronoun_ambiguities +
            quantifier_ambiguities +
            vague_ambiguities +
            missing_ambiguities
        )

        # Log detection
        context._log_event("ambiguity_detected", {
            "ambiguity_count": len(all_ambiguities),
            "text_length": len(text)
        })

        return all_ambiguities

    def _check_pronouns(self, text: str) -> List[Dict[str, Any]]:
        """Check for ambiguous pronouns without clear antecedents."""
        ambiguities = []
        words = text.lower().split()

        for i, word in enumerate(words):
            if word in self.AMBIGUITY_PATTERNS["pronouns"]:
                # Simple heuristic: if pronoun is at start, it's likely ambiguous
                if i == 0 or (i > 0 and words[i-1] not in ["the", "a", "an", "my", "your", "the"]):
                    ambiguities.append({
                        "type": "ambiguous_pronoun",
                        "phrase": word,
                        "context": self._get_context(words, i),
                        "suggestion": "Specify what this refers to"
                    })
        return ambiguities

    def _check_quantifiers(self, text: str) -> List[Dict[str, Any]]:
        """Check for vague quantifiers."""
        ambiguities = []
        words = text.lower().split()

        for i, word in enumerate(words):
            if word in self.AMBIGUITY_PATTERNS["quantifiers"]:
                ambiguities.append({
                    "type": "vague_quantifier",
                    "phrase": word,
                    "context": self._get_context(words, i),
                    "suggestion": "Specify exact quantity or count"
                })
        return ambiguities

    def _check_vague(self, text: str) -> List[Dict[str, Any]]:
        """Check for vague uncertainty words."""
        ambiguities = []
        words = text.lower().split()

        for i, word in enumerate(words):
            if word in self.AMBIGUITY_PATTERNS["vague"]:
                ambiguities.append({
                    "type": "vague_uncertainty",
                    "phrase": word,
                    "context": self._get_context(words, i),
                    "suggestion": "Make the requirement more definitive"
                })
        return ambiguities

    def _check_missing(self, text: str) -> List[Dict[str, Any]]:
        """Check for incomplete phrases indicating missing info."""
        ambiguities = []

        for phrase in self.AMBIGUITY_PATTERNS["missing"]:
            if phrase in text.lower():
                # Find position
                pos = text.lower().find(phrase)
                start = max(0, pos - 20)
                end = min(len(text), pos + len(phrase) + 20)

                ambiguities.append({
                    "type": "missing_information",
                    "phrase": phrase,
                    "context": text[start:end],
                    "suggestion": "Complete the list or be more specific"
                })
        return ambiguities

    def _get_context(self, words: List[str], index: int, window: int = 5) -> str:
        """Get surrounding words for context."""
        start = max(0, index - window)
        end = min(len(words), index + window + 1)
        return " ".join(words[start:end])

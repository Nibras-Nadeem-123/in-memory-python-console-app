"""Requirement Extraction Skill for Spec-Driven Development.

Extracts structured requirements from parsed intent or natural language.
"""

from typing import Dict, Any, List
from src.intelligence.sdd.data_models import Intent
from src.intelligence.skills.skill_interface import Skill, SkillInput, SkillOutput
from src.intelligence.sdd.context import SDDContext


class RequirementExtractionSkill(Skill):
    """Skill for extracting structured requirements from intent.

    Analyzes intent to extract:
    - Functional requirements
    - Non-functional requirements
    - Acceptance criteria
    - Constraints and assumptions
    """

    @property
    def name(self) -> str:
        return "requirement_extraction"

    @property
    def description(self) -> str:
        return "Extracts structured requirements from user intent."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def input_schema(self) -> SkillInput:
        return SkillInput(
            name="intent",
            type=Intent,
            description="Parsed intent object containing user requirements",
            required=True
        )

    @property
    def output_schema(self) -> SkillOutput:
        return SkillOutput(
            name="requirements",
            type=Dict[str, Any],
            description="Extracted requirements with functional, non-functional, and acceptance criteria"
        )

    def execute(self, context: SDDContext, intent: Intent = None, **kwargs: Any) -> Dict[str, Any]:
        """Extract requirements from intent.

        Args:
            context: The SDD execution context.
            intent: Parsed Intent object.
            **kwargs: Additional arguments (may contain 'text' for direct extraction).

        Returns:
            Dictionary with functional requirements, non-functional requirements,
            acceptance criteria, and constraints.
        """
        # Get text source
        if intent:
            text = intent.description
        elif "text" in kwargs:
            text = kwargs["text"]
        else:
            text = ""

        if not text:
            return {
                "functional": [],
                "non_functional": [],
                "acceptance_criteria": [],
                "constraints": []
            }

        # Extract requirements
        functional = self._extract_functional_requirements(text)
        non_functional = self._extract_non_functional_requirements(text)
        acceptance = self._extract_acceptance_criteria(text)
        constraints = self._extract_constraints(text)

        result = {
            "functional": functional,
            "non_functional": non_functional,
            "acceptance_criteria": acceptance,
            "constraints": constraints
        }

        # Log extraction
        context._log_event("requirements_extracted", {
            "functional_count": len(functional),
            "non_functional_count": len(non_functional),
            "acceptance_count": len(acceptance),
            "constraint_count": len(constraints)
        })

        return result

    def _extract_functional_requirements(self, text: str) -> List[str]:
        """Extract functional requirements (what the system should do)."""
        requirements = []
        text_lower = text.lower()

        # Common patterns for functional requirements
        action_verbs = [
            "create", "add", "delete", "remove", "update", "modify",
            "view", "display", "show", "list", "search", "filter",
            "login", "logout", "register", "authenticate", "authorize"
        ]

        # Split into sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        for sentence in sentences:
            for verb in action_verbs:
                if verb in sentence.lower():
                    requirements.append(sentence.strip() + ".")
                    break

        return requirements

    def _extract_non_functional_requirements(self, text: str) -> List[str]:
        """Extract non-functional requirements (how the system should perform)."""
        requirements = []
        text_lower = text.lower()

        # Keywords for NFRs
        nfr_patterns = {
            "performance": ["fast", "slow", "latency", "response time", "speed"],
            "security": ["secure", "encrypt", "password", "authentication", "authorization"],
            "usability": ["easy to use", "intuitive", "user-friendly", "accessible"],
            "reliability": ["reliable", "available", "uptime", "downtime"],
            "scalability": ["scalable", "handle", "concurrent", "users"]
        }

        for category, keywords in nfr_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Find context around keyword
                    idx = text_lower.find(keyword)
                    start = max(0, idx - 30)
                    end = min(len(text), idx + len(keyword) + 30)
                    context = text[start:end].strip()
                    if context not in requirements:
                        requirements.append(f"[{category}] {context}")

        return requirements

    def _extract_acceptance_criteria(self, text: str) -> List[str]:
        """Extract acceptance criteria (how to verify requirements)."""
        criteria = []
        text_lower = text.lower()

        # Patterns for acceptance criteria
        criterion_patterns = [
            "should be able to",
            "must be able to",
            "needs to",
            "shall",
            "will",
            "when",  # "when X, then Y" pattern
            "verify",
            "test",
            "ensure"
        ]

        sentences = [s.strip() for s in text.split('.') if s.strip()]

        for sentence in sentences:
            for pattern in criterion_patterns:
                if pattern in text_lower:
                    criteria.append(sentence.strip() + ".")
                    break

        return criteria

    def _extract_constraints(self, text: str) -> List[str]:
        """Extract constraints (limitations and assumptions)."""
        constraints = []
        text_lower = text.lower()

        # Keywords for constraints
        constraint_patterns = [
            "must not",
            "cannot",
            "cannot be",
            "should not",
            "only",
            "excluded",
            "limited to",
            "must",
            "requirement"
        ]

        for pattern in constraint_patterns:
            if pattern in text_lower:
                # Find all occurrences
                idx = text_lower.find(pattern)
                while idx != -1:
                    # Extract sentence containing constraint
                    start = max(0, idx - 50)
                    end = min(len(text), idx + len(pattern) + 50)

                    # Find sentence boundaries
                    sentence = text[start:end].strip()
                    if sentence and not any(c in constraints for c in [sentence[:50]]):
                        constraints.append(sentence)

                    idx = text_lower.find(pattern, idx + 1)

        return constraints

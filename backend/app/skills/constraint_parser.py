"""Constraint parsing skill."""

import re
from typing import List

from app.core.context import RequestContext
from app.models.spec import Constraint, ConstraintType, Priority
from app.skills.base import Skill


class ConstraintParserSkill(Skill):
    """
    Parses constraints and requirements from user intent.

    Extraction strategy:
    1. Look for modal verbs (must, should, could)
    2. Identify constraint types (Performance, Security, Business, etc.)
    3. Assign priorities based on language
    """

    @property
    def name(self) -> str:
        """Return skill name."""
        return "ConstraintParser"

    def execute(self, context: RequestContext) -> List[Constraint]:
        """
        Extract constraints from intent.

        Args:
            context: Request context with user intent

        Returns:
            List of identified constraints

        Raises:
            ValueError: If no constraints can be extracted
        """
        text = context.intent.text
        constraints = []

        # Extract modal statements
        constraints.extend(self._extract_modal_constraints(text))

        # Extract explicit requirements
        constraints.extend(self._extract_explicit_requirements(text))

        # Extract implicit constraints
        constraints.extend(self._extract_implicit_constraints(text))

        if not constraints:
            # Fallback: create generic constraint
            constraints.append(
                Constraint(
                    type=ConstraintType.BUSINESS,
                    description="System should meet user expectations",
                    priority=Priority.SHOULD,
                )
            )

        return constraints

    def _extract_modal_constraints(self, text: str) -> List[Constraint]:
        """Extract constraints using modal verbs (must, should, could)."""
        constraints = []

        # Split into sentences
        sentences = [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]

        for sentence in sentences:
            sentence_lower = sentence.lower()

            # Must = high priority
            if "must" in sentence_lower:
                desc = self._clean_constraint_text(sentence)
                if desc:
                    constraints.append(
                        Constraint(
                            type=self._infer_constraint_type(sentence),
                            description=desc,
                            priority=Priority.MUST,
                        )
                    )

            # Should = medium priority
            elif "should" in sentence_lower:
                desc = self._clean_constraint_text(sentence)
                if desc:
                    constraints.append(
                        Constraint(
                            type=self._infer_constraint_type(sentence),
                            description=desc,
                            priority=Priority.SHOULD,
                        )
                    )

            # Could = low priority
            elif "could" in sentence_lower:
                desc = self._clean_constraint_text(sentence)
                if desc:
                    constraints.append(
                        Constraint(
                            type=self._infer_constraint_type(sentence),
                            description=desc,
                            priority=Priority.COULD,
                        )
                    )

        return constraints

    def _extract_explicit_requirements(self, text: str) -> List[Constraint]:
        """Extract explicitly stated requirements."""
        constraints = []

        # Look for numbered requirements
        req_pattern = r"(?:requirement|req|fr)[-\s]*(\d+)[:\s]*([^.!?\n]+)"
        matches = re.finditer(req_pattern, text, re.IGNORECASE)

        for match in matches:
            desc = match.group(2).strip()
            if len(desc) >= 10:
                constraints.append(
                    Constraint(
                        type=ConstraintType.BUSINESS,
                        description=desc[:300],
                        priority=Priority.MUST,
                    )
                )

        return constraints

    def _extract_implicit_constraints(self, text: str) -> List[Constraint]:
        """Extract implicit constraints from context."""
        constraints = []
        text_lower = text.lower()

        # Performance hints
        if any(word in text_lower for word in ["fast", "quick", "performance", "speed"]):
            constraints.append(
                Constraint(
                    type=ConstraintType.PERFORMANCE,
                    description="System should provide fast response times",
                    priority=Priority.SHOULD,
                )
            )

        # Security hints
        if any(word in text_lower for word in ["secure", "auth", "login", "password"]):
            constraints.append(
                Constraint(
                    type=ConstraintType.SECURITY,
                    description="System must ensure data security and user authentication",
                    priority=Priority.MUST,
                )
            )

        # Usability hints
        if any(word in text_lower for word in ["easy", "simple", "intuitive", "user-friendly"]):
            constraints.append(
                Constraint(
                    type=ConstraintType.USABILITY,
                    description="System should be easy to use and intuitive",
                    priority=Priority.SHOULD,
                )
            )

        return constraints

    def _clean_constraint_text(self, text: str) -> str:
        """Clean and format constraint text."""
        # Remove leading articles and modal verbs
        text = re.sub(r"^\s*(?:the|a|an|must|should|could)\s+", "", text, flags=re.IGNORECASE)

        # Ensure first letter is capitalized
        if text:
            text = text[0].upper() + text[1:]

        # Truncate if too long
        if len(text) > 300:
            text = text[:297] + "..."

        # Validate length
        if len(text) < 10:
            return ""

        return text

    def _infer_constraint_type(self, text: str) -> ConstraintType:
        """Infer constraint type from text content."""
        text_lower = text.lower()

        # Performance indicators
        if any(word in text_lower for word in ["fast", "quick", "performance", "speed", "latency"]):
            return ConstraintType.PERFORMANCE

        # Security indicators
        if any(
            word in text_lower for word in ["secure", "auth", "encrypt", "permission", "access"]
        ):
            return ConstraintType.SECURITY

        # Technical indicators
        if any(word in text_lower for word in ["api", "database", "server", "deploy", "scale"]):
            return ConstraintType.TECHNICAL

        # Usability indicators
        if any(word in text_lower for word in ["easy", "simple", "intuitive", "user", "ux"]):
            return ConstraintType.USABILITY

        # Default to business
        return ConstraintType.BUSINESS

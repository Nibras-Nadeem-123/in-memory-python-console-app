"""Goal identification skill."""

import re
from typing import Optional

from app.core.context import RequestContext
from app.skills.base import Skill


class GoalIdentifierSkill(Skill):
    """
    Identifies the primary goal/objective from user intent.

    Extraction strategy:
    1. Look for explicit goal statements ("build", "create", "develop")
    2. Extract first sentence if it contains action verbs
    3. Fall back to summarizing first paragraph
    """

    @property
    def name(self) -> str:
        """Return skill name."""
        return "GoalIdentifier"

    def execute(self, context: RequestContext) -> str:
        """
        Extract primary goal from intent.

        Args:
            context: Request context with user intent

        Returns:
            Identified goal statement (10-200 chars)

        Raises:
            ValueError: If goal cannot be identified
        """
        text = context.intent.text

        # Strategy 1: Look for explicit goal statements
        goal = self._find_explicit_goal(text)
        if goal:
            return goal

        # Strategy 2: Extract first sentence with action verbs
        goal = self._extract_first_action_sentence(text)
        if goal:
            return goal

        # Strategy 3: Summarize first paragraph
        goal = self._summarize_first_paragraph(text)
        if goal:
            return goal

        raise ValueError("Could not identify primary goal from intent")

    def _find_explicit_goal(self, text: str) -> Optional[str]:
        """Find explicit goal statements."""
        # Look for phrases like "build a...", "create a...", "develop a..."
        patterns = [
            r"(?:build|create|develop|design|implement)\s+(?:a|an)\s+([^.!?]+)",
            r"(?:need|want|require)\s+(?:a|an)\s+([^.!?]+)",
            r"the\s+goal\s+is\s+to\s+([^.!?]+)",
            r"(?:should|must)\s+([^.!?]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                goal = match.group(0).strip()
                # Clean and validate
                if 10 <= len(goal) <= 200:
                    return goal[:200]

        return None

    def _extract_first_action_sentence(self, text: str) -> Optional[str]:
        """Extract first sentence containing action verbs."""
        sentences = [s.strip() for s in text.split(".") if s.strip()]

        action_verbs = [
            "build",
            "create",
            "develop",
            "design",
            "implement",
            "allow",
            "enable",
            "provide",
            "support",
        ]

        for sentence in sentences[:3]:  # Check first 3 sentences
            if any(verb in sentence.lower() for verb in action_verbs):
                if 10 <= len(sentence) <= 200:
                    return sentence
                elif len(sentence) > 200:
                    return sentence[:197] + "..."

        return None

    def _summarize_first_paragraph(self, text: str) -> Optional[str]:
        """Summarize first paragraph as goal."""
        # Split by double newline or take first 200 chars
        first_para = text.split("\n\n")[0].strip()

        if len(first_para) < 10:
            # Fallback: first sentence
            first_sentence = text.split(".")[0].strip()
            if len(first_sentence) >= 10:
                return first_sentence[:200]
        elif len(first_para) <= 200:
            return first_para
        else:
            # Truncate to 200 chars at word boundary
            truncated = first_para[:197]
            last_space = truncated.rfind(" ")
            if last_space > 0:
                truncated = truncated[:last_space]
            return truncated + "..."

        return None

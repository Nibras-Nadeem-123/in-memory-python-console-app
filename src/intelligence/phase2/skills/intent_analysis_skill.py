"""Intent Analysis Skill for Phase 2 intelligence.

Performs deep semantic analysis of user input to extract
structured understanding beyond simple keyword matching.
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from ..skills.skill_interface import Skill, SkillError, SkillValidationError, SkillExecutionError
from ..phase2.data_models import Intent, IntentType, Entity


class IntentAnalysisSkill(Skill):
    """Skill for semantic intent analysis.

    Analyzes natural language to:
    - Classify intent type (ORGANIZE, PRIORITIZE, PLAN, QUERY)
    - Extract entities (tasks, priorities, timeframes)
    - Derive implicit requirements
    - Calculate confidence scores
    """

    @property
    def name(self) -> str:
        return "intent_analysis_phase2"

    @property
    def description(self) -> str:
        return "Deep semantic analysis of user input to extract structured understanding"

    @property
    def version(self) -> str:
        return "1.0.0"

    def validate_inputs(self, user_input: str, **kwargs: Any) -> None:
        """Validate inputs before execution."""
        if not user_input or not user_input.strip():
            raise SkillValidationError("user_input must be non-empty string")
        if len(user_input) > 10000:
            raise SkillValidationError("user_input too long (>10000 characters)")

    def execute(
        self,
        context: Any,
        user_input: str,
        conversation_history: List[Any] = None,
        domain_context: Dict[str, Any] = None,
        existing_state: Dict[str, Any] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute semantic intent analysis.

        Args:
            context: The current execution context.
            user_input: Raw natural language text.
            conversation_history: Previous messages for context.
            domain_context: Domain-specific knowledge (e.g., todo operations).
            existing_state: Current task state.

        Returns:
            Dictionary containing analyzed intent results.

        Raises:
            SkillExecutionError: If uninterpretable input.
        """
        # Normalize input
        normalized_input = user_input.strip().lower()

        # Classify intent type
        intent_type = self._classify_intent_type(normalized_input)

        # Extract entities
        entities = self._extract_entities(normalized_input, domain_context)

        # Derive requirements
        explicit_requirements = self._extract_explicit_requirements(normalized_input, entities)
        implicit_requirements = self._derive_implicit_requirements(entities)

        # Calculate confidence
        confidence = self._calculate_confidence(normalized_input, entities, explicit_requirements)

        # Calculate completeness
        completeness = self._calculate_completeness(entities, explicit_requirements)

        # Identify missing information
        missing_information = self._identify_missing_information(entities, normalized_input)

        # Extract timeframes
        timeframes = self._extract_timeframes(normalized_input)

        # Extract constraints
        constraints = self._extract_constraints(normalized_input, entities)

        return {
            "intent_type": intent_type,
            "confidence": confidence,
            "entities": entities,
            "explicit_requirements": explicit_requirements,
            "implicit_requirements": implicit_requirements,
            "completeness_score": completeness,
            "missing_information": missing_information,
            "timeframes": timeframes,
            "constraints": constraints,
            "metadata": {
                "input_length": len(user_input),
                "word_count": len(user_input.split()),
                "has_entities": len(entities) > 0
            }
        }

    def _classify_intent_type(self, text: str) -> IntentType:
        """Classify high-level intent type from text."""
        # Keywords for each intent type
        organize_keywords = [
            "organize", "arrange", "sort", "order", "structure",
            "clean up", "manage", "handle", "process"
        ]
        prioritize_keywords = [
            "prioritize", "focus on", "important", "urgent", "priority",
            "first", "critical", "must do", "should do"
        ]
        plan_keywords = [
            "plan", "create plan", "break down", "schedule", "map out"
        ]
        query_keywords = [
            "show", "what", "list", "display", "tell me about",
            "get", "find", "search"
        ]

        # Score matches
        scores = {
            IntentType.ORGANIZE: sum(1 for kw in organize_keywords if kw in text),
            IntentType.PRIORITIZE: sum(1 for kw in prioritize_keywords if kw in text),
            IntentType.PLAN: sum(1 for kw in plan_keywords if kw in text),
            IntentType.QUERY: sum(1 for kw in query_keywords if kw in text)
        }

        # Return highest-scoring type
        max_score = max(scores.values())
        for intent_type, score in scores.items():
            if score == max_score:
                return intent_type

        # Default to ORGANIZE if no clear winner
        return IntentType.ORGANIZE

    def _extract_entities(self, text: str, domain_context: Dict[str, Any]) -> List[Entity]:
        """Extract entities from text."""
        entities = []

        # Task entities (look for task descriptions)
        task_patterns = [
            r"add task[:\s]*(.+?)\s*(?:with|for)\s*(priority\s+(\w+))?",
            r"create task[:\s]*(.+?)\s*(?:with|for)\s*(priority\s+(\w+))?",
            r"task[:\s]*\"([^\"]+)\"",
            r"tasks?[:\s]*\"([^\"]+)\""
        ]

        import re
        for pattern in task_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract task description
                if isinstance(match, tuple):
                    task_desc = match[0] if len(match) > 0 else ""
                else:
                    task_desc = match

                # Extract priority if present
                priority = "MEDIUM"
                if len(match) > 1 and match[1]:
                    priority = match[1].upper()
                    if priority not in ["HIGH", "MEDIUM", "LOW"]:
                        priority = "MEDIUM"

                entities.append(Entity(
                    entity_type="TASK",
                    value=task_desc,
                    confidence=0.8 if priority else 0.7,
                    position=(0, 0)  # Simplified position
                ))

        # Priority entities (look for priority mentions)
        priority_keywords = ["high", "medium", "low", "urgent", "critical"]
        for keyword in priority_keywords:
            if keyword in text:
                entities.append(Entity(
                    entity_type="PRIORITY",
                    value=keyword.upper(),
                    confidence=0.9,
                    position=(0, 0)
                ))

        # Timeframe entities
        timeframe_patterns = [
            (r"\btoday\b", "today"),
            (r"\btomorrow\b", "tomorrow"),
            (r"\bthis week\b", "this_week"),
            (r"\bnext week\b", "next_week"),
            (r"\bthis month\b", "this_month")
        ]

        for pattern, value in timeframe_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    entity_type="TIMEFRAME",
                    value=value,
                    confidence=0.9,
                    position=(0, 0)
                ))

        return entities

    def _extract_explicit_requirements(self, text: str, entities: List[Entity]) -> List[str]:
        """Extract explicitly stated requirements."""
        requirements = []

        # Task descriptions as requirements
        task_entities = [e for e in entities if e.entity_type == "TASK"]
        for task_entity in task_entities:
            requirements.append(f"Create task: {task_entity.value}")

        return requirements

    def _derive_implicit_requirements(self, entities: List[Entity]) -> List[str]:
        """Derive implicit requirements from entities."""
        requirements = []

        # If priorities mentioned, need priority support
        priority_entities = [e for e in entities if e.entity_type == "PRIORITY"]
        if priority_entities:
            requirements.append("Support task prioritization")

        # If timeframes mentioned, need time filtering
        timeframe_entities = [e for e in entities if e.entity_type == "TIMEFRAME"]
        if timeframe_entities:
            requirements.append("Filter tasks by timeframe")

        return requirements

    def _calculate_confidence(
        self,
        text: str,
        entities: List[Entity],
        explicit_requirements: List[str]
    ) -> float:
        """Calculate confidence score based on clarity and detail."""
        confidence = 0.5  # Base confidence

        # Increase for more detailed text
        word_count = len(text.split())
        if word_count >= 5:
            confidence += 0.1
        if word_count >= 10:
            confidence += 0.1

        # Increase for extracted entities
        if len(entities) > 0:
            confidence += 0.1
        if len(entities) >= 2:
            confidence += 0.1

        # Decrease for questions
        if text.strip().endswith("?"):
            confidence -= 0.1

        # Decrease for vague words
        vague_words = ["maybe", "might", "could", "possibly", "sort of", "kind of"]
        if any(vw in text for vw in vague_words):
            confidence -= 0.1

        return min(max(0.0, confidence), 1.0)

    def _calculate_completeness(self, entities: List[Entity], explicit_requirements: List[str]) -> float:
        """Calculate completeness score (0.0-1.0)."""
        score = 0.5  # Base score

        # Increase for having task descriptions
        task_entities = [e for e in entities if e.entity_type == "TASK"]
        if len(task_entities) > 0:
            score += 0.2

        # Increase for having priorities
        priority_entities = [e for e in entities if e.entity_type == "PRIORITY"]
        if len(priority_entities) > 0:
            score += 0.1

        # Increase for having timeframes
        timeframe_entities = [e for e in entities if e.entity_type == "TIMEFRAME"]
        if len(timeframe_entities) > 0:
            score += 0.1

        # Increase for explicit requirements
        if len(explicit_requirements) > 0:
            score += 0.1

        return min(score, 1.0)

    def _identify_missing_information(self, entities: List[Entity], text: str) -> List[str]:
        """Identify critical missing information."""
        missing = []

        # Check for task entities
        task_entities = [e for e in entities if e.entity_type == "TASK"]
        if not task_entities:
            missing.append("Task descriptions not specified")

        # Check for vague language
        vague_indicators = ["something", "anything", "stuff", "things"]
        if any(vi in text for vi in vague_indicators):
            missing.append("Vague language used - be more specific")

        return missing

    def _extract_timeframes(self, text: str) -> List[str]:
        """Extract timeframes from text."""
        timeframes = []

        timeframe_map = {
            "today": "today",
            "this week": "this_week",
            "next week": "next_week",
            "this month": "this_month",
            "tomorrow": "tomorrow"
        }

        for keyword, value in timeframe_map.items():
            if keyword in text:
                timeframes.append(value)

        return list(set(timeframes))

    def _extract_constraints(self, text: str, entities: List[Entity]) -> List[str]:
        """Extract constraints from text."""
        constraints = []

        # Priority constraints
        priority_entities = [e for e in entities if e.entity_type == "PRIORITY"]
        for entity in priority_entities:
            constraints.append(f"Priority: {entity.value}")

        return list(set(constraints))

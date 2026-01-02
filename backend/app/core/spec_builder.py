"""
Spec builder orchestrates skills to generate structured specifications.
"""

from typing import List

from app.core.context import RequestContext
from app.models.spec import Assumption, Constraint, Entity, SpecMetadata, StructuredSpec
from app.skills.assumption_detector import AssumptionDetectorSkill
from app.skills.constraint_parser import ConstraintParserSkill
from app.skills.entity_extractor import EntityExtractorSkill
from app.skills.goal_identifier import GoalIdentifierSkill


class SpecBuilder:
    """
    Orchestrates spec generation skills.

    Combines results from multiple skills to build a complete structured specification.
    """

    def __init__(self) -> None:
        """Initialize spec builder with skills."""
        self.goal_identifier = GoalIdentifierSkill()
        self.entity_extractor = EntityExtractorSkill()
        self.constraint_parser = ConstraintParserSkill()
        self.assumption_detector = AssumptionDetectorSkill()

    def build(self, context: RequestContext) -> StructuredSpec:
        """
        Build structured specification from user intent.

        Args:
            context: Request context containing intent

        Returns:
            Complete structured specification

        Raises:
            ValueError: If spec cannot be generated from intent
        """
        # Execute skills to extract components
        goal = self.goal_identifier.execute(context)
        entities = self.entity_extractor.execute(context)
        constraints = self.constraint_parser.execute(context)
        assumptions = self.assumption_detector.execute(context)

        # Calculate confidence score
        confidence_score = self._calculate_confidence(entities, constraints, assumptions)

        # Generate warnings
        warnings = self._generate_warnings(assumptions, confidence_score)

        # Create metadata
        metadata = SpecMetadata(
            processing_time_ms=context.elapsed_ms,
            confidence_score=confidence_score,
            warnings=warnings,
        )

        # Build and return spec
        return StructuredSpec(
            goal=goal,
            entities=entities,
            constraints=constraints,
            assumptions=assumptions,
            metadata=metadata,
        )

    def _calculate_confidence(
        self,
        entities: list,
        constraints: list,
        assumptions: list,
    ) -> float:
        """
        Calculate confidence score based on extracted information.

        Formula from data-model.md:
        confidence = (entities_found * 0.4) + (constraints_found * 0.3) +
                    (1 - assumptions_needing_clarification * 0.3)
        """
        entity_score = min(len(entities) / 5.0, 1.0) * 0.4
        constraint_score = min(len(constraints) / 5.0, 1.0) * 0.3

        clarification_count = sum(1 for a in assumptions if a.needs_clarification)
        assumption_score = max(0, 1.0 - (clarification_count / 5.0)) * 0.3

        confidence = entity_score + constraint_score + assumption_score
        return round(confidence, 2)

    def _generate_warnings(self, assumptions: list, confidence: float) -> list[str]:
        """Generate warnings based on spec quality."""
        warnings = []

        clarification_count = sum(1 for a in assumptions if a.needs_clarification)
        if clarification_count > 2:
            warnings.append(
                f"MANY_ASSUMPTIONS: {clarification_count} assumptions require user clarification"
            )

        if confidence < 0.5:
            warnings.append(f"LOW_CONFIDENCE: Overall confidence score is {confidence}")

        return warnings

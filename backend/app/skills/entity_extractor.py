"""Entity extraction skill."""

import re
from typing import List

from app.core.context import RequestContext
from app.models.spec import Entity, EntityType, Relationship, RelationshipType
from app.skills.base import Skill


class EntityExtractorSkill(Skill):
    """
    Extracts domain entities from user intent.

    Extraction strategy:
    1. Identify nouns that represent domain concepts
    2. Classify entities by type (Domain, Resource, Actor, Process)
    3. Infer attributes from context
    4. Identify relationships between entities
    """

    @property
    def name(self) -> str:
        """Return skill name."""
        return "EntityExtractor"

    def execute(self, context: RequestContext) -> List[Entity]:
        """
        Extract entities from intent.

        Args:
            context: Request context with user intent

        Returns:
            List of identified entities

        Raises:
            ValueError: If no entities can be extracted
        """
        text = context.intent.text

        # Extract candidate entities
        candidates = self._find_entity_candidates(text)

        if not candidates:
            raise ValueError("Could not extract any entities from intent")

        # Build Entity objects
        entities = []
        for name, entity_type, attributes in candidates:
            entity = Entity(
                name=name,
                type=entity_type,
                description=f"{name} entity in the system",
                attributes=attributes,
                relationships=[],
            )
            entities.append(entity)

        # Infer relationships
        entities = self._infer_relationships(entities, text)

        return entities

    def _find_entity_candidates(self, text: str) -> List[tuple]:
        """Find candidate entities from text."""
        candidates = []

        # Common domain entity patterns
        entity_patterns = {
            "task": (EntityType.DOMAIN, ["title", "description", "status", "priority"]),
            "user": (EntityType.ACTOR, ["name", "email", "id"]),
            "project": (EntityType.DOMAIN, ["name", "description", "status"]),
            "tag": (EntityType.RESOURCE, ["name", "color"]),
            "comment": (EntityType.DOMAIN, ["text", "author", "timestamp"]),
            "category": (EntityType.RESOURCE, ["name", "description"]),
            "post": (EntityType.DOMAIN, ["title", "content", "author", "publishedAt"]),
            "article": (EntityType.DOMAIN, ["title", "content", "author"]),
            "product": (EntityType.DOMAIN, ["name", "price", "description"]),
            "order": (EntityType.DOMAIN, ["id", "total", "status", "customerId"]),
            "customer": (EntityType.ACTOR, ["name", "email", "phone"]),
            "item": (EntityType.DOMAIN, ["name", "description", "id"]),
        }

        text_lower = text.lower()

        for keyword, (entity_type, attributes) in entity_patterns.items():
            if keyword in text_lower:
                # Capitalize entity name (PascalCase)
                entity_name = keyword.capitalize()
                candidates.append((entity_name, entity_type, attributes))

        # If no specific entities found, create generic ones
        if not candidates:
            candidates.append(
                ("Item", EntityType.DOMAIN, ["id", "name", "description", "status"])
            )

        return candidates

    def _infer_relationships(self, entities: List[Entity], text: str) -> List[Entity]:
        """Infer relationships between entities."""
        # Simple heuristic: look for common relationship patterns

        entity_names = {e.name for e in entities}

        for entity in entities:
            # User relationships
            if "User" in entity_names and entity.name != "User":
                # Most entities belong to users
                if entity.type == EntityType.DOMAIN:
                    entity.relationships.append(
                        Relationship(
                            type=RelationshipType.BELONGS_TO,
                            target="User",
                            description=f"Each {entity.name} belongs to a user",
                        )
                    )

            # Task-Tag many-to-many
            if entity.name == "Task" and "Tag" in entity_names:
                entity.relationships.append(
                    Relationship(
                        type=RelationshipType.MANY_TO_MANY,
                        target="Tag",
                        description="Tasks can have multiple tags",
                    )
                )

            # Post-Comment one-to-many
            if entity.name == "Post" and "Comment" in entity_names:
                entity.relationships.append(
                    Relationship(
                        type=RelationshipType.HAS_MANY,
                        target="Comment",
                        description="Posts can have multiple comments",
                    )
                )

        return entities

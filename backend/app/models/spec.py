"""Structured specification output models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class EntityType(str, Enum):
    """Classification of entities in the system."""

    DOMAIN = "Domain"
    RESOURCE = "Resource"
    ACTOR = "Actor"
    PROCESS = "Process"


class RelationshipType(str, Enum):
    """Nature of relationships between entities."""

    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"
    BELONGS_TO = "belongs_to"
    HAS_MANY = "has_many"
    HAS_ONE = "has_one"


class ConstraintType(str, Enum):
    """Category of constraints."""

    PERFORMANCE = "Performance"
    SECURITY = "Security"
    BUSINESS = "Business"
    TECHNICAL = "Technical"
    USABILITY = "Usability"


class Priority(str, Enum):
    """Importance level for constraints."""

    MUST = "Must"
    SHOULD = "Should"
    COULD = "Could"


class ConfidenceLevel(str, Enum):
    """Confidence in assumptions."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Relationship(BaseModel):
    """Connection between entities."""

    type: RelationshipType = Field(..., description="Nature of relationship")
    target: str = Field(..., description="Name of related entity")
    description: Optional[str] = Field(None, description="Explanation of relationship")

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "belongs_to",
                "target": "User",
                "description": "Each task is owned by a user",
            }
        }
    }


class Entity(BaseModel):
    """Domain entity in the system."""

    name: str = Field(
        ...,
        pattern=r"^[A-Z][a-zA-Z0-9]*$",
        min_length=2,
        max_length=50,
        description="Entity name in PascalCase",
    )
    type: EntityType = Field(..., description="Classification of entity")
    description: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="What this entity represents",
    )
    attributes: List[str] = Field(
        ...,
        min_length=1,
        description="Entity properties",
    )
    relationships: List[Relationship] = Field(
        default_factory=list,
        description="Connections to other entities",
    )

    @field_validator("attributes")
    @classmethod
    def validate_attributes(cls, v: List[str]) -> List[str]:
        """Ensure attributes are non-empty strings."""
        if not v:
            raise ValueError("Entity must have at least one attribute")
        if any(not attr.strip() for attr in v):
            raise ValueError("Attributes cannot be empty strings")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Task",
                "type": "Domain",
                "description": "Core work item that users manage",
                "attributes": ["title", "description", "priority", "dueDate", "status"],
                "relationships": [
                    {
                        "type": "belongs_to",
                        "target": "User",
                        "description": "Each task is owned by a user",
                    }
                ],
            }
        }
    }


class Constraint(BaseModel):
    """System requirement or limitation."""

    type: ConstraintType = Field(..., description="Category of constraint")
    description: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="What is required or constrained",
    )
    priority: Priority = Field(..., description="Importance level")

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "Business",
                "description": "Users must be able to filter tasks by priority level",
                "priority": "Must",
            }
        }
    }


class Assumption(BaseModel):
    """Implicit assumption detected in user intent."""

    description: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="What is assumed",
    )
    confidence: ConfidenceLevel = Field(
        ...,
        description="How certain is this assumption",
    )
    needs_clarification: bool = Field(
        ...,
        description="Should user confirm this?",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "description": "Single-user application (no multi-tenancy)",
                "confidence": "Medium",
                "needs_clarification": True,
            }
        }
    }


class SpecMetadata(BaseModel):
    """Metadata about the generated specification."""

    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When spec was generated (ISO 8601)",
    )
    processing_time_ms: float = Field(
        ...,
        ge=0.0,
        description="How long generation took (milliseconds)",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall spec quality (0.0-1.0)",
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Issues or suggestions",
    )

    @field_validator("confidence_score")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence score must be between 0.0 and 1.0, got {v}")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "generated_at": "2025-12-31T10:30:01.234Z",
                "processing_time_ms": 123.45,
                "confidence_score": 0.85,
                "warnings": [],
            }
        }
    }


class StructuredSpec(BaseModel):
    """Complete structured specification output."""

    goal: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="Primary objective of the system",
    )
    entities: List[Entity] = Field(
        ...,
        min_length=1,
        description="Domain entities in the system",
    )
    constraints: List[Constraint] = Field(
        ...,
        min_length=1,
        description="System requirements and limitations",
    )
    assumptions: List[Assumption] = Field(
        default_factory=list,
        description="Implicit assumptions detected in user intent",
    )
    metadata: SpecMetadata = Field(
        ...,
        description="Generation metadata and quality metrics",
    )

    @field_validator("entities")
    @classmethod
    def validate_entities(cls, v: List[Entity]) -> List[Entity]:
        """Ensure at least one entity exists."""
        if not v:
            raise ValueError("Specification must contain at least one entity")
        return v

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: List[Constraint]) -> List[Constraint]:
        """Ensure at least one constraint exists."""
        if not v:
            raise ValueError("Specification must contain at least one constraint")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "goal": "Build a task management system with priority and categorization features",
                "entities": [
                    {
                        "name": "Task",
                        "type": "Domain",
                        "description": "Core work item that users manage",
                        "attributes": ["title", "description", "priority", "dueDate", "status"],
                        "relationships": [
                            {
                                "type": "belongs_to",
                                "target": "User",
                                "description": "Each task is owned by a user",
                            }
                        ],
                    }
                ],
                "constraints": [
                    {
                        "type": "Business",
                        "description": "Users must be able to filter tasks by priority level",
                        "priority": "Must",
                    }
                ],
                "assumptions": [
                    {
                        "description": "Single-user application (no multi-tenancy)",
                        "confidence": "Medium",
                        "needs_clarification": True,
                    }
                ],
                "metadata": {
                    "generated_at": "2025-12-31T10:30:01.234Z",
                    "processing_time_ms": 123.45,
                    "confidence_score": 0.85,
                    "warnings": [],
                },
            }
        }
    }

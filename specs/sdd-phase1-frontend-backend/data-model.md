# Data Model: SDD System Phase 1

**Date**: 2025-12-31
**Feature**: Frontend-Backend Spec Generation System
**Purpose**: Define all data structures, validation rules, and relationships

---

## Entity Relationship Diagram

```
┌──────────────┐
│ UserIntent   │
│  (Input)     │
└──────┬───────┘
       │ transforms_to
       ▼
┌───────────────────┐
│ StructuredSpec    │
│  (Output)         │
└───────┬───────────┘
        │
        │ contains
        ├─────────────┐
        ▼             ▼
┌─────────────┐  ┌─────────────┐
│  Entity     │  │ Constraint  │
│  (0..N)     │  │  (0..N)     │
└─────────────┘  └─────────────┘
        │             │
        │             │
        ▼             ▼
┌─────────────┐  ┌─────────────┐
│ Relationship│  │ Assumption  │
│  (0..N)     │  │  (0..N)     │
└─────────────┘  └─────────────┘
```

---

## Input Models

### UserIntent

**Purpose**: Capture raw user input for spec generation

**Fields**:
- `text` (string, required): Natural language description of desired system
  - Validation: 50-500 words
  - Format: Plain text, UTF-8
- `request_id` (UUID, auto-generated): Unique identifier for this request
- `timestamp` (datetime, auto-generated): When the request was received

**Validation Rules**:
```python
from pydantic import BaseModel, Field, field_validator
from uuid import uuid4
from datetime import datetime

class UserIntent(BaseModel):
    text: str = Field(..., min_length=50, max_length=5000)
    request_id: UUID4 = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('text')
    @classmethod
    def validate_word_count(cls, v: str) -> str:
        words = len(v.split())
        if words < 50:
            raise ValueError(f'Text must contain at least 50 words (got {words})')
        if words > 500:
            raise ValueError(f'Text must contain at most 500 words (got {words})')
        return v
```

**Example**:
```json
{
  "text": "Create a task management application where users can create, edit, and delete tasks. Each task should have a title, description, priority level, and due date. Users should be able to categorize tasks using tags and filter tasks by priority or tag.",
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-12-31T10:30:00Z"
}
```

---

## Output Models

### StructuredSpec

**Purpose**: Structured representation of system specification

**Fields**:
- `goal` (string, required): Primary objective of the system
  - Validation: Non-empty, 10-200 characters
- `entities` (List[Entity], required): Domain entities
  - Validation: At least 1 entity
- `constraints` (List[Constraint], required): System constraints
  - Validation: At least 1 "Must" priority constraint
- `assumptions` (List[Assumption], optional): Implicit assumptions
- `metadata` (SpecMetadata, required): Generation metadata

**Validation Rules**:
```python
class StructuredSpec(BaseModel):
    goal: str = Field(..., min_length=10, max_length=200)
    entities: List[Entity] = Field(..., min_length=1)
    constraints: List[Constraint] = Field(..., min_length=1)
    assumptions: List[Assumption] = Field(default_factory=list)
    metadata: SpecMetadata

    @field_validator('constraints')
    @classmethod
    def validate_must_constraints(cls, v: List[Constraint]) -> List[Constraint]:
        must_constraints = [c for c in v if c.priority == ConstraintPriority.MUST]
        if not must_constraints:
            raise ValueError('At least one "Must" priority constraint required')
        return v

    @field_validator('entities')
    @classmethod
    def validate_unique_entity_names(cls, v: List[Entity]) -> List[Entity]:
        names = [e.name for e in v]
        if len(names) != len(set(names)):
            raise ValueError('Entity names must be unique')
        return v
```

**Example**:
```json
{
  "goal": "Build a task management system with priority and categorization features",
  "entities": [...],
  "constraints": [...],
  "assumptions": [...],
  "metadata": {...}
}
```

---

### Entity

**Purpose**: Represent domain objects in the system

**Fields**:
- `name` (string, required): Entity name
  - Validation: PascalCase, 2-50 characters, alphanumeric
- `type` (EntityType, required): Classification of entity
- `description` (string, required): What this entity represents
  - Validation: 10-200 characters
- `attributes` (List[string], required): Entity properties
  - Validation: At least 1 attribute, unique names
- `relationships` (List[Relationship], optional): Connections to other entities

**EntityType Enum**:
```python
from enum import Enum

class EntityType(str, Enum):
    DOMAIN = "Domain"        # Core business entities (e.g., Task, User)
    RESOURCE = "Resource"    # Supporting data (e.g., Tag, Category)
    ACTOR = "Actor"          # System actors (e.g., User, Admin)
    PROCESS = "Process"      # Workflows (e.g., TaskApproval, Notification)
```

**Validation Rules**:
```python
class Entity(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, pattern=r'^[A-Z][a-zA-Z0-9]*$')
    type: EntityType
    description: str = Field(..., min_length=10, max_length=200)
    attributes: List[str] = Field(..., min_length=1)
    relationships: List[Relationship] = Field(default_factory=list)

    @field_validator('attributes')
    @classmethod
    def validate_unique_attributes(cls, v: List[str]) -> List[str]:
        if len(v) != len(set(v)):
            raise ValueError('Attribute names must be unique')
        return v
```

**Example**:
```json
{
  "name": "Task",
  "type": "Domain",
  "description": "Core work item that users manage",
  "attributes": ["title", "description", "priority", "tags", "status", "dueDate"],
  "relationships": [
    {
      "type": "belongs_to",
      "target": "User",
      "description": "Each task is owned by a user"
    },
    {
      "type": "many_to_many",
      "target": "Tag",
      "description": "Tasks can have multiple tags"
    }
  ]
}
```

---

### Relationship

**Purpose**: Define connections between entities

**Fields**:
- `type` (RelationshipType, required): Nature of relationship
- `target` (string, required): Name of related entity
  - Validation: Must reference existing entity
- `description` (string, optional): Explanation of relationship

**RelationshipType Enum**:
```python
class RelationshipType(str, Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"
    BELONGS_TO = "belongs_to"
    HAS_MANY = "has_many"
    HAS_ONE = "has_one"
```

**Example**:
```json
{
  "type": "belongs_to",
  "target": "User",
  "description": "Each task is owned by a single user"
}
```

---

### Constraint

**Purpose**: System requirements and limitations

**Fields**:
- `type` (ConstraintType, required): Category of constraint
- `description` (string, required): What is required/constrained
  - Validation: 10-300 characters
- `priority` (ConstraintPriority, required): Importance level

**ConstraintType Enum**:
```python
class ConstraintType(str, Enum):
    PERFORMANCE = "Performance"  # Speed, throughput, resource usage
    SECURITY = "Security"        # Authentication, authorization, encryption
    BUSINESS = "Business"        # Business rules, workflows
    TECHNICAL = "Technical"      # Technology, architecture, integration
    USABILITY = "Usability"      # UX, accessibility
```

**ConstraintPriority Enum**:
```python
class ConstraintPriority(str, Enum):
    MUST = "Must"      # Required for MVP
    SHOULD = "Should"  # Important but not critical
    COULD = "Could"    # Nice to have
```

**Example**:
```json
{
  "type": "Business",
  "description": "Users must be able to filter tasks by priority level",
  "priority": "Must"
}
```

---

### Assumption

**Purpose**: Implicit assumptions detected in user intent

**Fields**:
- `description` (string, required): What is assumed
  - Validation: 10-300 characters
- `confidence` (ConfidenceLevel, required): How certain is this assumption
- `needs_clarification` (boolean, required): Should user confirm this?

**ConfidenceLevel Enum**:
```python
class ConfidenceLevel(str, Enum):
    HIGH = "High"      # 90%+ confident
    MEDIUM = "Medium"  # 60-90% confident
    LOW = "Low"        # <60% confident
```

**Example**:
```json
{
  "description": "Single-user application (no multi-tenancy)",
  "confidence": "Medium",
  "needs_clarification": true
}
```

---

### SpecMetadata

**Purpose**: Generation metadata and quality indicators

**Fields**:
- `generated_at` (datetime, required): When spec was generated
- `processing_time_ms` (float, required): How long generation took
  - Validation: >= 0.0
- `confidence_score` (float, required): Overall spec quality
  - Validation: 0.0 <= score <= 1.0
- `warnings` (List[string], optional): Issues or suggestions

**Confidence Score Calculation**:
```python
def calculate_confidence(
    goal_clarity: float,  # 0.0-1.0
    entity_count: int,
    constraint_count: int,
    ambiguity_count: int
) -> float:
    """
    Confidence = (goal_clarity * 0.4) +
                 (min(entity_count/3, 1.0) * 0.3) +
                 (min(constraint_count/5, 1.0) * 0.2) +
                 (max(0, 1 - ambiguity_count/10) * 0.1)
    """
    entity_score = min(entity_count / 3, 1.0)
    constraint_score = min(constraint_count / 5, 1.0)
    ambiguity_penalty = max(0, 1 - ambiguity_count / 10)

    return (
        goal_clarity * 0.4 +
        entity_score * 0.3 +
        constraint_score * 0.2 +
        ambiguity_penalty * 0.1
    )
```

**Warning Types**:
- `AMBIGUOUS_GOAL`: Goal not clearly stated
- `FEW_ENTITIES`: Less than 2 entities detected
- `NO_CONSTRAINTS`: No explicit constraints found
- `MANY_ASSUMPTIONS`: Many unverified assumptions
- `LOW_CONFIDENCE`: Overall confidence < 0.6

**Example**:
```json
{
  "generated_at": "2025-12-31T10:30:01.234Z",
  "processing_time_ms": 123.45,
  "confidence_score": 0.85,
  "warnings": [
    "MANY_ASSUMPTIONS: 3 assumptions require user clarification"
  ]
}
```

---

## TypeScript Equivalents

For frontend type safety, equivalent TypeScript interfaces:

```typescript
export interface UserIntent {
  text: string;
  request_id: string;
  timestamp: string;
}

export interface StructuredSpec {
  goal: string;
  entities: Entity[];
  constraints: Constraint[];
  assumptions: Assumption[];
  metadata: SpecMetadata;
}

export interface Entity {
  name: string;
  type: 'Domain' | 'Resource' | 'Actor' | 'Process';
  description: string;
  attributes: string[];
  relationships: Relationship[];
}

export interface Relationship {
  type: 'one_to_one' | 'one_to_many' | 'many_to_one' | 'many_to_many' | 'belongs_to' | 'has_many' | 'has_one';
  target: string;
  description?: string;
}

export interface Constraint {
  type: 'Performance' | 'Security' | 'Business' | 'Technical' | 'Usability';
  description: string;
  priority: 'Must' | 'Should' | 'Could';
}

export interface Assumption {
  description: string;
  confidence: 'High' | 'Medium' | 'Low';
  needs_clarification: boolean;
}

export interface SpecMetadata {
  generated_at: string;
  processing_time_ms: number;
  confidence_score: number;
  warnings: string[];
}
```

---

## Validation Summary

| Model | Key Validations |
|-------|----------------|
| UserIntent | 50-500 words, UTF-8 encoded |
| StructuredSpec | >=1 entity, >=1 Must constraint, unique entity names |
| Entity | PascalCase name, >=1 attribute, unique attributes |
| Relationship | Target must exist |
| Constraint | 10-300 chars description |
| Assumption | 10-300 chars description |
| SpecMetadata | 0.0 <= confidence <= 1.0, processing_time >= 0 |

---

## State Lifecycle

Phase 1 is stateless. Each request follows this lifecycle:

```
1. Receive UserIntent
2. Validate input (50-500 words)
3. Generate StructuredSpec
   a. Extract goal
   b. Identify entities
   c. Parse constraints
   d. Detect assumptions
   e. Calculate confidence
4. Validate output (all rules)
5. Return StructuredSpec
6. Discard context (no persistence)
```

No state persists between requests.

---

## Future Extensions (Out of Scope for Phase 1)

- **Plan** entity: Links spec to implementation plan
- **Task** entity: Breaks plan into executable tasks
- **ExecutionResult** entity: Records task execution outcomes
- **User** entity: Multi-user support
- **Project** entity: Persistence layer

---

**Status**: ✅ Complete - ready for contract generation
**Next**: Generate OpenAPI specification in contracts/openapi.yaml

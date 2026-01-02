---
id: 'skill-registry'
title: 'Skill Registry System'
version: '1.0.0'
date: '2025-12-28'
status: 'Draft'
feature: 'skill-registry'
branch: 'main'
---

## Overview

The Skill Registry provides a centralized system for discovering, registering, and invoking skills within the intelligence layer. Skills are stateless, composable units of capability that can be combined to build complex agent behaviors.

## Purpose

- **Registration**: Centralized skill catalog with unique names and metadata
- **Discovery**: Runtime discovery of skills by capability
- **Invocation**: Standardized interface for skill execution
- **Composition**: Skills can depend on and chain with other skills
- **Validation**: Input/output schema validation at registration and invocation

## User Scenarios & Testing

### User Story 1 - Skill Registration

As a developer, I want to register skills with the registry so that agents can discover and use them.

**Priority**: P1

**Independent Test**: Register skill, verify it appears in registry listing.

**Acceptance Scenarios**:

1. **Given** skill with unique name, **When** registered, **Then** skill appears in `list_skills()`
2. **Given** skill with duplicate name, **When** registered, **Then** registration rejected with error
3. **Given** skill with full metadata, **When** registered, **Then** all metadata persisted

### User Story 2 - Skill Discovery

As an agent, I want to discover skills by capability so that I can use the right skill for each task.

**Priority**: P1

**Independent Test**: Query registry by capability, verify results.

**Acceptance Scenarios**:

1. **Given** registry with 10 skills, **When** querying "text_generation", **Then** only skills with that capability returned
2. **Given** capability with multiple skills, **When** queried, **Then** skills returned with confidence scores
3. **Given** no matching skills, **When** queried, **Then** empty list returned (no error)

### User Story 3 - Skill Invocation

As an engine, I want to invoke skills through a standard interface so that agents can execute capabilities.

**Priority**: P1

**Independent Test**: Invoke skill with valid input, verify output.

**Acceptance Scenarios**:

1. **Given** registered skill, **When** invoked with valid input, **Then** output matches output schema
2. **Given** skill with dependencies, **When** invoked, **Then** dependencies resolved and available
3. **Given** skill invocation, **When** complete, **Then** metrics recorded (duration, success/failure)

### User Story 4 - Skill Composition

As a developer, I want to compose skills together so that complex behaviors emerge from simple parts.

**Priority**: P2

**Independent Test**: Chain skills, verify output flows between them.

**Acceptance Scenarios**:

1. **Given** Skill A produces type T, **When** Skill B accepts type T, **When** composed, **Then** A→B chain executes successfully
2. **Given** skill with optional dependency, **When** dependency available, **Then** injected into skill
3. **Given** skill composition, **When** intermediate step fails, **Then** error propagates with context

---

## Requirements

### Functional Requirements

- **FR-SKILL-001**: Skills MUST be registered with unique names
- **FR-SKILL-002**: Skills MUST declare input and output schemas
- **FR-SKILL-003**: Skills MUST be stateless (no internal state between invocations)
- **FR-SKILL-004**: Skills MUST declare dependencies on other skills
- **FR-SKILL-005**: Registry MUST support skill composition (chaining)
- **FR-SKILL-006**: Registry MUST validate schemas at registration and invocation
- **FR-SKILL-007**: Registry MUST track skill versions and deprecation

### Non-Functional Requirements

- **NFR-SKILL-001**: Skill registration MUST complete within 50ms
- **NFR-SKILL-002**: Skill lookup MUST complete within 5ms
- **NFR-SKILL-003**: Registry MUST support 1000+ registered skills
- **NFR-SKILL-004**: Skill invocation overhead MUST be under 1ms
- **NFR-SKILL-005**: All registry operations MUST be thread-safe

---

## Skill Definition

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type
import uuid


class SkillCategory(Enum):
    """Skill categories for organization."""
    PARSING = "parsing"
    GENERATION = "generation"
    ANALYSIS = "analysis"
    TRANSFORMATION = "transformation"
    REASONING = "reasoning"
    VALIDATION = "validation"
    ORCHESTRATION = "orchestration"
    MEMORY = "memory"
    EVALUATION = "evaluation"


class SkillStatus(Enum):
    """Skill lifecycle status."""
    EXPERIMENTAL = "experimental"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


@dataclass
class SkillVersion:
    """Semantic version for skills."""
    major: int = 1
    minor: int = 0
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def is_compatible(self, other: "SkillVersion") -> bool:
        """Check if versions are compatible (same major)."""
        return self.major == other.major

    def increment_major(self) -> "SkillVersion":
        return SkillVersion(self.major + 1, 0, 0)

    def increment_minor(self) -> "SkillVersion":
        return SkillVersion(self.major, self.minor + 1, 0)

    def increment_patch(self) -> "SkillVersion":
        return SkillVersion(self.major, self.minor, self.patch + 1)


@dataclass
class SkillInput:
    """Input specification for a skill."""
    name: str
    type: Type  # Python type or string for JSON schema
    required: bool = True
    description: str = ""
    default: Any = None
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SkillOutput:
    """Output specification for a skill."""
    name: str
    type: Type  # Python type or string for JSON schema
    description: str = ""


@dataclass
class SkillDependency:
    """Dependency on another skill."""
    skill_name: str
    version_range: str = ">=1.0.0,<2.0.0"  # Version specifier
    optional: bool = False
    injection_method: str = "constructor"  # "constructor", "property", "method_param"


@dataclass
class SkillMetadata:
    """Metadata describing a skill."""
    name: str
    category: SkillCategory
    version: SkillVersion = field(default_factory=SkillVersion)
    status: SkillStatus = SkillStatus.EXPERIMENTAL
    description: str = ""
    long_description: str = ""

    # Capabilities
    capabilities: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # Schema
    inputs: List[SkillInput] = field(default_factory=list)
    outputs: List[SkillOutput] = field(default_factory=list)

    # Dependencies
    dependencies: List[SkillDependency] = field(default_factory=list)
    skills_used: List[str] = field(default_factory=list)  # Other skills this skill uses

    # Lifecycle
    author: str = ""
    license: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deprecated_at: Optional[datetime] = None
    removal_at: Optional[datetime] = None

    # Performance
    estimated_duration_ms: int = 0
    timeout_seconds: int = 30

    # Example
    example_input: Dict[str, Any] = field(default_factory=dict)
    example_output: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillMetrics:
    """Runtime metrics for a skill."""
    invocations: int = 0
    successes: int = 0
    failures: int = 0
    total_duration_ms: int = 0
    avg_duration_ms: float = 0.0
    last_invoked: Optional[datetime] = None
    error_counts: Dict[str, int] = field(default_factory=dict)


class Skill(ABC):
    """
    Abstract base class for all skills.

    Skills are stateless units of capability. They accept inputs,
    produce outputs, and may depend on other skills.
    """

    @property
    @abstractmethod
    def metadata(self) -> SkillMetadata:
        """Get skill metadata."""
        ...

    @abstractmethod
    def execute(self, context: "SkillContext") -> Any:
        """
        Execute the skill.

        Skills are stateless - all state must be passed through context
        or stored in the shared context.

        Args:
            context: SkillContext containing inputs and dependencies

        Returns:
            Skill output (type must match output schema)
        """
        ...

    # ==================== Dependency Injection ====================

    @abstractmethod
    def set_dependency(self, skill_name: str, skill: "Skill") -> None:
        """Set a skill dependency."""
        ...

    @abstractmethod
    def get_dependency(self, skill_name: str) -> Optional["Skill"]:
        """Get a skill dependency."""
        ...

    # ==================== Lifecycle ====================

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize skill (stateless - no persistent state)."""
        ...

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Check skill health."""
        ...

    @abstractmethod
    def cleanup(self) -> None:
        """Release resources."""
        ...
```

---

## Skill Context

```python
@dataclass
class SkillContext:
    """
    Execution context for a skill invocation.

    Contains:
    - Input values
    - Shared context
    - Injected dependencies
    - Metrics collector
    - Configuration
    """

    # Input values (populated by invoker)
    inputs: Dict[str, Any] = field(default_factory=dict)

    # Shared state (from SharedContext)
    shared_context: Dict[str, Any] = field(default_factory=dict)

    # Skill registry for dependency resolution
    registry: "SkillRegistry" = None

    # Injected skill dependencies
    dependencies: Dict[str, "Skill"] = field(default_factory=dict)

    # Metrics collector
    metrics: "MetricsCollector" = None

    # Configuration overrides
    config: Dict[str, Any] = field(default_factory=dict)

    # Execution metadata
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    session_id: Optional[str] = None
    trace_id: Optional[str] = None

    # Skill-specific data
    skill_data: Dict[str, Any] = field(default_factory=dict)

    def get_input(self, name: str, default: Any = None) -> Any:
        """Get input value by name."""
        return self.inputs.get(name, default)

    def get_shared(self, key: str, default: Any = None) -> Any:
        """Get value from shared context."""
        return self.shared_context.get(key, default)

    def set_shared(self, key: str, value: Any) -> None:
        """Set value in shared context."""
        self.shared_context[key] = value

    def require_input(self, name: str) -> Any:
        """Get required input, raise if missing."""
        if name not in self.inputs:
            raise SkillInputError(f"Required input '{name}' not provided")
        return self.inputs[name]

    def get_dependency(self, name: str) -> "Skill":
        """Get injected dependency."""
        if name not in self.dependencies:
            raise SkillDependencyError(f"Dependency '{name}' not injected")
        return self.dependencies[name]


class SkillInputError(Exception):
    """Raised when required input is missing or invalid."""
    pass


class SkillDependencyError(Exception):
    """Raised when dependency is not available."""
    pass


class SkillExecutionError(Exception):
    """Raised when skill execution fails."""
    pass
```

---

## Registration Mechanism

```python
@dataclass
class RegistrationConfig:
    """Configuration for skill registration."""
    allow_duplicate_names: bool = False
    validate_schemas: bool = True
    auto_register_dependencies: bool = True
    overwrite_existing: bool = False


class SkillRegistry:
    """
    Central registry for skill discovery and management.

    Responsibilities:
    - Register skills with metadata
    - Discover skills by capability
    - Resolve skill dependencies
    - Track skill versions
    """

    def __init__(self, config: Optional[RegistrationConfig] = None):
        self._skills: Dict[str, Skill] = {}
        self._metadata: Dict[str, SkillMetadata] = {}
        self._metrics: Dict[str, SkillMetrics] = {}
        self._capability_index: Dict[str, List[str]] = {}  # capability -> skill names
        self._tag_index: Dict[str, List[str]] = {}  # tag -> skill names
        self._config = config or RegistrationConfig()
        self._version_spec_parser = VersionSpecParser()

    # ==================== Registration ====================

    @abstractmethod
    def register(self, skill: Skill, metadata: SkillMetadata,
                 config: Optional[RegistrationConfig] = None) -> bool:
        """
        Register a skill with the registry.

        Args:
            skill: Skill instance (stateless)
            metadata: Skill metadata
            config: Registration configuration

        Returns:
            True if registration successful
        """
        ...

    @abstractmethod
    def unregister(self, name: str, version: Optional[SkillVersion] = None) -> bool:
        """
        Unregister a skill.

        Args:
            name: Skill name
            version: Optional specific version (default: all versions)

        Returns:
            True if unregistration successful
        """
        ...

    @abstractmethod
    def register_batch(self, skills: List[tuple[Skill, SkillMetadata]],
                       config: Optional[RegistrationConfig] = None) -> tuple[int, List[str]]:
        """
        Register multiple skills at once.

        Args:
            skills: List of (skill, metadata) tuples
            config: Registration configuration

        Returns:
            (success_count, error_list)
        """
        ...

    def _validate_metadata(self, metadata: SkillMetadata) -> List[str]:
        """Validate skill metadata before registration."""
        errors = []

        if not metadata.name:
            errors.append("Skill name is required")
        if not metadata.category:
            errors.append("Skill category is required")
        if not metadata.inputs:
            errors.append("At least one input is recommended")
        if not metadata.outputs:
            errors.append("At least one output is recommended")

        # Check for duplicate input names
        input_names = [inp.name for inp in metadata.inputs]
        if len(input_names) != len(set(input_names)):
            errors.append("Duplicate input names found")

        # Check for duplicate output names
        output_names = [out.name for out in metadata.outputs]
        if len(output_names) != len(set(output_names)):
            errors.append("Duplicate output names found")

        return errors

    def _build_indexes(self, name: str, metadata: SkillMetadata) -> None:
        """Build search indexes for the skill."""
        # Capability index
        for capability in metadata.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = []
            if name not in self._capability_index[capability]:
                self._capability_index[capability].append(name)

        # Tag index
        for tag in metadata.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            if name not in self._tag_index[tag]:
                self._tag_index[tag].append(name)

    # ==================== Discovery ====================

    @abstractmethod
    def get(self, name: str, version: Optional[SkillVersion] = None) -> Optional[Skill]:
        """
        Get skill by name and optional version.

        Args:
            name: Skill name
            version: Optional version (default: latest stable)

        Returns:
            Skill instance or None
        """
        ...

    @abstractmethod
    def get_metadata(self, name: str,
                     version: Optional[SkillVersion] = None) -> Optional[SkillMetadata]:
        """
        Get skill metadata by name.

        Args:
            name: Skill name
            version: Optional version

        Returns:
            SkillMetadata or None
        """
        ...

    @abstractmethod
    def find_by_capability(self, capability: str,
                           status: Optional[SkillStatus] = None) -> List[str]:
        """
        Find skills by capability.

        Args:
            capability: Capability string
            status: Optional status filter

        Returns:
            List of skill names
        """
        ...

    @abstractmethod
    def find_by_tag(self, tag: str,
                    status: Optional[SkillStatus] = None) -> List[str]:
        """
        Find skills by tag.

        Args:
            tag: Tag string
            status: Optional status filter

        Returns:
            List of skill names
        """
        ...

    @abstractmethod
    def find_by_category(self, category: SkillCategory,
                         status: Optional[SkillStatus] = None) -> List[str]:
        """
        Find skills by category.

        Args:
            category: Skill category
            status: Optional status filter

        Returns:
            List of skill names
        """
        ...

    @abstractmethod
    def find_compatible(self, input_type: Type, output_type: Type) -> List[str]:
        """
        Find skills compatible with given types.

        Args:
            input_type: Required input type
            output_type: Required output type

        Returns:
            List of skill names that match
        """
        ...

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[str]:
        """
        Search skills by name, description, or tags.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching skill names
        """
        ...

    @abstractmethod
    def list_all(self, status: Optional[SkillStatus] = None) -> List[str]:
        """
        List all registered skills.

        Args:
            status: Optional status filter

        Returns:
            List of skill names
        """
        ...

    @abstractmethod
    def list_versions(self, name: str) -> List[SkillVersion]:
        """
        List all versions of a skill.

        Args:
            name: Skill name

        Returns:
            List of versions
        """
        ...

    # ==================== Dependency Resolution ====================

    @abstractmethod
    def resolve_dependencies(self, skill_name: str,
                             version: Optional[SkillVersion] = None) -> Dict[str, Skill]:
        """
        Resolve all dependencies for a skill.

        Args:
            name: Skill name
            version: Optional version

        Returns:
            Dictionary of dependency_name -> Skill instance
        """
        ...

    @abstractmethod
    def validate_dependencies(self, skill_name: str,
                              version: Optional[SkillVersion] = None) -> tuple[bool, List[str]]:
        """
        Validate that all dependencies can be satisfied.

        Args:
            name: Skill name
            version: Optional version

        Returns:
            (is_valid, list_of_missing_dependencies)
        """
        ...

    # ==================== Metrics ====================

    @abstractmethod
    def record_invocation(self, name: str, success: bool,
                          duration_ms: int, error: Optional[str] = None) -> None:
        """Record skill invocation metrics."""
        ...

    @abstractmethod
    def get_metrics(self, name: str,
                    version: Optional[SkillVersion] = None) -> SkillMetrics:
        """
        Get metrics for a skill.

        Args:
            name: Skill name
            version: Optional version

        Returns:
            SkillMetrics
        """
        ...

    @abstractmethod
    def get_all_metrics(self) -> Dict[str, SkillMetrics]:
        """Get metrics for all skills."""
        ...

    @abstractmethod
    def reset_metrics(self, name: Optional[str] = None) -> None:
        """
        Reset metrics for a skill or all skills.

        Args:
            name: Optional skill name (default: all)
        """
        ...

    # ==================== Version Management ====================

    @abstractmethod
    def deprecate(self, name: str, version: SkillVersion,
                  removal_date: Optional[datetime] = None) -> bool:
        """
        Mark a skill version as deprecated.

        Args:
            name: Skill name
            version: Version to deprecate
            removal_date: Optional removal date

        Returns:
            True if successful
        """
        ...

    @abstractmethod
    def get_deprecated(self) -> List[str]:
        """Get all deprecated skill versions."""
        ...

    @abstractmethod
    def is_deprecated(self, name: str, version: SkillVersion) -> bool:
        """Check if a skill version is deprecated."""
        ...
```

---

## Invocation Interface

```python
@dataclass
class InvocationConfig:
    """Configuration for skill invocation."""
    timeout_seconds: int = 30
    retry_on_failure: bool = False
    max_retries: int = 3
    retry_delay_ms: int = 100
    collect_metrics: bool = True
    enable_tracing: bool = False


@dataclass
class InvocationResult:
    """Result of skill invocation."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    duration_ms: int = 0
    retries: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SkillInvoker:
    """
    Invokes skills with validation and error handling.

    Responsibilities:
    - Validate inputs against schema
    - Execute skills with proper context
    - Handle errors and retries
    - Record metrics
    """

    def __init__(self, registry: SkillRegistry):
        self._registry = registry

    def invoke(self, skill_name: str, inputs: Dict[str, Any],
               config: Optional[InvocationConfig] = None,
               shared_context: Optional[Dict[str, Any]] = None) -> InvocationResult:
        """
        Invoke a skill by name.

        Args:
            skill_name: Name of skill to invoke
            inputs: Input values
            config: Invocation configuration
            shared_context: Shared context for state

        Returns:
            InvocationResult with output or error
        """
        ...

    def invoke_with_version(self, skill_name: str,
                            version: SkillVersion, inputs: Dict[str, Any],
                            config: Optional[InvocationConfig] = None,
                            shared_context: Optional[Dict[str, Any]] = None) -> InvocationResult:
        """
        Invoke a specific version of a skill.

        Args:
            skill_name: Name of skill
            version: Specific version
            inputs: Input values
            config: Invocation configuration
            shared_context: Shared context

        Returns:
            InvocationResult
        """
        ...

    def invoke_chain(self, chain: List[Dict[str, Any]],
                     initial_input: Dict[str, Any],
                     shared_context: Optional[Dict[str, Any]] = None) -> InvocationResult:
        """
        Invoke a chain of skills.

        Args:
            chain: List of {skill_name, input_mapping} steps
            initial_input: Initial input for first skill
            shared_context: Shared context

        Returns:
            Result from final skill
        """
        ...

    def validate_input(self, skill_name: str,
                       inputs: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate inputs against skill schema.

        Args:
            skill_name: Skill name
            inputs: Input values

        Returns:
            (is_valid, list_of_errors)
        """
        ...

    def validate_output(self, skill_name: str,
                        output: Any) -> tuple[bool, List[str]]:
        """
        Validate output against skill schema.

        Args:
            skill_name: Skill name
            output: Output value

        Returns:
            (is_valid, list_of_errors)
        """
        ...
```

---

## Validation Rules

### Registration Validation

```python
class RegistrationValidator:
    """Validates skill registration."""

    @staticmethod
    def validate_metadata(metadata: SkillMetadata) -> List[ValidationError]:
        """Validate skill metadata."""
        errors = []

        # Required fields
        if not metadata.name:
            errors.append(ValidationError("name", "required", "Skill name is required"))
        if not metadata.category:
            errors.append(ValidationError("category", "required", "Skill category is required"))

        # Name format
        if metadata.name and not re.match(r'^[a-z][a-z0-9_]*$', metadata.name):
            errors.append(ValidationError("name", "format",
                "Skill name must be lowercase with underscores"))

        # Version format
        if metadata.version:
            try:
                parts = str(metadata.version).split('.')
                if len(parts) != 3:
                    raise ValueError()
                for p in parts:
                    int(p)
            except ValueError:
                errors.append(ValidationError("version", "format",
                    "Version must be semver format (major.minor.patch)"))

        # Input validation
        for inp in metadata.inputs:
            if not inp.name:
                errors.append(ValidationError(f"inputs[{inp.name}]", "required", "Input name required"))
            if inp.required and inp.default is not None:
                errors.append(ValidationError(f"inputs[{inp.name}]", "conflict",
                    "Required input cannot have default value"))

        return errors

    @staticmethod
    def validate_schema_compatibility(
        producer_skill: SkillMetadata,
        consumer_skill: SkillMetadata
    ) -> List[ValidationError]:
        """Validate that producer output matches consumer input."""
        errors = []

        # Build output type map
        output_types = {out.name: out.type for out in producer_skill.outputs}

        # Check each consumer input against producer outputs
        for inp in consumer_skill.inputs:
            if inp.name in output_types:
                # Types should be compatible
                if not _types_compatible(output_types[inp.name], inp.type):
                    errors.append(ValidationError("schema", "incompatible",
                        f"Output '{inp.name}' type {output_types[inp.name]} "
                        f"not compatible with input type {inp.type}"))

        return errors
```

### Invocation Validation

```python
class InvocationValidator:
    """Validates skill invocation."""

    @staticmethod
    def validate_inputs(metadata: SkillMetadata,
                        inputs: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate inputs against schema."""
        errors = []

        # Check required inputs
        for inp in metadata.inputs:
            if inp.required and inp.name not in inputs:
                errors.append(f"Required input '{inp.name}' missing")
                continue

            if inp.name in inputs:
                value = inputs[inp.name]

                # Type validation
                if inp.type and not _is_type_compatible(value, inp.type):
                    errors.append(
                        f"Input '{inp.name}' type {type(value)} "
                        f"does not match schema type {inp.type}"
                    )

                # Custom validation rules
                for rule in inp.validation_rules:
                    if not _apply_validation_rule(value, rule):
                        errors.append(
                            f"Input '{inp.name}' failed validation: {rule.get('message')}"
                        )

        return len(errors) == 0, errors

    @staticmethod
    def validate_outputs(metadata: SkillMetadata,
                         output: Any) -> tuple[bool, List[str]]:
        """Validate output against schema."""
        errors = []

        if not metadata.outputs:
            return True, []  # No outputs to validate

        # Output is typically a dict - check each declared output
        if isinstance(output, dict):
            for out in metadata.outputs:
                if out.name in output:
                    value = output[out.name]
                    if out.type and not _is_type_compatible(value, out.type):
                        errors.append(
                            f"Output '{out.name}' type {type(value)} "
                            f"does not match schema type {out.type}"
                        )
        elif metadata.outputs:
            # Single output without name - check type
            out = metadata.outputs[0]
            if out.type and not _is_type_compatible(output, out.type):
                errors.append(
                    f"Output type {type(output)} does not match schema type {out.type}"
                )

        return len(errors) == 0, errors
```

---

## Skill Composition

```python
class SkillComposer:
    """Composes skills into chains and pipelines."""

    @staticmethod
    def compose_linear(skills: List[str],
                       registry: SkillRegistry) -> "ComposedSkill":
        """
        Compose skills into a linear chain.

        Output of each skill becomes input to next.

        Args:
            skills: List of skill names in order
            registry: Skill registry

        Returns:
            ComposedSkill that chains all skills
        """
        ...

    @staticmethod
    def compose_parallel(skills: List[str],
                         reducer: Optional[str] = None) -> "ComposedSkill":
        """
        Compose skills to run in parallel.

        Args:
            skills: List of skill names
            reducer: Optional skill name to reduce results

        Returns:
            ComposedSkill that runs skills in parallel
        """
        ...

    @staticmethod
    def compose_fanout(skill: str,
                       splitter: str) -> "ComposedSkill":
        """
        Compose skills with fan-out pattern.

        Args:
            skill: Skill to fan out
            splitter: Skill that determines splits

        Returns:
            ComposedSkill with fan-out pattern
        """
        ...


class ComposedSkill(Skill):
    """
    A skill composed of other skills.

    Provides:
    - Linear chaining
    - Parallel execution
    - Fan-out/fan-in patterns
    """

    def __init__(self, name: str, skills: List[Skill]):
        self._name = name
        self._skills = skills
        self._metadata = self._build_metadata()

    def _build_metadata(self) -> SkillMetadata:
        """Build metadata from composed skills."""
        # Combine inputs from first skill
        # Combine outputs from last skill
        # Union of all capabilities
        ...

    def execute(self, context: SkillContext) -> Any:
        """Execute composed skill chain."""
        result = None
        for skill in self._skills:
            context.inputs = {"input": result} if result else context.inputs
            result = skill.execute(context)
        return result
```

---

## Summary

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| **Skill** | Base class for all skills | `execute(context)`, `set_dependency(name, skill)` |
| **SkillMetadata** | Skill declaration | name, inputs, outputs, dependencies, capabilities |
| **SkillContext** | Execution context | `get_input`, `get_shared`, `require_input` |
| **SkillRegistry** | Central catalog | `register`, `get`, `find_by_capability`, `resolve_dependencies` |
| **SkillInvoker** | Execution engine | `invoke`, `invoke_chain`, `validate_input/output` |
| **SkillComposer** | Skill chaining | `compose_linear`, `compose_parallel`, `compose_fanout` |

**PHR**: `history/prompts/skill-registry/001-define-skill-registry.spec.prompt.md`

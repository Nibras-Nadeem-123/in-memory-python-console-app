# Reusable Cognitive Skills Specification

**Spec ID:** REUSABLE-COGNITIVE-SKILLS
**Version:** 1.0.0
**Status:** Draft
**Created:** 2025-12-29

## 1. Overview

This specification defines the core cognitive skills that form the building blocks of the intelligence system. These skills are:

- **Stateless:** No internal state between invocations; all context passed externally
- **Domain-agnostic:** No hardcoded business logic; operates on abstract structures
- **Composable:** Skills can be combined to form complex reasoning chains

## 2. Skill Design Principles

### 2.1 Common Characteristics

All skills share these properties:

```python
class CognitiveSkill(Generic[Input, Output]):
    """Base interface for all cognitive skills."""

    @property
    def skill_id(self) -> str:
        """Unique identifier for skill discovery and routing."""

    @property
    def version(self) -> str:
        """Semantic version for compatibility tracking."""

    async def invoke(
        self,
        input: Input,
        context: Context
    ) -> SkillResult[Output]:
        """
        Invoke the skill with given input and context.

        Args:
            input: Skill-specific input structure
            context: Shared context (stateless skill reads from it)

        Returns:
            SkillResult containing output or failure classification
        """
```

### 2.2 Skill Contract

| Aspect | Requirement |
|--------|-------------|
| **Idempotency** | Same input + context = same output |
| **Determinism** | No random or time-dependent behavior |
| **Purity** | No side effects; context is read-only |
| **Composability** | Output is valid input to other skills |
| **Timeout** | All skills honor the reasoning timeout budget |
| **Memory** | All skills operate within memory constraints |

## 3. Skill Definitions

### 3.1 Skill: Intent Parsing

**Skill ID:** `cognitive.intent.parse`
**Version:** 1.0.0

#### Purpose

Extract structured intent from raw user input. Converts natural language or unstructured queries into a canonical intent representation with identified entities and confidence scores.

#### Inputs

```yaml
Input:
  raw_text: string                    # Raw user input
  intent_types: list[string]          # Expected intent types (optional)
  context:
    session_history: list[Message]    # Previous messages (optional)
    user_profile: dict                # User preferences (optional)
    entities_known: list[Entity]      # Pre-known entities (optional)
```

#### Outputs

```yaml
Output:
  intent_type: string                 # Canonical intent classification
  entities: list[Entity]              # Extracted entities with spans
  parameters: dict                    # Parsed parameters from input
  confidence: float                   # 0.0-1.0 confidence score
  ambiguity: AmbiguityReport | null   # If multiple interpretations
  sentiment: Sentiment | null         # Optional sentiment (positive/negative)
```

#### Failure Modes

| Failure Type | Classification | Handling |
|--------------|----------------|----------|
| Empty input | `INVALID_INPUT` | Return empty result, don't fail |
| Unrecognized intent | `AMBIGUOUS` | Return null intent_type, confidence=0 |
| Multiple interpretations | `AMBIGUOUS` | Return ambiguity report with alternatives |
| Parse error (malformed) | `PARSE_ERROR` | Return error detail, suggest rephrase |
| Context expired | `CONTEXT_ERROR` | Request context refresh |

---

### 3.2 Skill: Specification Generation

**Skill ID:** `cognitive.spec.generate`
**Version:** 1.0.0

#### Purpose

Transform parsed intent into a formal specification structure. Creates a structured, requirements-grade document that defines what needs to be built/achieved without prescribing how.

#### Inputs

```yaml
Input:
  intent: ParsedIntent               # Output from Intent Parsing
  spec_template: string              # Template ID or content
  constraints: list[Constraint]      # Known constraints
  context: Context                   # Shared context
```

#### Outputs

```yaml
Output:
  spec_id: string                    # Unique specification identifier
  title: string                      # Human-readable title
  overview: string                   # Summary of what/why
  requirements: list[Requirement]    # Functional requirements
  non_goals: list[string]            # Explicitly out of scope
  acceptance_criteria: list[string]  # Success definitions
  dependencies: list[string]         # External dependencies
  risks: list[Risk]                  # Identified risks
  metadata:
    generated_at: timestamp
    source_intent: string
    confidence: float
```

#### Failure Modes

| Failure Type | Classification | Handling |
|--------------|----------------|----------|
| Missing required intent data | `INVALID_INPUT` | Request missing fields |
| Conflicting requirements | `CONFLICT` | Return conflict report with suggestions |
| Template not found | `NOT_FOUND` | Use default template, warn |
| Requirement too vague | `VALIDATION_WARNING` | Return with clarification requests |

---

### 3.3 Skill: Task Decomposition

**Skill ID:** `cognitive.task.decompose`
**Version:** 1.0.0

#### Purpose

Break down a high-level goal or specification into a hierarchical structure of smaller, actionable tasks. Identifies dependencies and creates a task tree.

#### Inputs

```yaml
Input:
  goal: string                       # High-level goal description
  spec: Specification | null         # Associated spec (optional)
  constraints: list[Constraint]      # Time, resource, scope limits
  available_skills: list[string]     # Registry of skill IDs
  context: Context                   # Shared context
```

#### Outputs

```yaml
Output:
  task_tree:
    root_tasks: list[TaskNode]
  task_graph:
    nodes: list[TaskNode]
    edges: list[DependencyEdge]      # from_id -> to_id
  total_estimate: TimeEstimate
  parallelizable: list[list[string]] # Groups that can run in parallel
  critical_path: list[string]        # Task IDs on critical path
  skill_requirements: dict           # skill_id -> count/usage
```

Where `TaskNode`:
```yaml
TaskNode:
  task_id: string
  description: string
  type: "atomic" | "composite"
  children: list[string]             # Child task IDs (if composite)
  skills_required: list[string]      # Skill IDs to invoke
  parameters: dict                   # Input parameters for this task
  success_criteria: list[string]
  estimated_effort: string
```

#### Failure Modes

| Failure Type | Classification | Handling |
|--------------|----------------|----------|
| Goal too vague | `INVALID_INPUT` | Request clarification |
| Circular dependency detected | `VALIDATION_ERROR` | Fail, return cycle graph |
| Missing required skill | `UNAVAILABLE_SKILL` | Fail, suggest alternative or custom skill |
| Decomposition too deep | `COMPLEXITY_ERROR` | Return partial, suggest summarization |

---

### 3.4 Skill: Constraint Validation

**Skill ID:** `cognitive.constraint.validate`
**Version:** 1.0.0

#### Purpose

Validate that a plan or set of tasks satisfies all known constraints. Checks for conflicts, violations, and boundary conditions before execution.

#### Inputs

```yaml
Input:
  plan: ActionPlan | TaskTree        # Plan or task structure to validate
  constraints: list[Constraint]      # Explicit constraints to check
  policies: list[Policy]             # Organization policies
  resource_limits: ResourceBudget    # Available resources
  context: Context                   # Shared context
```

#### Outputs

```yaml
Output:
  is_valid: boolean
  violations: list[Violation]        # Empty if is_valid
  warnings: list[Warning]            # Non-blocking concerns
  suggestions: list[Suggestion]      # Optional improvements
  validation_id: string              # For audit trail
  checked_constraints: list[string]  # Which constraints were checked
```

Where `Violation`:
```yaml
Violation:
  constraint_id: string
  severity: "error" | "warning" | "info"
  description: string
  affected_tasks: list[string]
  remediation: string | null
```

#### Failure Modes

| Failure Type | Classification | Handling |
|--------------|----------------|----------|
| Invalid constraint format | `INVALID_INPUT` | Reject, explain format |
| Constraint conflict | `CONFLICT` | Return all conflicts |
| Resource budget exceeded | `RESOURCE_ERROR` | Fail, show exceeded limits |
| Policy violation | `POLICY_VIOLATION` | Fail, require override |

---

### 3.5 Skill: Execution Planning

**Skill ID:** `cognitive.plan.generate`
**Version:** 1.0.0

#### Purpose

Generate a concrete execution plan from a validated task decomposition. Creates an ordered sequence of skill invocations with timing, resources, and success criteria.

#### Inputs

```yaml
Input:
  task_tree: TaskTree                # Output from Task Decomposition
  validation: ValidationResult        # Output from Constraint Validation
  available_resources: Resources      # Current resource state
  execution_policies: list[Policy]    # Retry, timeout, fallback rules
  context: Context                   # Shared context
```

#### Outputs

```yaml
Output:
  plan_id: string
  steps: list[ExecutionStep]
  total_duration: Duration
  resource_allocation: dict          # resource -> allocated amount
  risk_assessment: RiskAssessment
  rollback_plan: list[Step]          # Steps to undo (if supported)
  success_metrics: dict              # metric -> target value

ExecutionStep:
  step_id: string
  skill_id: string
  parameters: dict
  dependencies: list[string]         # Must complete before this
  executes_after: list[string]       # Alternative to dependencies
  timeout: Duration
  retry_policy: RetryConfig
  fallback: StepFallback | null
  success_criteria: list[string]
```

#### Failure Modes

| Failure Type | Classification | Handling |
|--------------|----------------|----------|
| Invalid task tree | `INVALID_INPUT` | Reject with validation errors |
| Resource allocation failed | `RESOURCE_ERROR` | Fail, show shortages |
| No valid execution order | `SCHEDULING_ERROR` | Fail, explain deadlock |
| Timeout too short | `VALIDATION_WARNING` | Warn, suggest minimum |

---

### 3.6 Skill: Result Evaluation

**Skill ID:** `cognitive.result.evaluate`
**Version:** 1.0.0

#### Purpose

Compare execution results against original intent and success criteria. Determines success/failure, identifies gaps, and generates feedback for refinement.

#### Inputs

```yaml
Input:
  execution_result: ExecutionResult  # Raw execution output
  original_intent: ParsedIntent      # Original user intent
  success_criteria: list[string]     # Defined acceptance criteria
  baseline_metrics: dict | null      # Previous run metrics (optional)
  context: Context                   # Shared context
```

#### Outputs

```yaml
Output:
  overall_score: float               # 0.0-1.0 composite score
  passed_criteria: list[string]
  failed_criteria: list[string]
  gaps: list[Gap]                    # What was missed
  quality_metrics: dict              # Specific metric values
  recommendations: list[Recommendation]
  refinement_suggestions: list[RefinementSuggestion]
  should_refine: boolean             # Whether refinement is warranted
  evaluation_id: string
```

Where `Gap`:
```yaml
Gap:
  description: string
  severity: "critical" | "major" | "minor"
  cause: "missing" | "incorrect" | "incomplete" | "timing"
  suggested_fix: string
```

#### Failure Modes

| Failure Type | Classification | Handling |
|--------------|----------------|----------|
| Missing result data | `INVALID_INPUT` | Request complete data |
| Criteria too vague | `VALIDATION_WARNING` | Return score with caveats |
| Evaluation timeout | `TIMEOUT` | Return partial evaluation |
| Metrics unavailable | `DATA_ERROR` | Skip affected metrics, warn |

---

## 4. Skill Composition Patterns

### 4.1 Linear Pipeline

```
Intent Parsing → Specification Generation → Task Decomposition
                 → Constraint Validation → Execution Planning → Result Evaluation
```

### 4.2 Parallel Execution

```
                    ┌─────────────────┐
                    │ Task Decomposer │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ Validator│   │ Validator│   │ Validator│
        └────┬─────┘   └────┬─────┘   └────┬─────┘
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                    ┌──────────────┐
                    │ Plan Merger  │
                    └──────────────┘
```

### 4.3 Conditional Branching

```
Intent Parser ──► Recognized? ──► Yes ──► Continue Pipeline
                  │
                  └── No ──► Clarification Skill ──► Back to Intent
```

### 4.4 Iteration (Refinement Loop)

```
Execution Planning ──► Execute ──► Evaluate ──► Success? ──► Yes ──► Done
                                          │
                                          └── No ──► Refine ──► Back to Planning
```

## 5. Skill Registry

Skills are discovered and routed via a registry:

```yaml
Registry Entry:
  skill_id: string
  version: string
  description: string
  input_schema: json-schema
  output_schema: json-schema
  dependencies: list[string]
  capabilities: list[string]
  author: string
  license: string
```

**Registered Skills:**
| Skill ID | Version | Purpose |
|----------|---------|---------|
| `cognitive.intent.parse` | 1.0.0 | Parse raw intent |
| `cognitive.spec.generate` | 1.0.0 | Generate specifications |
| `cognitive.task.decompose` | 1.0.0 | Decompose goals into tasks |
| `cognitive.constraint.validate` | 1.0.0 | Validate constraints |
| `cognitive.plan.generate` | 1.0.0 | Generate execution plans |
| `cognitive.result.evaluate` | 1.0.0 | Evaluate results |

## 6. Quality Standards

### 6.1 Performance Targets

| Skill | Latency (p95) | Memory |
|-------|---------------|--------|
| Intent Parsing | <100ms | <10MB |
| Spec Generation | <200ms | <20MB |
| Task Decomposition | <300ms | <30MB |
| Constraint Validation | <100ms | <10MB |
| Execution Planning | <300ms | <30MB |
| Result Evaluation | <150ms | <15MB |

### 6.2 Accuracy Targets

| Skill | Target | Measurement |
|-------|--------|-------------|
| Intent Parsing | >95% top-1 accuracy | Manual eval |
| Task Decomposition | >90% completeness | Coverage analysis |
| Constraint Validation | 100% violation detection | Test suite |
| Result Evaluation | >90% agreement with human | Blind eval |

## 7. Out of Scope

- **Domain-specific skills** — Business logic, integrations, tools
- **LLM provider integration** — Abstraction layer handles this
- **Skill execution runtime** — Separate specification
- **Skill versioning/migration** — Future enhancement

## 8. References

- **Intelligence Model:** `specs/core-intelligence-model/spec.md`
- **Skills System:** `specs/reusable-skills-system/spec.md`
- **Context Model:** `specs/shared-context-model/spec.md`
- **Constitution:** `.specify/memory/constitution.md`

---

**Spec Status:** Draft
**Review Required:** Yes
**Approval Authority:** Architect

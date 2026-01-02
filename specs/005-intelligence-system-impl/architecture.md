# SDD System Architecture

This document describes the architecture of the Spec-Driven Development system and how its components interact.

## Overview

The SDD system transforms natural language user intent into structured, implementation-ready artifacts through a multi-stage pipeline:

```
User Input
    ↓
[Stage 1] IntentAgent + Skills
    ↓
[Stage 2] SpecAgent + Template
    ↓
[Stage 3] PlanAgent + Skills
    ↓
[Stage 4] GuideAgent + Skills
    ↓
Generated Artifacts (spec.md, plan.md, guide.md)
```

## Component Architecture

### 1. Core Layer (Frozen)

The core intelligence layer provides the foundation for all AI-driven functionality:

**Components:**
- `ExecutionContext` - Base context for all intelligence operations
- `Skill` - Abstract base class for reusable cognitive skills
- `SkillRegistry` - Central registry for skill management
- `IntelligenceEngine` - Main orchestrator for goal execution

**Design Principles:**
- **Frozen**: Core logic cannot be modified without formal architectural review
- **Extensible**: New capabilities added through skills, not core changes
- **Stateless**: Skills are pure functions (no mutable state)
- **Composable**: Skills can be combined in chains/pipelines

### 2. SDD Layer (Extendable)

The SDD system extends the core intelligence layer for spec-driven development:

**Components:**
- `SDDContext` - Extended context with intent and artifact storage
- `IntentAgent` - Parses and classifies user intent
- `SpecAgent` - Generates specification documents
- `PlanAgent` - Creates implementation plans with tasks
- `GuideAgent` - Provides execution guidance and scaffolding
- `SDDEngine` - Orchestrates full SDD workflow

**SDD Skills:**
- `IntentParsingSkill` - Classifies intent type
- `AmbiguityDetectionSkill` - Identifies unclear phrases
- `RequirementExtractionSkill` - Extracts requirements from intent
- `TaskBreakdownSkill` - Breaks specs into tasks
- `DependencyResolutionSkill` - Resolves task dependencies
- `CodeScaffoldingSkill` - Generates code templates
- `BestPracticesSkill` - Provides language/framework patterns

### 3. Orchestration Layer

Manages workflow execution and stage transitions:

**Components:**
- `WorkflowManager` - Coordinates multi-stage execution
- `SkillComposer` - Combines skills in chains
- `Checkpoint` - Save/resume workflow state

### 4. Interface Layer

User-facing interfaces for interaction:

**Components:**
- `CLI` - Command-line interface for SDD operations
- `main.py` - Entry point with command routing

## Data Flow

### Intent Parsing Flow

```
User Input (text)
    ↓
IntentAgent.execute()
    ├─→ IntentParsingSkill → IntentType
    ├─→ AmbiguityDetectionSkill → Ambiguities
    └─→ Metadata extraction
    ↓
SDDContext.add_intent(Intent)
```

### Specification Generation Flow

```
SDDContext (with Intent)
    ↓
SpecAgent.execute()
    ├─→ RequirementExtractionSkill → Requirements
    ├─→ SpecTemplate.load() → Template
    └─→ Generate spec.md
    ↓
SDDContext.add_artifact("spec", spec_content)
```

### Planning Flow

```
SDDContext (with Spec artifact)
    ↓
PlanAgent.execute()
    ├─→ TaskBreakdownSkill → Tasks
    ├─→ DependencyResolutionSkill → Dependencies
    └─→ Generate plan.md
    ↓
SDDContext.add_artifact("plan", plan_content)
```

### Guidance Generation Flow

```
SDDContext (with Plan artifact)
    ↓
GuideAgent.execute()
    ├─→ CodeScaffoldingSkill → Templates
    ├─→ BestPracticesSkill → Patterns
    └─→ Generate guide.md
    ↓
SDDContext.add_artifact("guide", guide_content)
```

## Agent Interface

All SDD agents implement the `Agent` base class:

```python
class Agent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique agent identifier."""
        pass

    @abstractmethod
    def can_handle(self, context: SDDContext) -> bool:
        """Return True if agent should handle current context."""
        pass

    @abstractmethod
    def execute(self, context: SDDContext, **kwargs):
        """Execute agent logic and return result."""
        pass
```

### Agent Routing Logic

```
Context State            → Which Agent Handles
─────────────────────────────────────────────────────────────
No intent                 → IntentAgent
Intent.type == SPECIFY       → SpecAgent
Intent.type == PLAN          → PlanAgent
Plan artifact exists         → GuideAgent
```

## Skill Composition

Skills can be composed into execution chains:

### Sequential Chain

```python
composer = SkillComposer(context)
composer.register_chain("parse_intent", [
    SkillChainStep(IntentParsingSkill(), "intent"),
    SkillChainStep(AmbiguityDetectionSkill(), "ambiguities")
])

result = composer.execute_chain("parse_intent", {"text": user_input})
# result.outputs = {"intent": ..., "ambiguities": ...}
```

### Parallel Execution

```python
skills = [IntentParsingSkill(), RequirementExtractionSkill()]
outputs = composer.execute_parallel(skills)
# outputs = {"outputs": {...}, "errors": {...}}
```

## Error Handling

### SDD-Specific Exceptions

- `IntentParsingError` - Failed to parse user input
- `SpecGenerationError` - Failed to generate specification
- `PlanGenerationError` - Failed to create plan
- `GuideGenerationError` - Failed to create guide
- `WorkflowError` - Generic workflow execution failure
- `AmbiguityError` - Ambiguous input detected
- `CircularDependencyError` - Circular task dependencies detected

### Error Recovery

The system implements error handling at multiple levels:

1. **Skill Level**: Each skill can raise `SkillExecutionError`
2. **Agent Level**: Agents catch and log skill errors
3. **Workflow Level**: WorkflowManager handles stage failures
4. **CLI Level**: CLI catches and formats errors for display

## State Management

### Context State

The `SDDContext` maintains:

- `intent` - Parsed user intent
- `artifacts` - Dictionary of generated artifacts
- `workflow_state` - Current stage in pipeline
- `events` - Event history for debugging

### Workflow States

```
initialized → clarification → specification → planning → guide_generation → complete
     ↓              ↓             ↓            ↓                   ↓
   (abort)         (abort)      (abort)             (done)
```

### Checkpoints

WorkflowManager creates checkpoints after each stage:

```python
Checkpoint(
    stage=WorkflowStage.SPEC,
    context_data={"artifacts": {...}, "state": "specification"},
    status="completed",
    timestamp="2025-12-30T10:30:00"
)
```

Workflows can resume from checkpoints without re-executing completed stages.

## CLI Commands

### Parse Command

```bash
python -m src.intelligence.main --sdd parse "Create user auth system"
```

Output: Intent analysis with type, confidence, and metadata.

### Spec Command

```bash
python -m src.intelligence.main --sdd spec "Create user auth system"
```

Output: Generated specification document.

### Plan Command

```bash
python -m src.intelligence.main --sdd plan spec.md
```

Output: Implementation plan with tasks and dependencies.

### Guide Command

```bash
python -m src.intelligence.main --sdd guide plan.md
```

Output: Execution guide with scaffolding and best practices.

### Pipeline Command

```bash
python -m src.intelligence.main --sdd pipeline "Create user auth system" --start intent --end guide
```

Output: All artifacts (intent, spec, plan, guide) saved to directory.

## Integration Points

### Extending SDD with New Agents

```python
from src.intelligence.sdd import Agent, SDDContext

class CustomAgent(Agent):
    @property
    def name(self) -> str:
        return "custom"

    def can_handle(self, context: SDDContext) -> bool:
        # Define when to execute
        return context.workflow_state == "custom_stage"

    def execute(self, context: SDDContext, **kwargs):
        # Custom logic
        return result
```

Register in `SDDEngine._register_builtin_agents()`.

### Extending SDD with New Skills

```python
from src.intelligence.skills import Skill, SDDContext
from src.intelligence.skills.skill_registry import SYSTEM_SKILL_REGISTRY

class CustomSkill(Skill):
    @property
    def name(self) -> str:
        return "custom"

    def execute(self, context: SDDContext, **kwargs):
        # Custom logic
        return result

# Auto-register
SYSTEM_SKILL_REGISTRY.register(CustomSkill())
```

## Performance Considerations

### Efficiency

- **Agent Execution**: Each agent runs once per stage
- **Skill Chaining**: Skills execute sequentially with data passing
- **Template Caching**: Spec templates loaded once and reused
- **Context In-Memory**: All state in memory (no disk I/O during pipeline)

### Scalability

- **Concurrent Skills**: Parallel execution supported via `SkillComposer`
- **Checkpoint Management**: Checkpoints allow pause/resume
- **Artifact Storage**: Artifacts stored in memory (optional persistence)

## Security Considerations

- **Input Validation**: All user input validated before processing
- **Sanitization**: File paths and external references checked
- **Error Messages**: No sensitive data leaked in error messages
- **Sandboxing**: Code execution only through controlled environments

## Testing Strategy

### Unit Tests

Test each agent and skill independently:

```python
def test_intent_agent():
    context = SDDContext("create a user system")
    agent = IntentAgent()
    intent = agent.execute(context)
    assert intent.type == IntentType.SPECIFY
```

### Integration Tests

Test full pipeline:

```python
def test_full_pipeline():
    context = SDDContext("create a REST API for todos")
    engine = get_sdd_engine()
    results = engine.execute(context)
    assert "spec" in results["artifacts"]
    assert "plan" in results["artifacts"]
    assert "guide" in results["artifacts"]
```

## Future Extensions

### Potential Enhancements

1. **AI-Powered Generation**: Replace template-based with LLM generation
2. **Multi-Language Support**: Add support for TypeScript, Java, Go, etc.
3. **Interactive Clarification**: Chat-based ambiguity resolution
4. **Version Control Integration**: Auto-commit generated artifacts
5. **CI/CD Integration**: Generate GitHub Actions/Jenkins workflows
6. **Template Library**: User-customizable templates for different domains

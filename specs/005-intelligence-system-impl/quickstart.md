# SDD System Quickstart Guide

This guide demonstrates how to use the Spec-Driven Development (SDD) system to transform natural language intent into implementation artifacts.

## Overview

The SDD system provides a multi-stage pipeline:

1. **Intent Parsing**: Transform natural language → structured Intent
2. **Specification**: Generate formal spec.md from Intent
3. **Planning**: Create implementation plan.md from spec
4. **Guidance**: Generate development guide.md with scaffolding

## Installation

```bash
# The SDD system is already included in the intelligence framework
pip install -e .
```

## Quick Example

### 1. Parse User Intent

```python
from src.intelligence import get_sdd_engine

# Initialize SDD engine
engine = get_sdd_engine()

# Define user intent
user_intent = """
Create a user authentication system with login, logout, and password reset.
Users should authenticate via email and password. Include JWT token generation.
Support rate limiting on login attempts. Store passwords with bcrypt hashing.
"""

# Parse intent
results = engine.execute(user_intent, start_stage="intent", end_stage="intent")
intent = results["artifacts"]["intent"]

print(f"Intent Type: {intent.type}")
print(f"Confidence: {intent.confidence}")
print(f"Metadata: {intent.metadata}")
```

**Output:**
```
Intent Type: SPECIFY
Confidence: 0.95
Metadata: {'entities': ['user', 'authentication', 'JWT'], 'technologies': ['bcrypt']}
```

### 2. Generate Specification

```python
# Continue from intent to spec
results = engine.execute(user_intent, start_stage="intent", end_stage="spec")
spec = results["artifacts"]["spec"]

print(f"Spec Title: {spec.title}")
print(f"Requirements: {len(spec.requirements)}")
print(f"Acceptance Criteria: {len(spec.acceptance_criteria)}")
```

**Output:**
```
Spec Title: User Authentication System
Requirements: 5
Acceptance Criteria: 8
```

### 3. Generate Implementation Plan

```python
# Generate full plan
results = engine.execute(user_intent, start_stage="intent", end_stage="plan")
plan = results["artifacts"]["plan"]

print(f"Plan Title: {plan.title}")
print(f"Tasks: {len(plan.tasks)}")
print(f"Architecture: {plan.architecture[:100]}...")
```

**Output:**
```
Plan Title: User Authentication Implementation Plan
Tasks: 12
Architecture: RESTful API architecture with JWT middleware, bcrypt password hashing...
```

### 4. Full Pipeline (Intent → Guide)

```python
# Execute complete SDD pipeline
results = engine.execute(
    user_intent,
    start_stage="intent",
    end_stage="guide"
)

# Access all artifacts
intent = results["artifacts"]["intent"]
spec = results["artifacts"]["spec"]
plan = results["artifacts"]["plan"]
guide = results["artifacts"]["guide"]

print(f"Guide Title: {guide.title}")
print(f"Getting Started Section: {len(guide.getting_started)}")
print(f"Code Patterns: {len(guide.code_patterns)}")
```

## CLI Usage

### Using SDD Commands

```bash
# Parse intent from command line
python -m src.intelligence.sdd.cli parse-intent "Create a todo list app"

# Generate specification
python -m src.intelligence.sdd.cli generate-spec "Create a todo list app"

# Generate plan
python -m src.intelligence.sdd.cli generate-plan "Create a todo list app"

# Generate complete guide
python -m src.intelligence.sdd.cli generate-guide "Create a todo list app"
```

## Working with Context

The SDD system uses `SDDContext` to track state across stages:

```python
from src.intelligence.sdd import SDDContext, get_sdd_engine

# Create context
context = SDDContext("my-project")

# Execute stages with persistent context
engine = get_sdd_engine()

# Stage 1: Intent
context = engine.workflow.execute_stage(context, "intent", user_input="Build a REST API")

# Stage 2: Spec (uses intent from context)
context = engine.workflow.execute_stage(context, "spec")

# Stage 3: Plan (uses spec from context)
context = engine.workflow.execute_stage(context, "plan")

# Access artifacts
print(f"Intent: {context.intent}")
print(f"Spec artifact: {context.get_artifact('spec')}")
print(f"Plan artifact: {context.get_artifact('plan')}")
```

## Integration Scenarios

### Scenario 1: Automated Documentation Generation

```python
# Input: Existing codebase
# Output: Specification and plan documents

from src.intelligence import get_sdd_engine

# Reverse engineer from code
code_summary = """
Express.js API with 3 endpoints: /users, /posts, /comments.
Uses PostgreSQL database. JWT authentication on protected routes.
"""

engine = get_sdd_engine()
results = engine.execute(code_summary, start_stage="spec", end_stage="plan")

# Generate documentation
spec = results["artifacts"]["spec"]
plan = results["artifacts"]["plan"]

# Save to files
with open("docs/spec.md", "w") as f:
    f.write(spec.content)
with open("docs/plan.md", "w") as f:
    f.write(plan.content)
```

### Scenario 2: Iterative Refinement

```python
# Start with high-level intent
initial_intent = "Build an e-commerce platform"

results = engine.execute(initial_intent, end_stage="spec")
spec = results["artifacts"]["spec"]

# User reviews spec and provides clarifications
refined_intent = """
Build an e-commerce platform with:
- Product catalog with search and filtering
- Shopping cart and checkout
- Stripe payment integration
- Order tracking
- Admin dashboard
"""

# Re-run with refined input
results = engine.execute(refined_intent, end_stage="plan")
plan = results["artifacts"]["plan"]
```

### Scenario 3: Custom Skill Integration

```python
from src.intelligence.sdd.skills import IntentParsingSkill
from src.intelligence import SkillRegistry

# Create custom skill
class DomainSpecificParsingSkill(IntentParsingSkill):
    def execute(self, context, input_data):
        # Add domain-specific logic
        result = super().execute(context, input_data)
        # Enhance with custom metadata
        result.metadata["domain"] = "healthcare"
        return result

# Register custom skill
registry = SkillRegistry()
registry.register(DomainSpecificParsingSkill())

# Use in SDD pipeline
engine = get_sdd_engine()
# Engine will use custom skill
```

## Common Patterns

### Pattern 1: Checkpoint and Resume

```python
# Save context at each stage
context = SDDContext("project")

# Stage 1
context = engine.workflow.execute_stage(context, "intent", user_input="...")
context.save("checkpoint-intent.json")

# Stage 2 (can be run later)
context = SDDContext.load("checkpoint-intent.json")
context = engine.workflow.execute_stage(context, "spec")
context.save("checkpoint-spec.json")
```

### Pattern 2: Error Handling

```python
from src.intelligence.sdd.sdd_errors import IntentParsingError, WorkflowError

try:
    results = engine.execute(user_intent, end_stage="guide")
except IntentParsingError as e:
    print(f"Failed to parse intent: {e}")
    # Prompt user for clarification
except WorkflowError as e:
    print(f"Workflow error at stage {e.stage}: {e}")
    # Resume from last checkpoint
```

### Pattern 3: Batch Processing

```python
# Process multiple intents
intents = [
    "Create user authentication",
    "Add payment processing",
    "Build analytics dashboard"
]

engine = get_sdd_engine()

for user_intent in intents:
    results = engine.execute(user_intent, end_stage="spec")
    spec = results["artifacts"]["spec"]

    # Save spec
    filename = f"specs/{spec.title.lower().replace(' ', '-')}.md"
    with open(filename, "w") as f:
        f.write(spec.content)
```

## Testing

The SDD system includes comprehensive test suites:

```bash
# Run all SDD tests
pytest tests/unit/intelligence/ tests/integration/test_sdd_workflow.py

# Run specific agent tests
pytest tests/unit/intelligence/test_intent_agent.py
pytest tests/unit/intelligence/test_spec_agent.py
pytest tests/unit/intelligence/test_plan_agent.py
pytest tests/unit/intelligence/test_guide_agent.py

# Run with coverage
pytest tests/unit/intelligence/ --cov=src/intelligence/sdd
```

## Next Steps

1. **Explore Examples**: See `src/intelligence/sdd/examples/` for more usage patterns
2. **Read Architecture**: Review `specs/005-intelligence-system-impl/plan.md` for system design
3. **Extend Skills**: Create custom skills in `src/intelligence/sdd/skills/`
4. **Customize Agents**: Extend agent behavior by subclassing base agents

## Troubleshooting

### Issue: Intent parsing returns low confidence

**Solution**: Provide more specific details in the intent. Include:
- Specific technologies or frameworks
- Functional requirements
- Non-functional requirements (performance, security)

### Issue: Generated spec is too generic

**Solution**: Use the iterative refinement pattern. Review the initial spec and provide clarifications.

### Issue: Plan tasks are not detailed enough

**Solution**: Enhance the specification with more technical details before generating the plan.

## API Reference

### Core Classes

- `SDDContext`: Execution context with SDD-specific fields
- `SDDEngine`: Main orchestration engine
- `Intent`, `Spec`, `Plan`, `Guide`: Data models for artifacts

### Agents

- `IntentAgent`: Parse natural language to Intent
- `SpecAgent`: Generate specification from Intent
- `PlanAgent`: Create implementation plan from Spec
- `GuideAgent`: Generate development guide from Plan

### Skills

- `IntentParsingSkill`: Intent type classification
- `AmbiguityDetectionSkill`: Identify unclear requirements
- `RequirementExtractionSkill`: Extract requirements from text
- `TaskBreakdownSkill`: Decompose work into tasks
- `DependencyResolutionSkill`: Identify task dependencies
- `CodeScaffoldingSkill`: Generate project structure
- `BestPracticesSkill`: Suggest patterns and conventions

## Support

For issues or questions:
- Check the test files for usage examples
- Review the architecture documentation in `specs/005-intelligence-system-impl/`
- File issues in the project repository

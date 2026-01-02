# Reusable Templates Specification

**Feature Branch**: `feat/reusable-templates`
**Created**: 2025-12-28
**Status**: Draft
**Input**: User description: "Define reusable templates for reasoning and execution..."

## User Scenarios & Testing

### User Story 1 - Specification Template (Priority: P1)

As a developer, I want a standardized template for creating specifications so that all specifications follow a consistent structure and include all required elements.

**Why this priority**: The Specification Template is the foundation for all reasoning artifacts. Without it, specifications vary in quality and completeness.

**Independent Test**: Can be tested by filling the template and verifying output structure matches schema.

**Acceptance Scenarios**:

1. **Given** a user requirement, **When** Specification Template is filled, **Then** output includes all required fields (title, description, inputs, outputs, constraints)
2. **Given** incomplete input, **When** template is validated, **Then** missing required fields are identified
3. **Given** filled template, **When** validated against schema, **Then** all fields conform to expected types

---

### User Story 2 - Task Breakdown Template (Priority: P1)

As a developer, I want a template for breaking down work into discrete tasks so that I can create actionable, ordered work items with clear dependencies.

**Why this priority**: Task Breakdown is essential for planning and execution. Inconsistent breakdowns lead to missed dependencies and ordering errors.

**Independent Test**: Can be tested by providing a specification and verifying task output with dependencies.

**Acceptance Scenarios**:

1. **Given** a specification with requirements, **When** Task Breakdown Template is filled, **Then** output includes atomic, ordered tasks
2. **Given** task list, **When** validated, **Then** each task has unique ID, description, and dependencies
3. **Given** circular dependencies, **When** detected, **Then** error is raised with cycle details

---

### User Story 3 - Validation Checklist Template (Priority: P1)

As a developer, I want a template for creating validation checklists so that I can systematically verify completeness and correctness of artifacts.

**Why this priority**: Validation Checklists ensure nothing is missed during review and provide traceable verification records.

**Independent Test**: Can be tested by creating a checklist and verifying it covers all required validation points.

**Acceptance Scenarios**:

1. **Given** an artifact type, **When** Validation Checklist Template is filled, **Then** checklist includes all required validation criteria
2. **Given** checklist with criteria, **When** executed, **Then** each criterion produces pass/fail with evidence
3. **Given** completed checklist, **When** reviewed, **Then** overall validity status is determined

---

### User Story 4 - Execution Plan Template (Priority: P1)

As a developer, I want a template for creating execution plans so that I can translate tasks into actionable steps with resources, timing, and success criteria.

**Why this priority**: Execution Plans bridge the gap between task breakdown and actual execution, providing runnable instructions.

**Independent Test**: Can be tested by providing tasks and verifying executable plan output.

**Acceptance Scenarios**:

1. **Given** tasks with dependencies, **When** Execution Plan Template is filled, **Then** plan includes execution order, resource assignments, and timing
2. **Given** execution plan, **When** validated, **Then** each step has success criteria and rollback instructions
3. **Given** plan execution, **When** progress tracked, **Then** status reflects completion against plan

---

### User Story 5 - Error Handling Template (Priority: P2)

As a developer, I want a template for defining error handling patterns so that I can create consistent, comprehensive error responses across the system.

**Why this priority**: Consistent error handling improves reliability and user experience. Without templates, error handling becomes ad-hoc and incomplete.

**Independent Test**: Can be tested by providing error scenarios and verifying error template output.

**Acceptance Scenarios**:

1. **Given** error type, **When** Error Handling Template is filled, **Then** template defines error code, message, recovery action, and logging
2. **Given** error template, **When** error occurs, **Then** response matches template specification
3. **Given** recovery action defined, **When** executed, **Then** system returns to valid state

---

### User Story 6 - Reflection Template (Priority: P2)

As a developer, I want a template for capturing reflections and lessons learned so that I can systematically improve processes and avoid repeating mistakes.

**Why this priority**: Reflection enables continuous improvement. Without structured reflection, insights are lost.

**Independent Test**: Can be tested by providing execution results and verifying reflection output.

**Acceptance Scenarios**:

1. **Given** execution results, **When** Reflection Template is filled, **Then** output captures what worked, what didn't, and improvements
2. **Given** reflection, **When** reviewed, **Then** actionable items are identified with priorities
3. **Given** multiple reflections, **When** analyzed, **Then** patterns across reflections are identified

---

### Edge Cases

- What happens when required inputs are missing from a template?
- How are conflicting validation criteria handled?
- How do templates handle domain-specific extensions?
- What happens when template output fails validation?

## Requirements

### Functional Requirements

- **FR-TPL-001**: System MUST provide Specification Template for creating structured specifications
- **FR-TPL-002**: System MUST provide Task Breakdown Template for decomposing work into tasks
- **FR-TPL-003**: System MUST provide Validation Checklist Template for systematic verification
- **FR-TPL-004**: System MUST provide Execution Plan Template for actionable runnable plans
- **FR-TPL-005**: System MUST provide Error Handling Template for consistent error responses
- **FR-TPL-006**: System MUST provide Reflection Template for capturing lessons learned
- **FR-TPL-007**: Each template MUST define required inputs, expected outputs, and validation criteria
- **FR-TPL-008**: Each template MUST support parameterization via placeholder tokens
- **FR-TPL-009**: Each template MUST include schema validation for filled values
- **FR-TPL-010**: Each template MUST be usable without domain-specific modifications

### Non-Functional Requirements

- **NFR-TPL-001**: Template validation MUST complete within 50ms
- **NFR-TPL-002**: Templates MUST support nested templates (templates containing other templates)
- **NFR-TPL-003**: Template schemas MUST be self-describing (documented in the template itself)

### Key Entities

- **Template**: Parameterized document structure with placeholders
- **Placeholder**: Named token to be replaced with concrete values
- **Schema**: Validation rules for template content
- **FilledTemplate**: Template with all placeholders replaced
- **ValidationResult**: Outcome of template validation

## Success Criteria

- **SC-TPL-001**: All 6 templates can be instantiated with valid inputs
- **SC-TPL-002**: Each template produces output conforming to its schema
- **SC-TPL-003**: Invalid inputs are rejected with descriptive error messages
- **SC-TPL-004**: Templates can be extended for domain-specific needs
- **SC-TPL-005**: Template output can be validated against the template schema

---

## Template Specifications

### 1. Specification Template

**Purpose**: Create structured, complete specifications for features, requirements, or changes.

**Template Structure**:

```markdown
# [FEATURE_NAME]

**Type**: [feature|bugfix|improvement]
**Priority**: [P0|P1|P2|P3]
**Status**: [draft|review|approved|implemented]

## Description

[Brief description of what this specification covers]

## Background

[Context and motivation - why this is needed]

## Requirements

### Functional Requirements

- **FR-[NUM]**: [Requirement statement MUST...]
- **FR-[NUM]**: [Requirement statement MUST...]

### Non-Functional Requirements

- **NFR-[NUM]**: [Performance, security, or quality requirement]

## User Scenarios

### Scenario 1 - [Title]

**Given** [initial state], **When** [action], **Then** [expected outcome]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Dependencies

- [List of dependencies on other specifications or systems]

## References

- [Link to related specs, documents, or tickets]
```

**Required Inputs**:

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| feature_name | string | Yes | Name of the feature/specification |
| feature_type | enum | Yes | feature, bugfix, improvement |
| priority | enum | Yes | P0, P1, P2, P3 |
| description | string | Yes | Brief description |
| background | string | No | Context and motivation |
| functional_requirements | list | Yes | List of FR objects |
| non_functional_requirements | list | No | List of NFR objects |
| user_scenarios | list | Yes | List of scenario objects |
| acceptance_criteria | list | Yes | List of criteria strings |
| dependencies | list | No | List of dependency strings |
| references | list | No | List of reference URLs |

**Expected Output**: Filled markdown document conforming to structure above

**Validation Criteria**:

```python
specification_template_schema = {
    "type": "object",
    "properties": {
        "feature_name": {"type": "string", "minLength": 1},
        "feature_type": {"type": "string", "enum": ["feature", "bugfix", "improvement"]},
        "priority": {"type": "string", "enum": ["P0", "P1", "P2", "P3"]},
        "description": {"type": "string", "minLength": 1},
        "functional_requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "pattern": "^FR-\\d{3}$"},
                    "statement": {"type": "string", "pattern": r"^.*MUST.*$"}
                },
                "required": ["id", "statement"]
            }
        },
        "user_scenarios": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "object"}
        },
        "acceptance_criteria": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string"}
        }
    },
    "required": ["feature_name", "feature_type", "priority", "description", "functional_requirements", "user_scenarios", "acceptance_criteria"]
}
```

---

### 2. Task Breakdown Template

**Purpose**: Decompose specifications into atomic, ordered, actionable tasks.

**Template Structure**:

```markdown
# Task Breakdown: [SPECIFICATION_NAME]

**Created**: [DATE]
**Total Tasks**: [NUM]
**Estimated Effort**: [TIME]

## Task List

### Task [ID]: [TASK_NAME]

**Status**: [pending|in-progress|completed|blocked]
**Priority**: [P0|P1|P2|P3]
**Description**: [Task description]

**Dependencies**: [List of task IDs]
**Estimated Effort**: [TIME]
**Assignee**: [NAME]

**Steps**:
1. [Step description]
2. [Step description]

**Validation**:
- [ ] Step 1 complete
- [ ] Step 2 complete

---
```

**Required Inputs**:

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| specification_name | string | Yes | Name of parent specification |
| specification_id | string | Yes | ID of parent specification |
| tasks | list | Yes | List of task objects |
| default_priority | enum | Yes | Default priority if not specified |

**Expected Output**: Markdown document with ordered task list

**Validation Criteria**:

```python
task_breakdown_schema = {
    "type": "object",
    "properties": {
        "specification_name": {"type": "string", "minLength": 1},
        "specification_id": {"type": "string"},
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string", "minLength": 1},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["P0", "P1", "P2", "P3"]},
                    "dependencies": {"type": "array", "items": {"type": "string"}},
                    "steps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    },
                    "validation_criteria": {"type": "array"}
                },
                "required": ["id", "name", "description", "steps"]
            },
            "minItems": 1
        }
    },
    "required": ["specification_name", "tasks"]
}
```

**Additional Validation Rules**:
- No circular dependencies (checked via graph traversal)
- All dependency references must point to valid task IDs
- Task IDs must be unique

---

### 3. Validation Checklist Template

**Purpose**: Create systematic verification checklists for artifacts or processes.

**Template Structure**:

```markdown
# Validation Checklist: [ARTIFACT_NAME]

**Artifact Type**: [TYPE]
**Created**: [DATE]
**Validator**: [NAME]

## Checklist

### [CATEGORY_NAME]

| # | Criterion | Expected | Actual | Pass/Fail | Evidence |
|---|-----------|----------|--------|-----------|----------|
| 1 | [Criterion] | [Expected] | [Actual] | [PASS/FAIL] | [Link] |

## Overall Result

- **Total Criteria**: [NUM]
- **Passed**: [NUM]
- **Failed**: [NUM]
- **Result**: [PASS/FAIL]

## Notes

[Additional observations]
```

**Required Inputs**:

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| artifact_name | string | Yes | Name of artifact being validated |
| artifact_type | string | Yes | Type of artifact |
| validator | string | Yes | Name of person/system validating |
| categories | list | Yes | List of category objects with criteria |

**Expected Output**: Markdown checklist with pass/fail status

**Validation Criteria**:

```python
validation_checklist_schema = {
    "type": "object",
    "properties": {
        "artifact_name": {"type": "string", "minLength": 1},
        "artifact_type": {"type": "string"},
        "validator": {"type": "string"},
        "categories": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "criteria": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "description": {"type": "string"},
                                "expected": {"type": "string"},
                                "actual": {"type": "string"},
                                "result": {"type": "string", "enum": ["PASS", "FAIL"]},
                                "evidence": {"type": "string"}
                            },
                            "required": ["description", "result"]
                        }
                    }
                },
                "required": ["name", "criteria"]
            },
            "minItems": 1
        }
    },
    "required": ["artifact_name", "artifact_type", "categories"]
}
```

---

### 4. Execution Plan Template

**Purpose**: Create actionable, runnable plans from tasks.

**Template Structure**:

```markdown
# Execution Plan: [PLAN_NAME]

**Created**: [DATE]
**Status**: [pending|executing|completed|failed]
**Total Steps**: [NUM]

## Execution Order

### Phase [NUM]: [PHASE_NAME]

#### Step [ID]: [STEP_NAME]

**Status**: [pending|running|completed|failed]
**Task Ref**: [TASK_ID]
**Command**: [Command or action to execute]

**Expected Duration**: [TIME]
**Started**: [TIMESTAMP]
**Completed**: [TIMESTAMP]

**Success Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2

**Rollback**:
- [Rollback instructions if step fails]

---

## Execution Log

| Step | Status | Duration | Started | Completed |
|------|--------|----------|---------|-----------|
| [ID] | [STATUS] | [TIME] | [TS] | [TS] |

## Summary

- **Total Steps**: [NUM]
- **Completed**: [NUM]
- **Failed**: [NUM]
- **Total Duration**: [TIME]
```

**Required Inputs**:

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| plan_name | string | Yes | Name of the execution plan |
| phases | list | Yes | List of execution phases |
| global_rollback | string | No | Global rollback instructions |
| success_criteria | list | Yes | Overall success criteria |

**Expected Output**: Markdown execution plan with status tracking

**Validation Criteria**:

```python
execution_plan_schema = {
    "type": "object",
    "properties": {
        "plan_name": {"type": "string", "minLength": 1},
        "phases": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "command": {"type": "string"},
                                "success_criteria": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "rollback": {"type": "string"},
                                "estimated_duration": {"type": "string"}
                            },
                            "required": ["id", "name", "command", "success_criteria"]
                        }
                    }
                },
                "required": ["name", "steps"]
            }
        },
        "success_criteria": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        }
    },
    "required": ["plan_name", "phases", "success_criteria"]
}
```

---

### 5. Error Handling Template

**Purpose**: Define consistent error responses and recovery procedures.

**Template Structure**:

```markdown
# Error Handling Template: [COMPONENT_NAME]

**Created**: [DATE]
**Version**: [VERSION]

## Error Codes

| Code | Type | Message | Severity | Recovery Action |
|------|------|---------|----------|-----------------|
| [PREFIX]-001 | [type] | [Message] | [HIGH/MEDIUM/LOW] | [Action] |

## Error Handlers

### Handler: [HANDLER_NAME]

**Triggers**: [List of error codes or conditions]
**Severity**: [HIGH/MEDIUM/LOW]

**Response**:
```
[Response format]
```

**Recovery**:
1. [Step]
2. [Step]

**Logging**:
- Level: [DEBUG|INFO|WARNING|ERROR]
- Details: [What to log]

**Escalation**:
- [When to escalate]
- [Contact/procedure]
```

**Required Inputs**:

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| component_name | string | Yes | Name of component |
| error_codes | list | Yes | List of error code definitions |
| error_handlers | list | Yes | List of error handler definitions |

**Expected Output**: Markdown error handling documentation

**Validation Criteria**:

```python
error_handling_schema = {
    "type": "object",
    "properties": {
        "component_name": {"type": "string", "minLength": 1},
        "error_codes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "pattern": "^[A-Z]+-\\d{3}$"},
                    "type": {"type": "string"},
                    "message": {"type": "string"},
                    "severity": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                    "recovery_action": {"type": "string"}
                },
                "required": ["code", "message", "severity", "recovery_action"]
            }
        },
        "error_handlers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "triggers": {"type": "array", "items": {"type": "string"}},
                    "response": {"type": "string"},
                    "recovery": {"type": "array", "items": {"type": "string"}},
                    "logging": {
                        "type": "object",
                        "properties": {
                            "level": {"type": "string"},
                            "details": {"type": "string"}
                        }
                    }
                },
                "required": ["name", "triggers", "response", "recovery"]
            }
        }
    },
    "required": ["component_name", "error_codes", "error_handlers"]
}
```

---

### 6. Reflection Template

**Purpose**: Capture lessons learned, patterns, and improvement suggestions.

**Template Structure**:

```markdown
# Reflection: [TOPIC]

**Date**: [DATE]
**Context**: [Brief description of what was done]
**Outcome**: [SUCCESS|FAILURE|PARTIAL]

## What Worked

- [Observation 1]
- [Observation 2]

## What Didn't Work

- [Observation 1]
- [Observation 2]

## Surprises

- [Unexpected outcome 1]
- [Unexpected outcome 2]

## Patterns Identified

- [Pattern 1]
- [Pattern 2]

## Action Items

| Priority | Action | Owner | Due Date |
|----------|--------|-------|----------|
| [HIGH] | [Action] | [Owner] | [DATE] |

## Knowledge Capture

[Key insights to preserve]

## Related Reflections

- [Link to related reflections]
```

**Required Inputs**:

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| topic | string | Yes | Topic of reflection |
| context | string | Yes | Brief description of context |
| outcome | enum | Yes | SUCCESS, FAILURE, PARTIAL |
| what_worked | list | Yes | List of observations |
| what_didnt_work | list | Yes | List of observations |
| surprises | list | No | List of unexpected outcomes |
| patterns | list | No | Identified patterns |
| action_items | list | No | List of improvement actions |
| knowledge_capture | string | No | Key insights to preserve |

**Expected Output**: Markdown reflection document

**Validation Criteria**:

```python
reflection_schema = {
    "type": "object",
    "properties": {
        "topic": {"type": "string", "minLength": 1},
        "context": {"type": "string", "minLength": 1},
        "outcome": {"type": "string", "enum": ["SUCCESS", "FAILURE", "PARTIAL"]},
        "what_worked": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "what_didnt_work": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "surprises": {"type": "array", "items": {"type": "string"}},
        "patterns": {"type": "array", "items": {"type": "string"}},
        "action_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "priority": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                    "action": {"type": "string"},
                    "owner": {"type": "string"},
                    "due_date": {"type": "string", "format": "date"}
                },
                "required": ["action", "priority"]
            }
        },
        "knowledge_capture": {"type": "string"}
    },
    "required": ["topic", "context", "outcome", "what_worked", "what_didnt_work"]
}
```

---

## Template Metadata Schema

All templates include metadata for discovery and management:

```python
template_metadata_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
        "purpose": {"type": "string"},
        "author": {"type": "string"},
        "created": {"type": "string", "format": "date"},
        "updated": {"type": "string", "format": "date"},
        "inputs": {"type": "object"},
        "outputs": {"type": "object"},
        "validation_schema": {"type": "object"},
        "examples": {
            "type": "array",
            "items": {"type": "string"}
        },
        "extensions": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["name", "version", "purpose", "inputs", "outputs", "validation_schema"]
}
```

## Template Composition

Templates can be nested for complex documents:

```python
class TemplateComposer:
    """Composes multiple templates into composite documents."""

    def compose(self, base_template: str, nested_templates: dict) -> str:
        """Replace nested template placeholders with filled templates."""
        ...

    def validate_composition(self, composed: str) -> ValidationResult:
        """Validate that composed template meets all schema requirements."""
        ...
```

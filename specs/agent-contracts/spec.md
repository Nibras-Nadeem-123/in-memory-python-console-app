# Sub-Agent Formal Contracts Specification

**Feature Branch**: `feat/agent-contracts`
**Created**: 2025-12-28
**Status**: Draft
**Input**: User description: "Define formal contracts for sub-agents..."

## User Scenarios & Testing

### User Story 1 - Agent Contract Validation (Priority: P1)

As a developer, I want each agent to have a formal, machine-readable contract so that I can validate inputs/outputs and ensure compatibility.

**Why this priority**: Contracts enable automated validation, documentation generation, and integration testing.

**Independent Test**: Can be tested by validating agent inputs/outputs against declared schemas.

**Acceptance Scenarios**:

1. **Given** agent contract with input schema, **When** invalid input provided, **Then** validation fails with descriptive error
2. **Given** agent contract with output schema, **When** output generated, **Then** output conforms to declared schema
3. **Given** agent contract, **When** compared to other agents, **Then** no schema conflicts detected

---

### User Story 2 - Inter-Agent Data Passing (Priority: P1)

As a developer, I want a clear protocol for how agents pass data to each other so that I can compose agents into workflows.

**Why this priority**: Data passing is the glue that enables agent collaboration. Without clear protocols, data loss and type errors occur.

**Independent Test**: Can be tested by passing data between agents and verifying correct transformation.

**Acceptance Scenarios**:

1. **Given** ArchitectAgent output, **When** passed to PlannerAgent, **Then** PlannerAgent receives valid input
2. **Given** multiple agents in workflow, **When** data passed, **Then** all transformations are type-safe
3. **Given** data schema mismatch, **When** passed between agents, **Then** error is raised with location

---

### User Story 3 - Failure Mode Documentation (Priority: P1)

As a developer, I want each agent to declare its failure modes so that I can handle errors appropriately in workflows.

**Why this priority**: Proper error handling requires knowing what can fail and how.

**Independent Test**: Can be tested by triggering failure conditions and verifying error handling.

**Acceptance Scenarios**:

1. **Given** declared failure mode, **When** failure occurs, **Then** error matches declared pattern
2. **Given** unhandled failure, **When** occurs, **Then** error propagates with full context
3. **Given** retryable failure, **When** handled, **Then** retry succeeds within declared limits

---

### User Story 4 - Allowed Actions Enforcement (Priority: P2)

As a developer, I want each agent to declare its allowed actions so that I can enforce security and operational constraints.

**Why this priority**: Security and reliability require limiting what agents can do.

**Independent Test**: Can be tested by requesting disallowed actions and verifying rejection.

**Acceptance Scenarios**:

1. **Given** agent with declared allowed actions, **When** disallowed action requested, **Then** request is rejected
2. **Given** allowed action, **When** executed, **Then** action completes successfully
3. **Given** action requiring approval, **When** requested without approval, **Then** request is queued

---

## Requirements

### Functional Requirements

- **FR-CON-001**: Each agent MUST declare a formal contract with purpose, input/output schemas
- **FR-CON-002**: Each agent MUST declare allowed actions with permission levels
- **FR-CON-003**: Each agent MUST declare failure modes with recovery strategies
- **FR-CON-004**: Agents MUST pass data via structured contracts (not ad-hoc messages)
- **FR-CON-005**: Contract validation MUST occur at agent invocation boundaries
- **FR-CON-006**: Contract violations MUST produce descriptive error messages
- **FR-CON-007**: Inter-agent data passing MUST be type-safe and validated

### Non-Functional Requirements

- **NFR-CON-001**: Contract validation MUST complete within 10ms
- **NFR-CON-002**: Contract schemas MUST be serializable to JSON Schema
- **NFR-CON-003**: Contract parsing MUST support dynamic loading
- **NFR-CON-004**: All contracts MUST be versioned for compatibility

### Key Entities

- **AgentContract** - Complete contract for an agent
- **InputSchema** - JSON Schema for agent inputs
- **OutputSchema** - JSON Schema for agent outputs
- **AllowedActions** - Declared actions with permissions
- **FailureMode** - Declared failure with recovery strategy
- **DataContract** - Schema for inter-agent data passing
- **ContractValidator** - Validates inputs/outputs against schemas

---

## Agent Contract Base

### Contract Structure

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import json


class AgentType(Enum):
    ARCHITECT = "architect"
    PLANNER = "planner"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"
    REFINER = "refiner"


class PermissionLevel(Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


class Severity(Enum):
    BLOCKING = "blocking"
    WARNING = "warning"
    INFO = "info"


class Recoverability(Enum):
    NONE = "none"              # Cannot recover, requires human intervention
    MANUAL = "manual"          # Requires human action to recover
    AUTOMATIC = "automatic"    # Can recover automatically
    RETRY = "retry"            # Can recover with retry


@dataclass
class Purpose:
    """Agent's stated purpose."""
    summary: str
    detailed_description: str
    scope: List[str]  # What the agent handles
    out_of_scope: List[str]  # What the agent doesn't handle


@dataclass
class Action:
    """Declared action an agent can perform."""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema
    returns: Dict[str, Any]  # JSON Schema
    permission: PermissionLevel = PermissionLevel.READ
    timeout_seconds: int = 30
    idempotent: bool = False


@dataclass
class FailureMode:
    """Declared failure mode."""
    mode_id: str
    description: str
    trigger_conditions: List[str]
    severity: Severity
    recoverability: Recoverability
    recovery_action: str
    retry_strategy: Optional[Dict[str, Any]] = None
    escalation_path: Optional[str] = None


@dataclass
class ContractVersion:
    """Version information for a contract."""
    major: int
    minor: int
    patch: int
    released_at: datetime
    changelog: str = ""
    backwards_compatible: bool = True


@dataclass
class AgentContract:
    """Complete agent contract."""
    agent_name: str
    agent_type: AgentType
    version: ContractVersion
    purpose: Purpose
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    allowed_actions: List[Action] = field(default_factory=list)
    failure_modes: List[FailureMode] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    data_contracts: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_schema_version(self) -> str:
        """Get semver string."""
        return f"{self.version.major}.{self.version.minor}.{self.version.patch}"

    def validate_input(self, input: Any) -> tuple[bool, str]:
        """Validate input against schema."""
        ...

    def validate_output(self, output: Any) -> tuple[bool, str]:
        """Validate output against schema."""
        ...
```

---

## 1. ArchitectAgent Contract

**Purpose**: Designs system structure and abstractions.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "requirements": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "constraints": {"type": "array", "items": {"type": "string"}},
    "non_functional_requirements": {
      "type": "object",
      "properties": {
        "performance": {"type": "string"},
        "security": {"type": "string"},
        "scalability": {"type": "string"},
        "reliability": {"type": "string"}
      }
    },
    "context": {
      "type": "object",
      "properties": {
        "project_name": {"type": "string"},
        "project_root": {"type": "string"}
      }
    }
  },
  "required": ["requirements", "constraints", "context"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "components": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "responsibility": {"type": "string"},
          "interfaces": {"type": "array"},
          "dependencies": {"type": "array"},
          "technology": {"type": "string"}
        }
      }
    },
    "interfaces": {"type": "array"},
    "data_flows": {"type": "array"},
    "trade_offs": {"type": "array"}
  },
  "required": ["components", "interfaces", "data_flows", "trade_offs"]
}
```

**Allowed Actions**:
| Action | Description | Permission |
|--------|-------------|------------|
| `design_component` | Design a new component | WRITE |
| `define_interface` | Define interface between components | WRITE |
| `analyze_tradeoff` | Analyze architectural trade-off | READ |

**Failure Modes**:
| ID | Description | Severity | Recoverability |
|----|-------------|----------|----------------|
| ARCH-001 | Insufficient requirements | BLOCKING | MANUAL |
| ARCH-002 | Conflicting constraints | BLOCKING | MANUAL |
| ARCH-003 | Technology unavailable | WARNING | AUTOMATIC |
| ARCH-004 | Complexity exceeds limit | WARNING | MANUAL |

---

## 2. PlannerAgent Contract

**Purpose**: Converts specifications into actionable steps.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "specification": {
      "type": "object",
      "properties": {
        "feature_name": {"type": "string"},
        "requirements": {"type": "array"},
        "acceptance_criteria": {"type": "array"}
      }
    },
    "architecture": {"type": "object"},
    "context": {"type": "object"}
  },
  "required": ["specification", "context"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "task_id": {"type": "string"},
          "name": {"type": "string"},
          "description": {"type": "string"},
          "category": {"type": "string"},
          "priority": {"type": "string"},
          "dependencies": {"type": "array"},
          "steps": {"type": "array"}
        }
      }
    },
    "execution_order": {"type": "object"},
    "total_tasks": {"type": "integer"},
    "critical_path": {"type": "array"}
  },
  "required": ["tasks", "execution_order", "total_tasks"]
}
```

**Allowed Actions**:
| Action | Description | Permission |
|--------|-------------|------------|
| `decompose_task` | Break down task into steps | READ |
| `analyze_dependencies` | Analyze task dependencies | READ |
| `estimate_effort` | Estimate task effort | READ |

**Failure Modes**:
| ID | Description | Severity | Recoverability |
|----|-------------|----------|----------------|
| PLAN-001 | Specification too vague | BLOCKING | MANUAL |
| PLAN-002 | Circular dependencies | BLOCKING | AUTOMATIC |
| PLAN-003 | Task count exceeds limit | WARNING | MANUAL |
| PLAN-004 | Missing architecture | WARNING | AUTOMATIC |

---

## 3. ExecutorAgent Contract

**Purpose**: Performs implementation actions.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task": {
      "type": "object",
      "properties": {
        "task_id": {"type": "string"},
        "name": {"type": "string"},
        "steps": {"type": "array"}
      }
    },
    "context": {
      "type": "object",
      "properties": {
        "project_root": {"type": "string"},
        "dry_run": {"type": "boolean"}
      }
    }
  },
  "required": ["task", "context"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {"type": "string"},
    "overall_status": {"type": "string"},
    "step_results": {"type": "array"},
    "artifacts_created": {"type": "object"},
    "total_duration_ms": {"type": "integer"}
  },
  "required": ["task_id", "overall_status", "step_results"]
}
```

**Allowed Actions**:
| Action | Description | Permission |
|--------|-------------|------------|
| `execute_step` | Execute a single step | EXECUTE |
| `rollback_step` | Rollback a step | EXECUTE |
| `checkpoint` | Create execution checkpoint | WRITE |

**Failure Modes**:
| ID | Description | Severity | Recoverability |
|----|-------------|----------|----------------|
| EXEC-001 | Step execution failed | WARNING | RETRY |
| EXEC-002 | Rollback failed | BLOCKING | MANUAL |
| EXEC-003 | Artifact creation failed | BLOCKING | MANUAL |
| EXEC-004 | Context validation failed | BLOCKING | AUTOMATIC |

---

## 4. ReviewerAgent Contract

**Purpose**: Audits quality, correctness, and alignment.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "artifacts": {"type": "array", "items": {"type": "string"}},
    "specification": {"type": "object"},
    "review_depth": {"type": "string", "enum": ["shallow", "standard", "deep"]},
    "context": {"type": "object"}
  },
  "required": ["artifacts", "specification", "context"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "overall_score": {"type": "number"},
    "quality_scores": {"type": "array"},
    "findings": {"type": "array"},
    "summary": {"type": "string"},
    "recommendation": {"type": "string"}
  },
  "required": ["overall_score", "quality_scores", "findings", "summary", "recommendation"]
}
```

**Allowed Actions**:
| Action | Description | Permission |
|--------|-------------|------------|
| `check_quality` | Check code quality metrics | READ |
| `check_alignment` | Check spec alignment | READ |
| `generate_report` | Generate review report | READ |

**Failure Modes**:
| ID | Description | Severity | Recoverability |
|----|-------------|----------|----------------|
| REV-001 | Artifact not found | BLOCKING | MANUAL |
| REV-002 | Review timeout | WARNING | AUTOMATIC |
| REV-003 | Spec missing required fields | WARNING | AUTOMATIC |
| REV-004 | Invalid quality criteria | INFO | AUTOMATIC |

---

## 5. RefinerAgent Contract

**Purpose**: Improves clarity, efficiency, and robustness.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "artifacts": {"type": "array"},
    "review_findings": {"type": "array"},
    "improvement_goals": {"type": "array"},
    "context": {"type": "object"}
  },
  "required": ["artifacts", "context"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "suggestions": {"type": "array"},
    "prioritized_suggestions": {"type": "array"},
    "quick_wins": {"type": "array"},
    "refactoring_roadmap": {"type": "array"}
  },
  "required": ["suggestions", "prioritized_suggestions", "quick_wins"]
}
```

**Allowed Actions**:
| Action | Description | Permission |
|--------|-------------|------------|
| `analyze_code` | Analyze code for improvements | READ |
| `prioritize_suggestions` | Prioritize suggestions | READ |
| `generate_roadmap` | Generate refactoring roadmap | READ |

**Failure Modes**:
| ID | Description | Severity | Recoverability |
|----|-------------|----------|----------------|
| REF-001 | No artifacts provided | INFO | NONE |
| REF-002 | Analysis timeout | WARNING | AUTOMATIC |
| REF-003 | Review findings missing | INFO | AUTOMATIC |
| REF-004 | Constraints prevent suggestions | INFO | AUTOMATIC |

---

## Inter-Agent Data Passing Protocol

### Data Contracts

| Source → Target | Schema | Transformation |
|-----------------|--------|----------------|
| Architect → Planner | components, interfaces, data_flows | rename fields |
| Planner → Executor | tasks, execution_order | extract fields |
| Executor → Reviewer | task_id, artifacts, results | wrap in object |
| Reviewer → Refiner | findings, scores | direct pass-through |
| Refiner → Executor | implementation_steps | extract fields |

### Transformation Types

- `extract_fields`: Select specific fields
- `rename_fields`: Rename field keys
- `wrap_in_object`: Wrap data in container
- `filter_fields`: Filter by conditions

---

## Contract Validator

```python
class ContractValidator:
    def validate_contract(self, contract: AgentContract) -> tuple[bool, List[str]]:
        """Validate contract structure."""

    def validate_input(self, contract: AgentContract, input: Any) -> tuple[bool, str]:
        """Validate input against contract."""

    def validate_output(self, contract: AgentContract, output: Any) -> tuple[bool, str]:
        """Validate output against contract."""

    def validate_data_handoff(self, source: str, target: str, data: Any) -> tuple[bool, str]:
        """Validate data passing between agents."""
```

---

## Agent Contract Registry

```python
class AgentContractRegistry:
    def register(self, contract: AgentContract) -> tuple[bool, str]:
        """Register agent contract."""

    def get(self, agent_name: str) -> Optional[AgentContract]:
        """Get contract by name."""

    def validate_handoff(self, source: str, target: str, data: Any) -> tuple[bool, str]:
        """Validate data handoff between agents."""
```

---

## Summary

| Agent | Purpose | Key Inputs | Key Outputs |
|-------|---------|------------|-------------|
| **ArchitectAgent** | Design structure | Requirements, constraints | Components, interfaces, flows |
| **PlannerAgent** | Create tasks | Spec, architecture | Tasks, order, critical path |
| **ExecutorAgent** | Execute tasks | Task with steps | Results, artifacts |
| **ReviewerAgent** | Audit quality | Artifacts, spec | Findings, scores |
| **RefinerAgent** | Suggest improvements | Artifacts, findings | Suggestions, roadmap |

**PHR**: `history/prompts/agent-contracts/001-define-agent-contracts.spec.prompt.md`

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
    data_contracts: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # target_agent -> schema
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

```python
ARCHITECT_CONTRACT = AgentContract(
    agent_name="ArchitectAgent",
    agent_type=AgentType.ARCHITECT,
    version=ContractVersion(
        major=1, minor=0, patch=0,
        released_at=datetime(2025, 12, 28),
        changelog="Initial contract",
        backwards_compatible=True
    ),
    purpose=Purpose(
        summary="Designs system structure and abstractions",
        detailed_description="""
        The Architect Agent analyzes requirements and constraints to produce
        a complete system architecture. It defines components, interfaces,
        data flows, and architectural decisions with trade-offs.
        """,
        scope=[
            "Component design",
            "Interface definition",
            "Data flow modeling",
            "Technology selection",
            "Trade-off analysis"
        ],
        out_of_scope=[
            "Implementation details",
            "Code generation",
            "Testing strategy"
        ]
    ),
    input_schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "requirements": {
                "type": "array",
                "description": "Feature or functional requirements",
                "items": {"type": "string"},
                "minItems": 1
            },
            "constraints": {
                "type": "array",
                "description": "System constraints",
                "items": {"type": "string"}
            },
            "non_functional_requirements": {
                "type": "object",
                "description": "NFRs for performance, security, etc.",
                "properties": {
                    "performance": {"type": "string"},
                    "security": {"type": "string"},
                    "scalability": {"type": "string"},
                    "reliability": {"type": "string"}
                }
            },
            "existing_architecture": {
                "type": "object",
                "description": "Existing architecture context",
                "nullable": True
            },
            "technology_preferences": {
                "type": "array",
                "description": "Preferred technologies",
                "items": {"type": "string"}
            },
            "context": {
                "type": "object",
                "description": "Engine context",
                "properties": {
                    "project_name": {"type": "string"},
                    "project_root": {"type": "string"}
                }
            }
        },
        "required": ["requirements", "constraints", "context"]
    },
    output_schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "components": {
                "type": "array",
                "description": "Designed components",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "responsibility": {"type": "string"},
                        "interfaces": {"type": "array", "items": {"type": "string"}},
                        "dependencies": {"type": "array", "items": {"type": "string"}},
                        "technology": {"type": "string"}
                    },
                    "required": ["name", "responsibility", "interfaces", "dependencies"]
                }
            },
            "interfaces": {
                "type": "array",
                "description": "Component interfaces",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "input_schema": {"type": "object"},
                        "output_schema": {"type": "object"},
                        "protocol": {"type": "string"}
                    },
                    "required": ["name", "protocol"]
                }
            },
            "data_flows": {
                "type": "array",
                "description": "Data flows between components",
                "items": {
                    "type": "object",
                    "properties": {
                        "from_component": {"type": "string"},
                        "to_component": {"type": "string"},
                        "data_type": {"type": "string"},
                        "frequency": {"type": "string"}
                    },
                    "required": ["from_component", "to_component", "data_type"]
                }
            },
            "trade_offs": {
                "type": "array",
                "description": "Architectural trade-offs",
                "items": {
                    "type": "object",
                    "properties": {
                        "dimension": {"type": "string"},
                        "choice": {"type": "string"},
                        "rationale": {"type": "string"},
                        "alternative": {"type": "string"},
                        "rejection_reason": {"type": "string"}
                    },
                    "required": ["dimension", "choice", "rationale"]
                }
            },
            "architecture_diagram": {"type": "string"},
            "assumptions": {"type": "array", "items": {"type": "string"}},
            "risks": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["components", "interfaces", "data_flows", "trade_offs"]
    },
    allowed_actions=[
        Action(
            name="design_component",
            description="Design a new system component",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "requirements": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["name", "requirements"]
            },
            returns={
                "type": "object",
                "properties": {
                    "component": {"type": "object"}
                }
            },
            permission=PermissionLevel.WRITE
        ),
        Action(
            name="define_interface",
            description="Define interface between components",
            parameters={
                "type": "object",
                "properties": {
                    "component_a": {"type": "string"},
                    "component_b": {"type": "string"},
                    "data_schema": {"type": "object"}
                },
                "required": ["component_a", "component_b"]
            },
            returns={"type": "object"},
            permission=PermissionLevel.WRITE
        ),
        Action(
            name="analyze_tradeoff",
            description="Analyze architectural trade-off",
            parameters={
                "type": "object",
                "properties": {
                    "options": {"type": "array", "items": {"type": "string"}},
                    "criteria": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["options", "criteria"]
            },
            returns={
                "type": "object",
                "properties": {
                    "recommendation": {"type": "string"},
                    "reasoning": {"type": "string"}
                }
            },
            permission=PermissionLevel.READ
        )
    ],
    failure_modes=[
        FailureMode(
            mode_id="ARCH-001",
            description="Insufficient requirements",
            trigger_conditions=["requirements array is empty", "requirements contain contradictions"],
            severity=Severity.BLOCKING,
            recoverability=Recoverability.MANUAL,
            recovery_action="Request additional requirements from user",
            escalation_path="human:architect-review"
        ),
        FailureMode(
            mode_id="ARCH-002",
            description="Conflicting constraints",
            trigger_conditions=["constraints cannot be satisfied simultaneously"],
            severity=Severity.BLOCKING,
            recoverability=Recoverability.MANUAL,
            recovery_action="Identify conflicting constraints and request resolution",
            escalation_path="human:architect-review"
        ),
        FailureMode(
            mode_id="ARCH-003",
            description="Technology preference unavailable",
            trigger_conditions=["preferred technology not available in context"],
            severity=Severity.WARNING,
            recoverability=Recoverability.AUTOMATIC,
            recovery_action="Fall back to alternative technology from approved list",
            retry_strategy={"max_attempts": 1}
        ),
        FailureMode(
            mode_id="ARCH-004",
            description="Design complexity exceeds limit",
            trigger_conditions=["component count exceeds threshold", "dependency graph too complex"],
            severity=Severity.WARNING,
            recoverability=Recoverability.MANUAL,
            recovery_action="Suggest decomposition or simplification"
        )
    ],
    data_contracts={
        "PlannerAgent": {
            "type": "object",
            "description": "Architecture output passed to PlannerAgent",
            "properties": {
                "components": {"type": "array"},
                "interfaces": {"type": "array"},
                "data_flows": {"type": "array"},
                "constraints": {"type": "array"}
            },
            "required": ["components", "interfaces", "data_flows"]
        }
    }
)
```

---

## 2. PlannerAgent Contract

```python
PLANNER_CONTRACT = AgentContract(
    agent_name="PlannerAgent",
    agent_type=AgentType.PLANNER,
    version=ContractVersion(
        major=1, minor=0, patch=0,
        released_at=datetime(2025, 12, 28),
        changelog="Initial contract",
        backwards_compatible=True
    ),
    purpose=Purpose(
        summary="Converts specifications into actionable steps",
        detailed_description="""
        The Planner Agent takes validated specifications and architectural
        context, then breaks them down into atomic, ordered tasks with
        clear dependencies and estimates.
        """,
        scope=[
            "Task decomposition",
            "Dependency analysis",
            "Effort estimation",
            "Priority assignment",
            "Resource planning"
        ],
        out_of_scope=[
            "Task execution",
            "Quality review",
            "Architecture design"
        ]
    ),
    input_schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "specification": {
                "type": "object",
                "description": "Validated specification document",
                "properties": {
                    "feature_name": {"type": "string"},
                    "requirements": {"type": "array", "items": {"type": "string"}},
                    "acceptance_criteria": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["feature_name", "requirements"]
            },
            "architecture": {
                "type": "object",
                "description": "Architecture context from ArchitectAgent",
                "nullable": True
            },
            "constraints": {
                "type": "array",
                "description": "Planning constraints"
            },
            "task_templates": {
                "type": "array",
                "description": "Available task templates"
            },
            "context": {
                "type": "object",
                "description": "Engine context",
                "properties": {
                    "project_name": {"type": "string"},
                    "default_priority": {"type": "string", "enum": ["P0", "P1", "P2", "P3"]}
                }
            }
        },
        "required": ["specification", "context"]
    },
    output_schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "tasks": {
                "type": "array",
                "description": "Decomposed tasks",
                "items": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "category": {"type": "string", "enum": ["implementation", "testing", "documentation", "review"]},
                        "priority": {"type": "string"},
                        "dependencies": {"type": "array", "items": {"type": "string"}},
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step_id": {"type": "string"},
                                    "description": {"type": "string"},
                                    "command": {"type": "string"},
                                    "success_criteria": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["step_id", "description", "success_criteria"]
                            }
                        },
                        "estimated_effort": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "required": ["task_id", "name", "description", "steps"]
                }
            },
            "execution_order": {
                "type": "object",
                "properties": {
                    "task_ids": {"type": "array", "items": {"type": "string"}},
                    "justification": {"type": "string"},
                    "parallel_groups": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}
                },
                "required": ["task_ids", "justification"]
            },
            "total_tasks": {"type": "integer"},
            "critical_path": {"type": "array", "items": {"type": "string"}},
            "risk_assessment": {
                "type": "object",
                "properties": {
                    "high_risk_tasks": {"type": "array", "items": {"type": "string"}},
                    "bottlenecks": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "required": ["tasks", "execution_order", "total_tasks"]
    },
    allowed_actions=[
        Action(
            name="decompose_task",
            description="Break down a task into smaller steps",
            parameters={
                "type": "object",
                "properties": {
                    "task_description": {"type": "string"},
                    "max_depth": {"type": "integer"}
                },
                "required": ["task_description"]
            },
            returns={"type": "array"},
            permission=PermissionLevel.READ
        ),
        Action(
            name="analyze_dependencies",
            description="Analyze task dependencies",
            parameters={
                "type": "object",
                "properties": {
                    "tasks": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["tasks"]
            },
            returns={
                "type": "object",
                "properties": {
                    "dependency_graph": {"type": "object"},
                    "critical_path": {"type": "array", "items": {"type": "string"}}
                }
            },
            permission=PermissionLevel.READ
        ),
        Action(
            name="estimate_effort",
            description="Estimate effort for a task",
            parameters={
                "type": "object",
                "properties": {
                    "task": {"type": "object"},
                    "historical_data": {"type": "object", "nullable": True}
                },
                "required": ["task"]
            },
            returns={
                "type": "object",
                "properties": {
                    "effort": {"type": "string"},
                    "confidence": {"type": "number"}
                }
            },
            permission=PermissionLevel.READ
        )
    ],
    failure_modes=[
        FailureMode(
            mode_id="PLAN-001",
            description="Specification too vague",
            trigger_conditions=["requirements lack detail", "acceptance criteria undefined"],
            severity=Severity.BLOCKING,
            recoverability=Recoverability.MANUAL,
            recovery_action="Request clarification on requirements",
            escalation_path="human:requirement-review"
        ),
        FailureMode(
            mode_id="PLAN-002",
            description="Circular dependencies detected",
            trigger_conditions=["dependency graph contains cycle"],
            severity=Severity.BLOCKING,
            recoverability=Recoverability.AUTOMATIC,
            recovery_action="Break cycle by reordering or combining tasks",
            retry_strategy={"max_attempts": 2, "backoff": "exponential"}
        ),
        FailureMode(
            mode_id="PLAN-003",
            description="Task count exceeds limit",
            trigger_conditions=["total tasks > 100"],
            severity=Severity.WARNING,
            recoverability=Recoverability.MANUAL,
            recovery_action="Suggest task grouping or phase decomposition"
        ),
        FailureMode(
            mode_id="PLAN-004",
            description="Missing architecture context",
            trigger_conditions=["architecture is null"],
            severity=Severity.WARNING,
            recoverability=Recoverability.AUTOMATIC,
            recovery_action="Proceed with specification-only planning"
        )
    ],
    data_contracts={
        "ExecutorAgent": {
            "type": "object",
            "description": "Task list passed to ExecutorAgent",
            "properties": {
                "tasks": {"type": "array"},
                "execution_order": {"type": "object"},
                "context": {"type": "object"}
            },
            "required": ["tasks", "execution_order"]
        },
        "ReviewerAgent": {
            "type": "object",
            "description": "Planning output for review",
            "properties": {
                "tasks": {"type": "array"},
                "risk_assessment": {"type": "object"}
            },
            "required": ["tasks"]
        }
    }
)
```

---

## 3. ExecutorAgent Contract

```python
EXECUTOR_CONTRACT = AgentContract(
    agent_name="ExecutorAgent",
    agent_type=AgentType.EXECUTOR,
    version=ContractVersion(
        major=1, minor=0, patch=0,
        released_at=datetime(2025, 12, 28),
        changelog="Initial contract",
        backwards_compatible=True
    ),
    purpose=Purpose(
        summary="Performs implementation actions",
        detailed_description="""
        The Executor Agent takes task definitions and executes them,
        creating artifacts, modifying state, and reporting outcomes.
        It supports both synchronous and asynchronous execution.
        """,
        scope=[
            "Task execution",
            "Artifact creation",
            "State modification",
            "Progress tracking",
            "Rollback handling"
        ],
        out_of_scope=[
            "Task planning",
            "Quality review",
            "Architecture design"
        ]
    ),
    input_schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "task": {
                "type": "object",
                "description": "Task to execute",
                "properties": {
                    "task_id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "step_id": {"type": "string"},
                                "description": {"type": "string"},
                                "command": {"type": "string"},
                                "success_criteria": {"type": "array", "items": {"type": "string"}},
                                "rollback_command": {"type": "string"}
                            },
                            "required": ["step_id", "description", "command", "success_criteria"]
                        }
                    }
                },
                "required": ["task_id", "name", "steps"]
            },
            "context": {
                "type": "object",
                "description": "Execution context",
                "properties": {
                    "project_root": {"type": "string"},
                    "available_tools": {"type": "array", "items": {"type": "string"}},
                    "dry_run": {"type": "boolean"}
                },
                "required": ["project_root"]
            },
            "checkpoint_frequency": {
                "type": "integer",
                "description": "Steps between checkpoints"
            }
        },
        "required": ["task", "context"]
    },
    output_schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "task_id": {"type": "string"},
            "overall_status": {"type": "string", "enum": ["completed", "partial", "failed"]},
            "step_results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "step_id": {"type": "string"},
                        "status": {"type": "string"},
                        "output": {"type": "string"},
                        "duration_ms": {"type": "integer"},
                        "artifacts_created": {"type": "array", "items": {"type": "string"}},
                        "error": {"type": "string"}
                    },
                    "required": ["step_id", "status"]
                }
            },
            "artifacts_created": {
                "type": "object",
                "description": "artifact_name -> file_path"
            },
            "total_duration_ms": {"type": "integer"},
            "state_before": {"type": "object"},
            "state_after": {"type": "object"},
            "checkpoints": {"type": "array", "items": {"type": "object"}}
        },
        "required": ["task_id", "overall_status", "step_results"]
    },
    allowed_actions=[
        Action(
            name="execute_step",
            description="Execute a single step",
            parameters={
                "type": "object",
                "properties": {
                    "step": {"type": "object"},
                    "context": {"type": "object"}
                },
                "required": ["step", "context"]
            },
            returns={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "output": {"type": "string"},
                    "artifacts": {"type": "array", "items": {"type": "string"}}
                }
            },
            permission=PermissionLevel.EXECUTE
        ),
        Action(
            name="rollback_step",
            description="Rollback a step",
            parameters={
                "type": "object",
                "properties": {
                    "step_id": {"type": "string"},
                    "rollback_command": {"type": "string"}
                },
                "required": ["step_id", "rollback_command"]
            },
            returns={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"}
                }
            },
            permission=PermissionLevel.EXECUTE
        ),
        Action(
            name="checkpoint",
            description="Create execution checkpoint",
            parameters={
                "type": "object",
                "properties": {
                    "state": {"type": "object"}
                },
                "required": ["state"]
            },
            returns={
                "type": "object",
                "properties": {
                    "checkpoint_id": {"type": "string"}
                }
            },
            permission=PermissionLevel.WRITE
        )
    ],
    failure_modes=[
        FailureMode(
            mode_id="EXEC-001",
            description="Step execution failed",
            trigger_conditions=["command returns non-zero exit code", "command times out"],
            severity=Severity.WARNING,
            recoverability=Recoverability.RETRY,
            recovery_action="Retry step with exponential backoff",
            retry_strategy={"max_attempts": 3, "backoff": "exponential", "initial_delay": 1}
        ),
        FailureMode(
            mode_id="EXEC-002",
            description="Rollback failed",
            trigger_conditions=["rollback_command fails"],
            severity=Severity.BLOCKING,
            recoverability=Recoverability.MANUAL,
            recovery_action="Manual intervention required",
            escalation_path="human:operations"
        ),
        FailureMode(
            mode_id="EXEC-003",
            description="Artifact creation failed",
            trigger_conditions=["file write fails", "permission denied"],
            severity=Severity.BLOCKING,
            recoverability=Recoverability.MANUAL,
            recovery_action="Check permissions and disk space"
        ),
        FailureMode(
            mode_id="EXEC-004",
            description="Context validation failed",
            trigger_conditions=["project_root doesn't exist", "tool not available"],
            severity=Severity.BLOCKING,
            recoverability=Recoverability.AUTOMATIC,
            recovery_action="Provide descriptive error with required setup"
        ),
        FailureMode(
            mode_id="EXEC-005",
            description="Checkpoint restore failed",
            trigger_conditions=["checkpoint not found", "checkpoint corrupted"],
            severity=Severity.WARNING,
            recoverability=Recoverability.NONE,
            recovery_action="Continue without checkpoint"
        )
    ],
    data_contracts={
        "ReviewerAgent": {
            "type": "object",
            "description": "Execution results for review",
            "properties": {
                "task_id": {"type": "string"},
                "overall_status": {"type": "string"},
                "artifacts_created": {"type": "object"},
                "step_results": {"type": "array"}
            },
            "required": ["task_id", "overall_status", "step_results"]
        },
        "RefinerAgent": {
            "type": "object",
            "description": "Execution results for refinement",
            "properties": {
                "task_id": {"type": "string"},
                "step_results": {"type": "array"},
                "duration_ms": {"type": "integer"}
            },
            "required": ["task_id", "step_results"]
        }
    }
)
```

---

## 4. ReviewerAgent Contract

```python
REVIEWER_CONTRACT = AgentContract(
    agent_name="ReviewerAgent",
    agent_type=AgentType.REVIEWER,
    version=ContractVersion(
        major=1, minor=0, patch=0,
        released_at=datetime(2025, 12, 28),
        changelog="Initial contract",
        backwards_compatible=True
    ),
    purpose=Purpose(
        summary="Audits quality, correctness, and alignment",
        detailed_description="""
        The Reviewer Agent examines artifacts for quality standards,
        correctness, security, and alignment with specifications.
        It provides actionable findings with severity levels.
        """,
        scope=[
            "Code quality review",
            "Correctness verification",
            "Security analysis",
            "Performance assessment",
            "Specification alignment"
        ],
        out_of_scope=[
            "Task execution",
            "Architecture design",
            "Implementation"
        ]
    ),
    input_schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "artifacts": {
                "type": "array",
                "description": "Paths to artifacts to review",
                "items": {"type": "string"},
                "minItems": 1
            },
            "specification": {
                "type": "object",
                "description": "Reference specification"
            },
            "quality_criteria": {
                "type": "object",
                "description": "Custom quality criteria"
            },
            "review_depth": {
                "type": "string",
                "enum": ["shallow", "standard", "deep"],
                "default": "standard"
            },
            "context": {
                "type": "object",
                "description": "Engine context"
            }
        },
        "required": ["artifacts", "specification", "context"]
    },
    output_schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "overall_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Overall quality score"
            },
            "quality_scores": {
                "type": "array",
                "description": "Scores by category",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "score": {"type": "number", "minimum": 0, "maximum": 1},
                        "max_score": {"type": "number"},
                        "findings_count": {"type": "integer"}
                    },
                    "required": ["category", "score", "findings_count"]
                }
            },
            "findings": {
                "type": "array",
                "description": "Review findings",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "severity": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "location": {"type": "string"},
                        "suggestion": {"type": "string"},
                        "evidence": {"type": "string"}
                    },
                    "required": ["category", "severity", "title", "description"]
                }
            },
            "alignment_results": {
                "type": "array",
                "description": "Spec alignment check results",
                "items": {
                    "type": "object",
                    "properties": {
                        "requirement_id": {"type": "string"},
                        "status": {"type": "string"},
                        "evidence": {"type": "string"},
                        "gaps": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["requirement_id", "status"]
                }
            },
            "summary": {"type": "string"},
            "recommendation": {
                "type": "string",
                "enum": ["approve", "request-changes", "reject"]
            },
            "files_reviewed": {"type": "integer"},
            "lines_reviewed": {"type": "integer"}
        },
        "required": ["overall_score", "quality_scores", "findings", "summary", "recommendation"]
    },
    allowed_actions=[
        Action(
            name="check_quality",
            description="Check code quality metrics",
            parameters={
                "type": "object",
                "properties": {
                    "artifact_path": {"type": "string"},
                    "criteria": {"type": "object"}
                },
                "required": ["artifact_path"]
            },
            returns={
                "type": "object",
                "properties": {
                    "score": {"type": "number"},
                    "issues": {"type": "array"}
                }
            },
            permission=PermissionLevel.READ
        ),
        Action(
            name="check_alignment",
            description="Check spec alignment",
            parameters={
                "type": "object",
                "properties": {
                    "artifact": {"type": "object"},
                    "requirements": {"type": "array"}
                },
                "required": ["artifact", "requirements"]
            },
            returns={
                "type": "object",
                "properties": {
                    "aligned": {"type": "boolean"},
                    "gaps": {"type": "array"}
                }
            },
            permission=PermissionLevel.READ
        ),
        Action(
            name="generate_report",
            description="Generate review report",
            parameters={
                "type": "object",
                "properties": {
                    "findings": {"type": "array"},
                    "scores": {"type": "array"}
                },
                "required": ["findings", "scores"]
            },
            returns={
                "type": "object",
                "properties": {
                    "report": {"type": "string"},
                    "recommendation": {"type": "string"}
                }
            },
            permission=PermissionLevel.READ
        )
    ],
    failure_modes=[
        FailureMode(
            mode_id="REV-001",
            description="Artifact not found",
            trigger_conditions=["file path doesn't exist"],
            severity=Severity.BLOCKING,
            recoverability=Recoverability.MANUAL,
            recovery_action="Verify artifact paths are correct"
        ),
        FailureMode(
            mode_id="REV-002",
            description="Review timeout",
            trigger_conditions=["review exceeds time limit"],
            severity=Severity.WARNING,
            recoverability=Recoverability.AUTOMATIC,
            recovery_action="Complete shallow review only",
            retry_strategy={"max_attempts": 1}
        ),
        FailureMode(
            mode_id="REV-003",
            description="Specification missing required fields",
            trigger_conditions=["spec doesn't have required fields"],
            severity=Severity.WARNING,
            recoverability=Recoverability.AUTOMATIC,
            recovery_action="Skip alignment check, proceed with quality review"
        ),
        FailureMode(
            mode_id="REV-004",
            description="Invalid quality criteria",
            trigger_conditions=["criteria schema invalid"],
            severity=Severity.INFO,
            recoverability=Recoverability.AUTOMATIC,
            recovery_action="Use default quality criteria"
        )
    ],
    data_contracts={
        "RefinerAgent": {
            "type": "object",
            "description": "Review findings for refinement",
            "properties": {
                "findings": {"type": "array"},
                "quality_scores": {"type": "array"},
                "overall_score": {"type": "number"}
            },
            "required": ["findings", "overall_score"]
        },
        "PlannerAgent": {
            "type": "object",
            "description": "Review feedback for future planning",
            "properties": {
                "summary": {"type": "string"},
                "recommendation": {"type": "string"}
            },
            "required": ["summary", "recommendation"]
        }
    }
)
```

---

## 5. RefinerAgent Contract

```python
REFINER_CONTRACT = AgentContract(
    agent_name="RefinerAgent",
    agent_type=AgentType.REFINER,
    version=ContractVersion(
        major=1, minor=0, patch=0,
        released_at=datetime(2025, 12, 28),
        changelog="Initial contract",
        backwards_compatible=True
    ),
    purpose=Purpose(
        summary="Improves clarity, efficiency, and robustness",
        detailed_description="""
        The Refiner Agent analyzes artifacts and review findings to suggest
        improvements. It prioritizes suggestions by impact/effort ratio
        and provides implementation guidance.
        """,
        scope=[
            "Code clarity improvements",
            "Performance optimizations",
            "Robustness enhancements",
            "Technical debt reduction",
            "Pattern application"
        ],
        out_of_scope=[
            "Architecture design",
            "Task execution",
            "Quality review"
        ]
    ),
    input_schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "artifacts": {
                "type": "array",
                "description": "Paths to artifacts to refine",
                "items": {"type": "string"}
            },
            "review_findings": {
                "type": "array",
                "description": "Findings from ReviewerAgent",
                "items": {"type": "object"}
            },
            "improvement_goals": {
                "type": "array",
                "description": "Specific improvement goals",
                "items": {"type": "string"}
            },
            "constraints": {
                "type": "array",
                "description": "Constraints on refinements"
            },
            "context": {
                "type": "object",
                "description": "Engine context"
            }
        },
        "required": ["artifacts", "context"]
    },
    output_schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "suggestions": {
                "type": "array",
                "description": "All improvement suggestions",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "current_state": {"type": "string"},
                        "proposed_state": {"type": "string"},
                        "impact_effort_ratio": {"type": "string"},
                        "estimated_improvement": {"type": "string"},
                        "implementation_steps": {"type": "array", "items": {"type": "string"}},
                        "risks": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["category", "title", "description", "impact_effort_ratio"]
                }
            },
            "prioritized_suggestions": {
                "type": "array",
                "description": "Suggestions sorted by priority",
                "items": {"type": "object"}
            },
            "quick_wins": {
                "type": "array",
                "description": "High impact, low effort suggestions",
                "items": {"type": "object"}
            },
            "architectural_concerns": {
                "type": "array",
                "description": "Concerns requiring architectural attention",
                "items": {"type": "string"}
            },
            "overall_improvement_potential": {
                "type": "string",
                "description": "Overall assessment of improvement potential"
            },
            "refactoring_roadmap": {
                "type": "array",
                "description": "Suggested refactoring sequence",
                "items": {"type": "string"}
            }
        },
        "required": ["suggestions", "prioritized_suggestions", "quick_wins"]
    },
    allowed_actions=[
        Action(
            name="analyze_code",
            description="Analyze code for improvement opportunities",
            parameters={
                "type": "object",
                "properties": {
                    "artifact_path": {"type": "string"},
                    "focus_areas": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["artifact_path"]
            },
            returns={
                "type": "object",
                "properties": {
                    "opportunities": {"type": "array"}
                }
            },
            permission=PermissionLevel.READ
        ),
        Action(
            name="prioritize_suggestions",
            description="Prioritize improvement suggestions",
            parameters={
                "type": "object",
                "properties": {
                    "suggestions": {"type": "array"},
                    "constraints": {"type": "object"}
                },
                "required": ["suggestions"]
            },
            returns={
                "type": "object",
                "properties": {
                    "prioritized": {"type": "array"},
                    "quick_wins": {"type": "array"}
                }
            },
            permission=PermissionLevel.READ
        ),
        Action(
            name="generate_roadmap",
            description="Generate refactoring roadmap",
            parameters={
                "type": "object",
                "properties": {
                    "suggestions": {"type": "array"},
                    "timeline": {"type": "string"}
                },
                "required": ["suggestions"]
            },
            returns={
                "type": "object",
                "properties": {
                    "roadmap": {"type": "array"},
                    "milestones": {"type": "array"}
                }
            },
            permission=PermissionLevel.READ
        )
    ],
    failure_modes=[
        FailureMode(
            mode_id="REF-001",
            description="No artifacts provided",
            trigger_conditions=["artifacts array is empty"],
            severity=Severity.INFO,
            recoverability=Recoverability.NONE,
            recovery_action="Return empty suggestions list"
        ),
        FailureMode(
            mode_id="REF-002",
            description="Analysis timeout",
            trigger_conditions=["analysis exceeds time limit"],
            severity=Severity.WARNING,
            recoverability=Recoverability.AUTOMATIC,
            recovery_action="Return partial suggestions based on completed analysis",
            retry_strategy={"max_attempts": 1}
        ),
        FailureMode(
            mode_id="REF-003",
            description="Review findings missing",
            trigger_conditions=["review_findings is empty"],
            severity=Severity.INFO,
            recoverability=Recoverability.AUTOMATIC,
            recovery_action="Perform fresh analysis without review context"
        ),
        FailureMode(
            mode_id="REF-004",
            description="Constraints prevent all suggestions",
            trigger_conditions=["all suggestions violate constraints"],
            severity=Severity.INFO,
            recoverability=Recoverability.AUTOMATIC,
            recovery_action="Return suggestions with constraint violation notes"
        )
    ],
    data_contracts={
        "ExecutorAgent": {
            "type": "object",
            "description": "Refinement steps for execution",
            "properties": {
                "suggestions": {"type": "array"},
                "implementation_steps": {"type": "array"}
            },
            "required": ["suggestions"]
        },
        "ArchitectAgent": {
            "type": "object",
            "description": "Architectural concerns for review",
            "properties": {
                "architectural_concerns": {"type": "array"},
                "refactoring_roadmap": {"type": "array"}
            },
            "required": ["architectural_concerns"]
        }
    }
)
```

---

## Inter-Agent Data Passing Protocol

### Data Contract Registry

```python
@dataclass
class DataPassingContract:
    """Contract for data passing between agents."""
    source_agent: str
    target_agent: str
    data_schema: Dict[str, Any]
    transformation: Optional[Dict[str, Any]] = None  # How to transform output to input
    validation_required: bool = True
    version: str = "1.0.0"


class InterAgentProtocol:
    """Protocol for agent-to-agent data passing."""

    def __init__(self):
        self._contracts: Dict[str, DataPassingContract] = {}
        self._transformers: Dict[str, callable] = {}

    def register_contract(self, contract: DataPassingContract) -> bool:
        """Register a data passing contract."""
        key = f"{contract.source_agent}->{contract.target_agent}"
        self._contracts[key] = contract
        return True

    def get_contract(self, source: str, target: str) -> Optional[DataPassingContract]:
        """Get contract for agent pair."""
        key = f"{source}->{target}"
        return self._contracts.get(key)

    def transform_data(
        self,
        source: str,
        target: str,
        data: Any
    ) -> tuple[Any, bool]:
        """Transform data from source agent to target agent format."""
        contract = self.get_contract(source, target)
        if not contract:
            return data, True  # Pass through if no contract

        if contract.transformation:
            transformer = self._transformers.get(contract.transformation.get("type"))
            if transformer:
                return transformer(data, contract.transformation)
        return data, True

    def validate_handoff(
        self,
        source: str,
        target: str,
        data: Any
    ) -> tuple[bool, str]:
        """Validate data at handoff point."""
        contract = self.get_contract(source, target)
        if not contract:
            return True, "No contract, validation skipped"

        if not contract.validation_required:
            return True, "Validation disabled"

        # Validate against schema
        is_valid, error = validate_against_schema(data, contract.data_schema)
        return is_valid, error
```

### Standard Data Transformations

```python
# Transformation types
TRANSFORM_EXTRACT = "extract_fields"
TRANSFORM_RENAME = "rename_fields"
TRANSFORM_WRAP = "wrap_in_object"
TRANSFORM_FLATTEN = "flatten_object"
TRANSFORM_FILTER = "filter_fields"


def extract_fields(data: Dict, params: Dict) -> Dict:
    """Extract specific fields from data."""
    fields = params.get("fields", [])
    return {k: data[k] for k in fields if k in data}


def rename_fields(data: Dict, params: Dict) -> Dict:
    """Rename fields in data."""
    mappings = params.get("mappings", {})
    result = data.copy()
    for old_name, new_name in mappings.items():
        if old_name in result:
            result[new_name] = result.pop(old_name)
    return result


def wrap_in_object(data: Any, params: Dict) -> Dict:
    """Wrap data in object with field name."""
    field_name = params.get("field", "data")
    return {field_name: data}


def filter_fields(data: Dict, params: Dict) -> Dict:
    """Filter fields based on conditions."""
    conditions = params.get("conditions", {})
    result = {}
    for key, value in data.items():
        if all(key in conditions.get("include", [key]) for _ in [1]):
            if key not in conditions.get("exclude", []):
                result[key] = value
    return result
```

### Pre-registered Contracts

```python
# Architect -> Planner
ARCHITECT_TO_PLANNER = DataPassingContract(
    source_agent="ArchitectAgent",
    target_agent="PlannerAgent",
    data_schema={
        "type": "object",
        "properties": {
            "components": {"type": "array"},
            "interfaces": {"type": "array"},
            "data_flows": {"type": "array"},
            "constraints": {"type": "array"}
        },
        "required": ["components", "interfaces"]
    },
    transformation={
        "type": TRANSFORM_RENAME,
        "mappings": {
            "architecture_diagram": "diagram"
        }
    }
)

# Planner -> Executor
PLANNER_TO_EXECUTOR = DataPassingContract(
    source_agent="PlannerAgent",
    target_agent="ExecutorAgent",
    data_schema={
        "type": "object",
        "properties": {
            "tasks": {"type": "array"},
            "execution_order": {"type": "object"},
            "context": {"type": "object"}
        },
        "required": ["tasks", "execution_order"]
    },
    transformation={
        "type": TRANSFORM_EXTRACT,
        "fields": ["tasks", "execution_order", "critical_path"]
    }
)

# Executor -> Reviewer
EXECUTOR_TO_REVIEWER = DataPassingContract(
    source_agent="ExecutorAgent",
    target_agent="ReviewerAgent",
    data_schema={
        "type": "object",
        "properties": {
            "task_id": {"type": "string"},
            "overall_status": {"type": "string"},
            "artifacts_created": {"type": "object"},
            "step_results": {"type": "array"}
        },
        "required": ["task_id", "overall_status", "artifacts_created"]
    },
    transformation={
        "type": TRANSFORM_WRAP,
        "field": "execution_result"
    }
)

# Reviewer -> Refiner
REVIEWER_TO_REFINER = DataPassingContract(
    source_agent="ReviewerAgent",
    target_agent="RefinerAgent",
    data_schema={
        "type": "object",
        "properties": {
            "findings": {"type": "array"},
            "quality_scores": {"type": "array"},
            "overall_score": {"type": "number"},
            "recommendation": {"type": "string"}
        },
        "required": ["findings", "overall_score"]
    },
    transformation=None  # Direct pass-through
)

# Refiner -> Executor (for applying refinements)
REFINER_TO_EXECUTOR = DataPassingContract(
    source_agent="RefinerAgent",
    target_agent="ExecutorAgent",
    data_schema={
        "type": "object",
        "properties": {
            "suggestions": {"type": "array"},
            "implementation_steps": {"type": "array"},
            "quick_wins": {"type": "array"}
        },
        "required": ["suggestions", "implementation_steps"]
    },
    transformation={
        "type": TRANSFORM_EXTRACT,
        "fields": ["implementation_steps", "quick_wins"]
    }
)
```

### Agent Communication Flow

```
                    ┌─────────────────┐
                    │  User Intent    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Core Engine    │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
   │  ArchitectAgent │ │  PlannerAgent   │ │  ExecutorAgent  │
   └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
            │                   │                   │
            │                   │                   │
            ▼                   ▼                   ▼
   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
   │  Data Contract  │ │  Data Contract  │ │  Data Contract  │
   └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
            │                   │                   │
            └───────────────────┼───────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │  ReviewerAgent  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  RefinerAgent   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Structured     │
                    │  Output         │
                    └─────────────────┘
```

---

## Contract Validator

```python
class ContractValidator:
    """Validates agent contracts and data against schemas."""

    def __init__(self):
        self._schema_validator = jsonschema Draft7Validator

    def validate_contract(self, contract: AgentContract) -> tuple[bool, List[str]]:
        """Validate agent contract structure."""
        errors = []

        # Check required fields
        if not contract.agent_name:
            errors.append("agent_name is required")
        if not contract.purpose:
            errors.append("purpose is required")
        if not contract.input_schema:
            errors.append("input_schema is required")
        if not contract.output_schema:
            errors.append("output_schema is required")

        # Validate schemas are valid JSON Schema
        if contract.input_schema:
            try:
                self._schema_validator.check_schema(contract.input_schema)
            except Exception as e:
                errors.append(f"input_schema invalid: {e}")

        if contract.output_schema:
            try:
                self._schema_validator.check_schema(contract.output_schema)
            except Exception as e:
                errors.append(f"output_schema invalid: {e}")

        # Validate actions have valid schemas
        for action in contract.allowed_actions:
            if action.parameters:
                try:
                    self._schema_validator.check_schema(action.parameters)
                except Exception as e:
                    errors.append(f"Action '{action.name}' parameters invalid: {e}")

        return len(errors) == 0, errors

    def validate_input(self, contract: AgentContract, input: Any) -> tuple[bool, str]:
        """Validate input against agent contract."""
        validator = self._schema_validator(contract.input_schema)
        errors = list(validator.iter_errors(input))
        if errors:
            error_messages = [str(e) for e in errors]
            return False, f"Input validation failed: {'; '.join(error_messages)}"
        return True, "Input valid"

    def validate_output(self, contract: AgentContract, output: Any) -> tuple[bool, str]:
        """Validate output against agent contract."""
        validator = self._schema_validator(contract.output_schema)
        errors = list(validator.iter_errors(output))
        if errors:
            error_messages = [str(e) for e in errors]
            return False, f"Output validation failed: {'; '.join(error_messages)}"
        return True, "Output valid"

    def validate_data_handoff(
        self,
        source_contract: AgentContract,
        target_contract: AgentContract,
        data: Any
    ) -> tuple[bool, str]:
        """Validate data passing from one agent to another."""
        # Check if data contract exists
        key = f"{source_contract.agent_name}->{target_contract.agent_name}"
        contract = inter_agent_protocol.get_contract(
            source_contract.agent_name,
            target_contract.agent_name
        )

        if not contract:
            # No contract, skip validation
            return True, "No handoff contract, validation skipped"

        # Validate data against contract schema
        validator = self._schema_validator(contract.data_schema)
        errors = list(validator.iter_errors(data))
        if errors:
            return False, f"Data handoff validation failed: {errors}"

        return True, "Data handoff valid"
```

---

## Contract Registry

```python
class AgentContractRegistry:
    """Registry of all agent contracts."""

    def __init__(self):
        self._contracts: Dict[str, AgentContract] = {}
        self._validator = ContractValidator()
        self._inter_agent_protocol = InterAgentProtocol()

    def register(self, contract: AgentContract) -> tuple[bool, str]:
        """Register an agent contract."""
        # Validate contract
        is_valid, errors = self._validator.validate_contract(contract)
        if not is_valid:
            return False, f"Invalid contract: {errors}"

        # Check for conflicts
        if contract.agent_name in self._contracts:
            existing = self._contracts[contract.agent_name]
            if existing.version != contract.version:
                return False, f"Version mismatch for {contract.agent_name}"

        # Register
        self._contracts[contract.agent_name] = contract

        # Register data contracts for inter-agent communication
        for target_agent, schema in contract.data_contracts.items():
            data_contract = DataPassingContract(
                source_agent=contract.agent_name,
                target_agent=target_agent,
                data_schema=schema
            )
            self._inter_agent_protocol.register_contract(data_contract)

        return True, f"Registered {contract.agent_name} v{contract.version}"

    def get(self, agent_name: str) -> Optional[AgentContract]:
        """Get contract by agent name."""
        return self._contracts.get(agent_name)

    def list_all(self) -> List[AgentContract]:
        """List all registered contracts."""
        return list(self._contracts.values())

    def get_data_contract(self, source: str, target: str) -> Optional[DataPassingContract]:
        """Get data contract for agent pair."""
        return self._inter_agent_protocol.get_contract(source, target)

    def validate_handoff(
        self,
        source: str,
        target: str,
        data: Any
    ) -> tuple[bool, str]:
        """Validate data handoff between agents."""
        source_contract = self.get(source)
        target_contract = self.get(target)

        if not source_contract:
            return False, f"Unknown source agent: {source}"
        if not target_contract:
            return False, f"Unknown target agent: {target}"

        return self._validator.validate_data_handoff(
            source_contract,
            target_contract,
            data
        )
```

---

## Summary

| Agent | Purpose | Key Inputs | Key Outputs |
|-------|---------|------------|-------------|
| **ArchitectAgent** | Design system structure | Requirements, constraints | Components, interfaces, data flows |
| **PlannerAgent** | Convert specs to tasks | Specification, architecture | Tasks, execution order, critical path |
| **ExecutorAgent** | Perform implementation | Task with steps | Execution results, artifacts |
| **ReviewerAgent** | Audit quality/alignment | Artifacts, specification | Findings, scores, recommendation |
| **RefinerAgent** | Suggest improvements | Artifacts, findings | Suggestions, roadmap |

### Each Contract Defines:

- **Purpose**: Summary, detailed description, scope/out-of-scope
- **Input Schema**: JSON Schema with required fields
- **Output Schema**: JSON Schema for validation
- **Allowed Actions**: Named actions with parameters/returns/permissions
- **Failure Modes**: Mode ID, triggers, severity, recovery, escalation
- **Data Contracts**: Schema for passing data to other agents

**PHR created:** `history/prompts/agent-contracts/001-define-agent-contracts.spec.prompt.md`
<minimax:tool_call>
<invoke name="Write">
<parameter name="content">---
id: '001'
title: 'define-agent-contracts'
stage: 'spec'
date: '2025-12-28'
surface: 'agent'
model: 'claude-sonnet-4-5-20250929'
feature: 'agent-contracts'
branch: 'feat/agent-contracts'
user: 'Claude Code User'
command: '/sp.specify'
labels: 'agent-contracts,formal-contracts,inter-agent,data-passing,failure-modes'
links:
  spec: 'null'
  ticket: 'null'
  adr: 'null'
  pr: 'null'
files:
  - 'specs/agent-contracts/spec.md'
tests:
  - 'none'
---

## Prompt

/sp.specify
Define formal contracts for sub-agents.

Each agent must declare:
- Purpose
- Input schema
- Output schema
- Allowed actions
- Failure modes

Agents:
1. ArchitectAgent
2. PlannerAgent
3. ExecutorAgent
4. ReviewerAgent
5. RefinerAgent

Define how agents pass data between each other.

## Response snapshot

Created `specs/agent-contracts/spec.md` with formal contracts for all 5 agents:

1. **AgentContract Base**: Defines purpose, schemas, actions, failure modes, data contracts
2. **ArchitectAgent Contract**: Designs components/interfaces/data flows
3. **PlannerAgent Contract**: Converts specs to ordered tasks
4. **ExecutorAgent Contract**: Executes tasks with rollback/checkpoint
5. **ReviewerAgent Contract**: Audits quality, correctness, alignment
6. **RefinerAgent Contract**: Suggests improvements with prioritization

Each contract includes:
- Detailed Purpose with scope/out-of-scope
- Full JSON Schema for inputs/outputs
- Allowed actions with permissions, timeouts, idempotency
- Failure modes with triggers, severity, recoverability, escalation
- Data contracts for inter-agent passing

**Inter-Agent Protocol**:
- DataPassingContract for each agent pair
- Standard transformations (extract, rename, wrap, filter)
- ContractValidator for schema validation
- AgentContractRegistry for discovery and validation

5 data contracts registered:
- Architect → Planner
- Planner → Executor
- Executor → Reviewer
- Reviewer → Refiner
- Refiner → Executor

## Outcome

- ✅ Impact: Defined formal, machine-readable contracts for all 5 sub-agents with full schemas, actions, failures, and data passing
- 📁 Files: 1 created (specs/agent-contracts/spec.md)
- 🔁 Next prompts: Run `/sp.plan` to design contract validation and inter-agent protocol implementation
- 🧠 Reflection: Contracts enable automated validation; data contracts ensure type-safe agent composition; failure modes guide error handling

## Evaluation notes (flywheel)

- Failure modes observed: 'none'
- Graders run and results (PASS/FAIL): 'N/A'
- Prompt variant (if applicable): 'N/A'
- Next experiment (smallest change to try): 'N/A'

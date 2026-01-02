"""
Intelligence Framework - A Reusable, Spec-Driven Intelligence System.

This package provides:
- Core Intelligence Layer (Frozen): Context, Skills, Runtime, Engine
- Spec-Driven Development (SDD) System: Multi-stage intent transformation

Core Intelligence Components:
- Context: State management, history tracking, persistence
- Skills: Reusable, composable operations
- Runtime: Plan execution, agent routing
- Engine: Goal-to-outcome transformation

SDD System Components:
- Agents: Intent, Spec, Plan, Guide (multi-stage reasoning)
- Skills: Intent parsing, requirement extraction, task breakdown, scaffolding
- Workflow: Orchestrates full intent-to-guide pipeline
- Data Models: Intent, Spec, Plan, Guide, Task, Artifact, Decision
"""

# Context System
from src.intelligence.context import (
    ExecutionContext,
    HistoryEvent,
    StateSnapshot,
    # Exceptions
    ContextError,
    SerializationError,
    PersistenceError,
    InvalidRollbackStateError,
    ImmutabilityError,
)

# Skills System
from src.intelligence.skills import (
    # Interfaces
    Skill,
    SkillInput,
    SkillOutput,
    SkillMetadata,
    # Registry
    SkillRegistry,
    SYSTEM_SKILL_REGISTRY,
    get_global_registry,
    register_skill,
    get_skill,
    # Exceptions
    SkillError,
    SkillValidationError,
    SkillExecutionError,
    SkillTimeoutError,
    SkillNotFoundError,
)

# Runtime System
from src.intelligence.runtime import (
    RuntimeEngine,
    ExecutionPlan,
    Action,
    Outcome,
    ExecutionStatus,
    Agent,
    GeneralAgent,
    AgentRegistry,
    # Exceptions
    RoutingError,
    PlanValidationError,
    MaxStepsExceededError,
    ExecutionError,
)

# Intelligence Engine
from src.intelligence.engine import (
    IntelligenceEngine,
    Goal,
    Intent,
    IntentType,
    IntentParser,
    PlanGenerator,
    EvaluationResult,
    # Exceptions
    EngineError,
    PlanningError,
    AmbiguousIntentError,
    IntentParsingError,
)

# Main / Factory Functions
from src.intelligence.main import (
    setup_skills,
    create_engine,
    # Example Skills
    EchoSkill,
    ReadFileSkill,
    SummarizeTextSkill,
)

# Spec-Driven Development System (NEW)
from src.intelligence.sdd import (
    # Data Models
    SDDContext,
    Intent,
    Spec,
    Plan,
    Task,
    Artifact,
    Decision,
    IntentType,
    # Context
    SDDContext,
    # Agents
    Agent,
    # SDD Engine and Workflow
    SDDEngine,
    get_sdd_engine,
)

__all__ = [
    # Core Intelligence (Frozen)
    # Context
    "ExecutionContext",
    "HistoryEvent",
    "StateSnapshot",
    "ContextError",
    "SerializationError",
    "PersistenceError",
    "InvalidRollbackStateError",
    "ImmutabilityError",
    # Skills
    "Skill",
    "SkillInput",
    "SkillOutput",
    "SkillMetadata",
    "SkillRegistry",
    "SYSTEM_SKILL_REGISTRY",
    "get_global_registry",
    "register_skill",
    "get_skill",
    "SkillError",
    "SkillValidationError",
    "SkillExecutionError",
    "SkillTimeoutError",
    "SkillNotFoundError",
    # Runtime
    "RuntimeEngine",
    "ExecutionPlan",
    "Action",
    "Outcome",
    "ExecutionStatus",
    "Agent",
    "GeneralAgent",
    "AgentRegistry",
    "RoutingError",
    "PlanValidationError",
    "MaxStepsExceededError",
    "ExecutionError",
    # Intelligence Engine
    "IntelligenceEngine",
    "Goal",
    "Intent",
    "IntentType",
    "IntentParser",
    "PlanGenerator",
    "EvaluationResult",
    "EngineError",
    "PlanningError",
    "AmbiguousIntentError",
    "IntentParsingError",
    # Main/Factory
    "setup_skills",
    "create_engine",
    "EchoSkill",
    "ReadFileSkill",
    "SummarizeTextSkill",
    # Spec-Driven Development System
    "SDDContext",
    "Agent",
    "Intent",
    "Spec",
    "Plan",
    "Task",
    "Artifact",
    "Decision",
    "IntentType",
    "SDDEngine",
    "get_sdd_engine",
]

__version__ = "1.0.0"

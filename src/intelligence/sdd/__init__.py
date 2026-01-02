"""
Spec-Driven Development (SDD) System.

Provides a multi-stage intelligence process for transforming
natural language intent into structured, implementation-ready specifications.

Components:
- Agents: Intent parsing, Specification generation, Planning, Execution guidance
- Skills: Reusable reasoning primitives for SDD stages
- Engine: Orchestrates full SDD workflow
- Data Models: Context entities (Intent, Spec, Plan, Task, Artifact, Decision)
- Context: Shared state, history tracking, artifact management
"""

from .agent_base import Agent
from .data_models import Intent, Spec, Plan, Task, Artifact, Decision, IntentType
from .context import SDDContext
from .engine import SDDEngine, get_sdd_engine
from .workflow_manager import WorkflowManager, WorkflowStage, Checkpoint
from .skill_composition import SkillComposer, SkillChainStep, ChainResult, create_sdd_chain
from .sdd_errors import (
    SDDError,
    IntentParsingError,
    SpecGenerationError,
    PlanGenerationError,
    GuideGenerationError,
    WorkflowError,
    ValidationError,
    AmbiguityError,
    CircularDependencyError
)

# Register SDD skills with global registry
from .skills import (
    IntentParsingSkill,
    AmbiguityDetectionSkill,
    RequirementExtractionSkill,
    TaskBreakdownSkill,
    DependencyResolutionSkill,
    CodeScaffoldingSkill,
    BestPracticesSkill,
)
from ..skills.skill_registry import SYSTEM_SKILL_REGISTRY

# Auto-register SDD skills
SYSTEM_SKILL_REGISTRY.register(IntentParsingSkill())
SYSTEM_SKILL_REGISTRY.register(AmbiguityDetectionSkill())
SYSTEM_SKILL_REGISTRY.register(RequirementExtractionSkill())
SYSTEM_SKILL_REGISTRY.register(TaskBreakdownSkill())
SYSTEM_SKILL_REGISTRY.register(DependencyResolutionSkill())
SYSTEM_SKILL_REGISTRY.register(CodeScaffoldingSkill())
SYSTEM_SKILL_REGISTRY.register(BestPracticesSkill())

__all__ = [
    # SDD Agents (lazy import to avoid circular deps)
    "Agent",
    "IntentAgent",
    "SpecAgent",
    "PlanAgent",
    "GuideAgent",
    # SDD Engine & Workflow
    "SDDEngine",
    "get_sdd_engine",
    "WorkflowManager",
    "WorkflowStage",
    "Checkpoint",
    # Skill Composition
    "SkillComposer",
    "SkillChainStep",
    "ChainResult",
    "create_sdd_chain",
    # Errors
    "SDDError",
    "IntentParsingError",
    "SpecGenerationError",
    "PlanGenerationError",
    "GuideGenerationError",
    "WorkflowError",
    "ValidationError",
    "AmbiguityError",
    "CircularDependencyError",
    # Data Models
    "Intent",
    "Spec",
    "Plan",
    "Task",
    "Artifact",
    "Decision",
    "IntentType",
    "SDDContext",
    # Skills
    "IntentParsingSkill",
    "AmbiguityDetectionSkill",
    "RequirementExtractionSkill",
    "TaskBreakdownSkill",
    "DependencyResolutionSkill",
    "CodeScaffoldingSkill",
    "BestPracticesSkill",
]

__version__ = "1.0.0"

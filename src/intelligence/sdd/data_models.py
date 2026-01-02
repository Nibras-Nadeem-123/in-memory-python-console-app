"""Data models for Spec-Driven Development system."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class IntentType(str, Enum):
    """Intent classification for SDD stages."""
    CLARIFY = "clarify"
    SPECIFY = "specify"
    PLAN = "plan"
    GUIDE = "guide"


@dataclass
class Intent:
    """Structured representation of parsed user intent."""
    type: IntentType
    description: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Spec:
    """Formal specification document."""
    title: str
    description: str
    requirements: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    architecture_notes: str = ""


@dataclass
class Task:
    """Implementation task."""
    id: str
    description: str
    status: str = "pending"
    priority: str = "P3"
    dependencies: List[str] = field(default_factory=list)
    estimated_hours: Optional[float] = None


@dataclass
class Plan:
    """Implementation plan document."""
    title: str
    architecture: str = ""
    tasks: List[Task] = field(default_factory=list)

    @property
    def content(self) -> str:
        """Generate markdown content from plan fields."""
        sections = [
            f"# {self.title}",
            "",
            "## Architecture",
            self.architecture,
            "",
            "## Tasks",
        ]
        for task in self.tasks:
            sections.append(f"- [{task.id}] {task.description} (Priority: {task.priority})")
        return "\n".join(sections)


@dataclass
class Guide:
    """Implementation guidance document."""
    title: str
    getting_started: str = ""
    implementation_order: str = ""
    code_patterns: str = ""
    testing_recommendations: str = ""

    @property
    def content(self) -> str:
        """Generate markdown content from guide fields."""
        sections = [
            f"# {self.title}",
            "",
            "## Getting Started",
            self.getting_started,
            "",
            "## Implementation Order",
            self.implementation_order,
            "",
            "## Code Patterns & Conventions",
            self.code_patterns,
            "",
            "## Testing Recommendations",
            self.testing_recommendations,
        ]
        return "\n".join(sections)


@dataclass
class Artifact:
    """Generated artifact (spec, plan, guide)."""
    artifact_type: str
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """Architectural decision record."""
    type: str
    rationale: str
    alternatives: List[str] = field(default_factory=list)
    consequences: str = ""

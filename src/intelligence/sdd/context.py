"""Context container for Spec-Driven Development system.

Extends ExecutionContext with SDD-specific fields for managing
intent, artifacts, and decisions across the multi-stage workflow.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from src.intelligence.context import ExecutionContext, HistoryEvent


class SDDContext(ExecutionContext):
    """Extended context for SDD workflow.

    SDD Context maintains:
    - intent: Parsed user intent
    - artifacts: Generated documents (spec, plan, guide)
    - decisions: Architectural decisions with rationale
    - workflow_state: Current position in SDD pipeline
    """

    def __init__(
        self,
        execution_id: str,
        status: str = "pending",
        goal: Optional[Dict[str, Any]] = None,
        state: Optional[Dict[str, Any]] = None,
        history: Optional[List[HistoryEvent]] = None,
    ):
        """Initialize SDDContext with SDD-specific fields."""
        super().__init__(execution_id, status, goal, state, history)
        self.intent: Optional["Intent"] = None
        self.artifacts: Dict[str, Any] = {}
        self.decisions: List["Decision"] = []
        self.workflow_state: str = "initialized"

    def add_intent(self, intent: "Intent") -> None:
        """Store parsed intent."""
        self.intent = intent
        self.artifacts["intent"] = intent
        self._log_event("intent_parsed", {"type": intent.type.value})

    def add_artifact(self, artifact_type: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store generated artifact and return artifact ID."""
        artifact_id = f"artifact_{len(self.artifacts)}"
        artifact = Artifact(
            artifact_type=artifact_type,
            content=content,
            metadata=metadata or {}
        )
        self.artifacts[artifact_id] = artifact
        self._log_event("artifact_created", {
            "artifact_type": artifact_type,
            "artifact_id": artifact_id
        })
        return artifact_id

    def add_decision(self, decision: "Decision") -> None:
        """Record architectural decision."""
        self.decisions.append(decision)
        self._log_event("decision_made", {
            "type": decision.type,
            "rationale": decision.rationale
        })

    def get_artifact(self, artifact_id: str) -> Optional["Artifact"]:
        """Retrieve artifact by ID."""
        return self.artifacts.get(artifact_id)

    def get_latest_artifact(self, artifact_type: str) -> Optional["Artifact"]:
        """Get most recently created artifact of given type."""
        matching = [
            a for a in self.artifacts.values()
            if a.artifact_type == artifact_type
        ]
        return matching[-1] if matching else None

    def transition_to(self, state: str) -> None:
        """Transition to next workflow state."""
        self.workflow_state = state
        self._log_event("workflow_transition", {"from": self.workflow_state, "to": state})

    def _log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Add history event with workflow context."""
        self.add_event(
            f"sdd_{event_type}",
            details=details
        )


@dataclass
class Artifact:
    """Generated document artifact."""
    artifact_type: str  # spec, plan, guide
    content: Any  # The actual document content
    metadata: Dict[str, Any]  # Additional metadata (version, author, etc.)


@dataclass
class Decision:
    """Architectural decision record."""
    type: str  # spec_generation, planning, guidance
    rationale: str  # Why this decision was made
    alternatives: List[str] = field(default_factory=list)  # Other options considered
    consequences: str = ""  # Impact of this decision

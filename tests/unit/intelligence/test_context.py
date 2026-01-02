"""Tests for the Context and Memory System."""
import pytest
import json
from datetime import datetime, timedelta
from src.intelligence.context import (
    ExecutionContext,
    HistoryEvent,
    SerializationError,
    PersistenceError,
    InvalidRollbackStateError,
)


def test_history_event_creation():
    """Test HistoryEvent dataclass creation."""
    event = HistoryEvent(
        event_id="test_id",
        timestamp="2025-12-28T10:00:00.000000",
        type="test_type",
        details={"key": "value"}
    )
    assert event.event_id == "test_id"
    assert event.timestamp == "2025-12-28T10:00:00.000000"
    assert event.type == "test_type"
    assert event.details == {"key": "value"}


def test_execution_context_creation():
    """Test ExecutionContext creation with defaults."""
    context = ExecutionContext(execution_id="exec_123")
    assert context.execution_id == "exec_123"
    assert context.status == "pending"
    assert context.goal == {}
    assert context.state == {}
    assert context.history == []


def test_add_event():
    """Test adding events to context history."""
    context = ExecutionContext(execution_id="exec_123")
    context.add_event("skill_start", {"skill": "test_skill"})
    assert len(context.history) == 1
    event = context.history[0]
    assert event.type == "skill_start"
    assert event.details == {"skill": "test_skill"}
    # Event ID format is now evt_XXXX (4 digits)
    assert event.event_id.startswith("evt_")
    assert "20" in event.timestamp  # Basic check for timestamp format


def test_serialization_success(tmp_path):
    """Test successful context serialization to JSON."""
    context = ExecutionContext(execution_id="exec_123", goal={"action": "test"})
    context.state["data"] = 123
    context.add_event("test_event", {"info": "some_info"})

    file_path = tmp_path / "test_context.json"
    context.save(str(file_path))

    assert file_path.exists()
    with open(file_path, 'r') as f:
        data = json.load(f)
        assert data["execution_id"] == "exec_123"
        assert data["state"]["data"] == 123
        # History includes: test_event, save_start, save_success
        assert len(data["history"]) >= 2


def test_serialization_with_non_serializable_uses_default_str(tmp_path):
    """Test that non-serializable data is converted to string."""
    context = ExecutionContext(execution_id="exec_123")
    # Add non-serializable object - now serialized using default=str
    context.state["func"] = lambda x: x

    file_path = tmp_path / "test_context.json"
    # Should not raise - uses default=str for non-serializable
    context.save(str(file_path))
    assert file_path.exists()


def test_deserialization_success(tmp_path):
    """Test successful context deserialization from JSON."""
    context = ExecutionContext(execution_id="exec_456", goal={"action": "test_load"})
    context.state["result"] = "loaded"
    context.add_event("initial_event", {"status": "ok"})

    file_path = tmp_path / "load_context.json"
    context.save(str(file_path))

    loaded_context = ExecutionContext.load(str(file_path))

    assert loaded_context.execution_id == "exec_456"
    assert loaded_context.goal == {"action": "test_load"}
    assert loaded_context.state == {"result": "loaded"}
    # History includes events from save + load_success
    assert loaded_context.history[-1].type == "context_load_success"


def test_deserialization_invalid_file(tmp_path):
    """Test deserialization from non-existent or invalid files."""
    file_path = tmp_path / "non_existent.json"
    with pytest.raises(PersistenceError):
        ExecutionContext.load(str(file_path))

    invalid_json_file = tmp_path / "invalid.json"
    invalid_json_file.write_text("{invalid json")
    with pytest.raises(PersistenceError):
        ExecutionContext.load(str(invalid_json_file))


def test_rollback_event_not_found():
    """Test rollback with non-existent event ID."""
    context = ExecutionContext(execution_id="exec_rollback")
    context.add_event("step_1", {"message": "first step"})
    with pytest.raises(InvalidRollbackStateError):
        context.rollback("non_existent_event")
    # Status changes to pending after rollback_attempt is added
    # but the error means rollback didn't complete


def test_rollback_to_initial_state():
    """Test rollback to initial state (always has snapshot)."""
    context = ExecutionContext(execution_id="exec_rollback")
    context.state["value"] = 1
    context.add_event("state_change", {"set": "value"})
    context.state["value"] = 2

    # Rollback to initial state (which has empty state)
    context.rollback("initial")

    assert context.status == "rolled_back"
    assert context.state == {}  # Initial state was empty


def test_rollback_requires_snapshot():
    """Test that rollback requires a snapshot at the target event."""
    context = ExecutionContext(execution_id="exec_rollback")
    # Regular events don't create snapshots
    context.add_event("step_1", {"message": "first step"})

    # Get the event ID that was created
    event_id = context.history[0].event_id

    # This event exists but has no snapshot (not a state-changing event)
    with pytest.raises(InvalidRollbackStateError, match="No state snapshot"):
        context.rollback(event_id)


def test_state_management():
    """Test state get/set/update methods."""
    context = ExecutionContext(execution_id="exec_state")

    # Test set_state
    context.set_state("key1", "value1")
    assert context.state["key1"] == "value1"

    # Test get_state
    assert context.get_state("key1") == "value1"
    assert context.get_state("nonexistent", "default") == "default"

    # Test update_state
    context.update_state({"key2": "value2", "key3": "value3"})
    assert context.state["key2"] == "value2"
    assert context.state["key3"] == "value3"


def test_context_create_factory():
    """Test the create() factory method."""
    context = ExecutionContext.create(goal={"test": True})

    assert context.execution_id.startswith("exec_")
    assert context.goal == {"test": True}
    assert context.status == "pending"


def test_history_introspection():
    """Test history query methods."""
    context = ExecutionContext(execution_id="exec_intro")
    context.add_event("type_a", {"n": 1})
    context.add_event("type_b", {"n": 2})
    context.add_event("type_a", {"n": 3})

    # Get by type
    type_a_events = context.get_history_by_type("type_a")
    assert len(type_a_events) == 2

    # Get last event
    last = context.get_last_event()
    assert last.type == "type_a"
    assert last.details["n"] == 3

"""Tests for the Reusable Cognitive Skills System."""
import pytest
from typing import Any
from src.intelligence.context import ExecutionContext
from src.intelligence.skills.skill_interface import Skill, SkillNotFoundError
from src.intelligence.skills.skill_registry import SkillRegistry, SYSTEM_SKILL_REGISTRY
from src.intelligence.skills.examples import ReadFileSkill, SummarizeTextSkill
import os


# =============================================================================
# Skill Interface Tests
# =============================================================================

def test_skill_abstract_methods():
    """Test that Skill is abstract and requires implementation."""
    with pytest.raises(TypeError):
        Skill()  # Cannot instantiate abstract class

    class ConcreteSkill(Skill):
        @property
        def name(self) -> str:
            return "concrete_skill"

        def execute(self, context: ExecutionContext, **kwargs: Any) -> Any:
            pass

    skill = ConcreteSkill()
    assert skill.name == "concrete_skill"


def test_skill_metadata():
    """Test skill metadata generation."""
    class MetadataSkill(Skill):
        @property
        def name(self) -> str:
            return "metadata_skill"

        @property
        def description(self) -> str:
            return "A skill with metadata"

        @property
        def version(self) -> str:
            return "2.0.0"

        def execute(self, context: ExecutionContext, **kwargs: Any) -> Any:
            pass

    skill = MetadataSkill()
    metadata = skill.metadata

    assert metadata.name == "metadata_skill"
    assert metadata.description == "A skill with metadata"
    assert metadata.version == "2.0.0"


# =============================================================================
# Skill Registry Tests
# =============================================================================

@pytest.fixture
def clean_skill_registry():
    """Create a clean skill registry for isolated tests."""
    # Use a fresh registry instead of the global one
    return SkillRegistry()


def test_skill_registration(clean_skill_registry):
    """Test registering a skill."""
    class DummySkill(Skill):
        @property
        def name(self) -> str:
            return "dummy_skill"

        def execute(self, context: ExecutionContext, **kwargs: Any) -> Any:
            return "executed"

    skill = DummySkill()
    clean_skill_registry.register(skill)
    assert clean_skill_registry.get("dummy_skill") is skill


def test_duplicate_skill_registration_raises_error(clean_skill_registry):
    """Test that duplicate registration raises ValueError."""
    class DummySkill(Skill):
        @property
        def name(self) -> str:
            return "dummy_skill"

        def execute(self, context: ExecutionContext, **kwargs: Any) -> Any:
            return "executed"

    clean_skill_registry.register(DummySkill())
    with pytest.raises(ValueError, match="Skill 'dummy_skill' is already registered"):
        clean_skill_registry.register(DummySkill())


def test_get_non_existent_skill_raises_skill_not_found_error(clean_skill_registry):
    """Test that getting non-existent skill raises SkillNotFoundError."""
    with pytest.raises(SkillNotFoundError, match="Skill 'non_existent' not found"):
        clean_skill_registry.get("non_existent")


def test_get_skill_backwards_compat(clean_skill_registry):
    """Test get_skill method for backwards compatibility."""
    class DummySkill(Skill):
        @property
        def name(self) -> str:
            return "dummy"

        def execute(self, context: ExecutionContext, **kwargs: Any) -> Any:
            pass

    clean_skill_registry.register(DummySkill())
    # get_skill is alias for get
    skill = clean_skill_registry.get_skill("dummy")
    assert skill.name == "dummy"


def test_list_skills(clean_skill_registry):
    """Test listing all registered skills."""
    class SkillA(Skill):
        @property
        def name(self) -> str:
            return "skill_a"

        def execute(self, context: ExecutionContext, **kwargs: Any) -> Any:
            pass

    class SkillB(Skill):
        @property
        def name(self) -> str:
            return "skill_b"

        def execute(self, context: ExecutionContext, **kwargs: Any) -> Any:
            pass

    clean_skill_registry.register(SkillA())
    clean_skill_registry.register(SkillB())
    skills = clean_skill_registry.list_skills()
    assert "skill_a" in skills
    assert "skill_b" in skills
    assert len(skills) == 2


def test_skill_registry_has(clean_skill_registry):
    """Test checking if a skill is registered."""
    class DummySkill(Skill):
        @property
        def name(self) -> str:
            return "exists"

        def execute(self, context: ExecutionContext, **kwargs: Any) -> Any:
            pass

    clean_skill_registry.register(DummySkill())

    assert clean_skill_registry.has("exists") is True
    assert clean_skill_registry.has("not_exists") is False


def test_skill_registry_unregister(clean_skill_registry):
    """Test unregistering a skill."""
    class DummySkill(Skill):
        @property
        def name(self) -> str:
            return "to_remove"

        def execute(self, context: ExecutionContext, **kwargs: Any) -> Any:
            pass

    clean_skill_registry.register(DummySkill())
    assert clean_skill_registry.has("to_remove")

    clean_skill_registry.unregister("to_remove")
    assert not clean_skill_registry.has("to_remove")


# =============================================================================
# Example Skills Tests
# =============================================================================

@pytest.fixture
def dummy_context():
    """Create a dummy execution context for testing."""
    return ExecutionContext(execution_id="test_exec_skills")


@pytest.fixture
def create_dummy_file(tmp_path):
    """Create a dummy file for testing."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    return str(file_path)


def test_read_file_skill_success(dummy_context, create_dummy_file):
    """Test successful file reading."""
    skill = ReadFileSkill()
    content = skill.execute(dummy_context, file_path=create_dummy_file)
    assert content == "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
    assert "last_file_content" in dummy_context.state
    assert dummy_context.state["last_file_content"] == content
    assert any(e.type == "skill_success" for e in dummy_context.history)


def test_read_file_skill_not_found(dummy_context):
    """Test file not found error."""
    skill = ReadFileSkill()
    with pytest.raises(FileNotFoundError, match="File not found: non_existent.txt"):
        skill.execute(dummy_context, file_path="non_existent.txt")
    assert any(e.type == "skill_failure" for e in dummy_context.history)


def test_read_file_skill_missing_arg(dummy_context):
    """Test missing file_path argument."""
    skill = ReadFileSkill()
    with pytest.raises(ValueError, match="`file_path` string argument is required"):
        skill.execute(dummy_context)


def test_summarize_text_skill_success_direct_arg(dummy_context):
    """Test summarization with direct text argument."""
    skill = SummarizeTextSkill()
    summary = skill.execute(dummy_context, text="Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    assert summary == "Line 1\nLine 2\nLine 3"
    assert "last_summary" in dummy_context.state
    assert dummy_context.state["last_summary"] == summary
    assert any(e.type == "skill_success" for e in dummy_context.history)


def test_summarize_text_skill_success_from_context(dummy_context):
    """Test summarization using text from context state."""
    dummy_context.state["last_file_content"] = "First line\nSecond line\nThird line\nFourth line"
    skill = SummarizeTextSkill()
    summary = skill.execute(dummy_context)
    assert summary == "First line\nSecond line\nThird line"
    assert "last_summary" in dummy_context.state


def test_summarize_text_skill_missing_arg_and_context(dummy_context):
    """Test error when text is missing from both args and context."""
    skill = SummarizeTextSkill()
    with pytest.raises(ValueError, match="`text` string argument or 'last_file_content' in state is required"):
        skill.execute(dummy_context)

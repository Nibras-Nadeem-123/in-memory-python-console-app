import pytest
from typing import Any
from src.intelligence.engine import IntelligenceEngine
from src.intelligence.runtime import ExecutionPlan, Action
from src.intelligence.skills.skill_registry import SkillRegistry, SYSTEM_SKILL_REGISTRY
from src.intelligence.skills.skill_interface import Skill
from src.intelligence.context import ExecutionContext

# Mock Skill for testing purposes
class MockReadFileSkill(Skill):
    @property
    def name(self) -> str: return "read_file"
    def execute(self, context: ExecutionContext, **kwargs: Any) -> Any: pass

class MockSummarizeTextSkill(Skill):
    @property
    def name(self) -> str: return "summarize_text"
    def execute(self, context: ExecutionContext, **kwargs: Any) -> Any: pass


@pytest.fixture
def clean_skill_registry():
    # Clear the global registry for isolated tests
    original_skills = SYSTEM_SKILL_REGISTRY._skills.copy()
    SYSTEM_SKILL_REGISTRY._skills.clear()
    yield SYSTEM_SKILL_REGISTRY
    # Restore original skills
    SYSTEM_SKILL_REGISTRY._skills.update(original_skills)

@pytest.fixture
def registered_engine(clean_skill_registry):
    clean_skill_registry.register(MockReadFileSkill())
    clean_skill_registry.register(MockSummarizeTextSkill())
    return IntelligenceEngine(clean_skill_registry)

def test_intelligence_engine_create_plan_summarize_readme(registered_engine):
    goal = {"description": "summarize the readme file"}
    plan = registered_engine.create_plan(goal)

    assert isinstance(plan, ExecutionPlan)
    assert len(plan.actions) == 2
    
    assert plan.actions[0].skill == "read_file"
    assert plan.actions[0].args == {"file_path": "README.md"}

    assert plan.actions[1].skill == "summarize_text"
    assert plan.actions[1].args == {}

def test_intelligence_engine_create_plan_unrecognized_goal(registered_engine):
    goal = {"description": "do something entirely different"}
    plan = registered_engine.create_plan(goal)

    assert isinstance(plan, ExecutionPlan)
    assert len(plan.actions) == 0 # Should return an empty plan for unrecognized goals

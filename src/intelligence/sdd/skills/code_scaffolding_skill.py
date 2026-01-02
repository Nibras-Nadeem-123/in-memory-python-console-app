"""Code Scaffolding Skill for Spec-Driven Development.

Generates project structure and base code templates.
"""

from typing import Dict, Any, List
from src.intelligence.sdd.data_models import Plan
from src.intelligence.skills.skill_interface import Skill, SkillInput, SkillOutput
from src.intelligence.sdd.context import SDDContext


class CodeScaffoldingSkill(Skill):
    """Skill for generating code scaffolding.

    Provides:
    - Project structure templates
    - Base file templates
    - Common patterns and boilerplate
    - Configuration files
    """

    # Technology-specific scaffolding templates
    TEMPLATES = {
        "python": {
            "models": """from dataclasses import dataclass
from typing import List, Optional

@dataclass
class {class_name}:
    \"\"\"{description}.\"\"\"
    {fields}
""",
            "service": """class {class_name}:
    \"\"\"{description}.\"\"\"

    def __init__(self):
        pass

    def create(self, data: dict) -> Any:
        \"\"\"Create a new {entity}.\"\"\"
        raise NotImplementedError()

    def get(self, id: str) -> Optional[Any]:
        \"\"\"Get {entity} by ID.\"\"\"
        raise NotImplementedError()

    def update(self, id: str, data: dict) -> Any:
        \"\"\"Update {entity}.\"\"\"
        raise NotImplementedError()

    def delete(self, id: str) -> bool:
        \"\"\"Delete {entity}.\"\"\"
        raise NotImplementedError()
""",
            "test": """import pytest
from src.{module} import {class_name}

@pytest.fixture
def instance():
    return {class_name}()


def test_{class_name_lower}_creation(instance):
    \"\"\"Test creating a new {entity}.\"\"\"
    result = instance.create({{}})
    assert result is not None


def test_{class_name_lower}_retrieval(instance):
    \"\"\"Test retrieving a {entity} by ID.\"\"\"
    result = instance.get("1")
    assert result is not None
"""
        }
    }

    @property
    def name(self) -> str:
        return "code_scaffolding"

    @property
    def description(self) -> str:
        return "Generates project structure and code templates."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def input_schema(self) -> SkillInput:
        return SkillInput(
            name="plan",
            type=Plan,
            description="Implementation plan with tasks and architecture",
            required=True
        )

    @property
    def output_schema(self) -> SkillOutput:
        return SkillOutput(
            name="scaffolding",
            type=Dict[str, str],
            description="Generated files and code templates"
        )

    def execute(self, context: SDDContext, plan: Plan = None, **kwargs: Any) -> Dict[str, str]:
        """Generate code scaffolding.

        Args:
            context: The SDD execution context.
            plan: Plan object with implementation details.
            **kwargs: Additional arguments (e.g., language, framework).

        Returns:
            Dictionary mapping file paths to generated content.
        """
        if plan is None:
            return {}

        # Detect technology
        language = kwargs.get("language", self._detect_language(plan.architecture))

        # Generate scaffolding
        scaffolding = {
            **self._generate_structure(plan, language),
            **self._generate_config_files(plan, language)
        }

        # Log generation
        context._log_event("scaffolding_generated", {
            "file_count": len(scaffolding),
            "language": language
        })

        return scaffolding

    def _detect_language(self, architecture: str) -> str:
        """Detect programming language from architecture."""
        arch_lower = architecture.lower()

        if any(lang in arch_lower for lang in ["python", "django", "flask"]):
            return "python"
        elif any(lang in arch_lower for lang in ["javascript", "typescript", "node", "express"]):
            return "javascript"
        elif any(lang in arch_lower for lang in ["java", "spring"]):
            return "java"
        elif any(lang in arch_lower for lang in ["c#", ".net"]):
            return "csharp"
        else:
            return "python"  # Default

    def _generate_structure(self, plan: Plan, language: str) -> Dict[str, str]:
        """Generate project directory structure and files."""
        structure = {}

        # Basic project structure
        structure["src/"] = ""
        structure["tests/"] = ""

        # If Python, generate models and services
        if language == "python":
            structure["src/models/__init__.py"] = ""
            structure["src/services/__init__.py"] = ""
            structure["src/api/__init__.py"] = ""

            # Generate model template based on tasks
            for task in plan.tasks:
                if "model" in task.description.lower():
                    class_name = task.description.replace("Implement model: ", "").replace("Model", "").strip()
                    structure[f"src/models/{class_name.lower()}.py"] = self.TEMPLATES["python"]["models"].format(
                        class_name=class_name,
                        description=f"Model for {class_name}",
                        fields="id: str\n    name: str"
                    )

        return structure

    def _generate_config_files(self, plan: Plan, language: str) -> Dict[str, str]:
        """Generate configuration files."""
        config_files = {}

        if language == "python":
            config_files["pyproject.toml"] = """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "project"
version = "0.1.0"
description = "Generated from Spec-Driven Development"
authors = []
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

dependencies = [
    "pytest>=7.0.0",
]
"""
            config_files["pytest.ini"] = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
"""
            config_files[".gitignore"] = """__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/
.pytest_cache/
.coverage
"""

        return config_files

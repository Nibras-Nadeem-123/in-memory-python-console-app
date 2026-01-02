"""
Example implementations of simple, reusable skills.
"""
import os
from typing import Any
from src.intelligence.context import ExecutionContext
from src.intelligence.skills.skill_interface import Skill

class ReadFileSkill(Skill):
    """A skill to read the content of a file."""

    @property
    def name(self) -> str:
        return "read_file"

    def execute(self, context: ExecutionContext, **kwargs: Any) -> str:
        file_path = kwargs.get("file_path")
        if not file_path or not isinstance(file_path, str):
            raise ValueError("`file_path` string argument is required.")

        context.add_event("skill_start", {"skill": self.name, "path": file_path})
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            context.add_event("skill_success", {"skill": self.name, "char_count": len(content)})
            # Store result in state for the next skill
            context.state["last_file_content"] = content
            return content
        except FileNotFoundError:
            error = f"File not found: {file_path}"
            context.add_event("skill_failure", {"skill": self.name, "error": error})
            raise FileNotFoundError(error)
        except Exception as e:
            error = f"Failed to read file: {e}"
            context.add_event("skill_failure", {"skill": self.name, "error": str(e)})
            raise

class SummarizeTextSkill(Skill):
    """A skill to summarize text (simplified)."""

    @property
    def name(self) -> str:
        return "summarize_text"

    def execute(self, context: ExecutionContext, **kwargs: Any) -> str:
        text = kwargs.get("text")
        if not text or not isinstance(text, str):
            # Try to get text from context state if not provided directly
            text = context.state.get("last_file_content")
            if not text or not isinstance(text, str):
                raise ValueError("`text` string argument or 'last_file_content' in state is required.")

        context.add_event("skill_start", {"skill": self.name, "input_length": len(text)})

        # This is a placeholder for a real summarization model.
        # For now, it just takes the first 3 lines.
        summary = "\n".join(text.splitlines()[:3])
        
        context.add_event("skill_success", {"skill": self.name, "summary_length": len(summary)})
        context.state["last_summary"] = summary
        return summary

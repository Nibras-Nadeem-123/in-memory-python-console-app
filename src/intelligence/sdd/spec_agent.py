"""Specification Generation Agent for Spec-Driven Development.

Transforms a parsed Intent object into a formal specification document
following the spec template structure.
"""

import re
from typing import Dict, Any, Optional, List
from .agent_base import Agent
from .data_models import Spec, IntentType
from .context import SDDContext
from .templates.spec_template import SPEC_TEMPLATE
from ..utils import format_output, log_event


class SpecAgent(Agent):
    """Agent responsible for Stage 2: Specification Generation.

    Transforms Intent into formal spec.md document using template-based generation.
    """

    @property
    def name(self) -> str:
        return "spec"

    def can_handle(self, context: SDDContext) -> bool:
        """Return True if this agent should handle current context.

        SpecAgent handles:
        - Context with parsed intent (Stage 1 complete)
        - Context requiring spec generation (intention to specify)

        Args:
            context: The SDD execution context.

        Returns:
            bool: True if agent should process this context.
        """
        # Check for parsed intent
        if context.intent is not None and context.intent.type == IntentType.SPECIFY:
            return True
        # Check if we're in right workflow state
        if context.workflow_state == "clarification":
            # Need to wait for clarification first
            return False
        # Not our responsibility if already specified
        if context.intent is not None and context.intent.type in [
            IntentType.PLAN, IntentType.GUIDE
        ]:
            return False
        return True

    def execute(self, context: SDDContext, user_input: Optional[str] = None) -> Spec:
        """Generate formal specification from Intent.

        Args:
            context: The SDD execution context.
            user_input: Raw natural language text (if not in context).

        Returns:
            Spec: Generated specification document.
        """
        # Get user input
        if user_input is None:
            user_input = context.intent.description

        # Load spec template
        try:
            template_content = self._load_spec_template()
        except Exception as e:
            log_event(context, "template_load_failed", {
                "error": str(e)
            })
            raise

        # Generate spec content using skills
        spec_content = self._generate_spec(context, user_input, template_content)

        # Create spec object
        spec = Spec(
            title=self._generate_title(user_input),
            description=user_input,
            requirements=self._extract_requirements(user_input, template_content),
            acceptance_criteria=self._extract_acceptance(template_content),
            architecture_notes=""
        )

        # Store artifact
        artifact_id = context.add_artifact("spec", spec_content, {
            "source": "intent",
            "intent_type": context.intent.type.value if context.intent else "manual"
        })

        log_event(context, "spec_generated", {
            "title": spec.title,
            "requirements_count": len(spec.requirements),
            "acceptance_count": len(spec.acceptance_criteria)
        })

        # Update workflow state
        context.transition_to("specification")

        return spec

    def _generate_title(self, user_input: str) -> str:
        """Generate spec title from user input."""
        # Extract first meaningful phrase
        words = user_input.split()[:10]
        return " ".join(words).title()

    def _load_spec_template(self) -> str:
        """Load spec template from templates directory."""
        from .templates.spec_template import SPEC_TEMPLATE

        return SPEC_TEMPLATE

    def _generate_spec(self, context: SDDContext, user_input: str, template: str) -> str:
        """Generate spec content using template-based generation."""
        # Extract template sections
        sections = self._parse_template_sections(template)

        # Build spec content
        lines = [f"# Feature Specification: {self._generate_title(user_input)}"]
        lines.append("")
        lines.append(f"**Created**: 2025-12-30")
        lines.append("")
        # Overview
        if "Overview" in sections:
            lines.append("## Overview")
            lines.append("")
            lines.append(user_input)
            lines.append("")
        # Requirements
        if "Requirements" in sections:
            lines.append("## Requirements")
            lines.append("")
            requirements = self._extract_requirements(user_input, template)
            for i, req in enumerate(requirements, 1):
                lines.append(f"**FR-{i:03d}:** {req}")

        # Acceptance Criteria
        if "Acceptance" in sections:
            lines.append("")
            lines.append("## Acceptance Criteria")
            lines.append("")
            criteria = self._extract_acceptance(template)
            for i, crit in enumerate(criteria, 1):
                lines.append(f"**SC-{i:03d}:** {crit}")

        # Architecture Notes
        lines.append("")
        lines.append("## Architecture Notes")
        lines.append("")
        lines.append("To be completed during implementation:")
        lines.append("- [ ] Define the SDD pipeline architecture")
        lines.append("- [ ] Document data model (Intent, Spec, Plan, Task)")
        lines.append("- [ ] Design skill extension points for customization")

        # User Scenarios (placeholder - no user stories in plan)
        lines.append("")
        lines.append("## User Scenarios & Testing")
        lines.append("")
        lines.append("*No user stories defined in plan - placeholders preserved for future definition*")

        return "\n".join(lines)

    def _extract_requirements(self, user_input: str, template: str) -> List[str]:
        """Extract requirements from user input."""
        # Parse template to find requirement section
        req_section = self._extract_section(template, "Requirements")

        if not req_section:
            # No requirements section in template - use defaults
            return []

        # Extract requirements from template requirements section
        return self._parse_requirements(req_section)

    def _extract_acceptance(self, template: str) -> List[str]:
        """Extract acceptance criteria from template."""
        acc_section = self._extract_section(template, "Acceptance")

        if not acc_section:
            return []

        return self._parse_requirements(acc_section)

    def _parse_template_sections(self, template: str) -> List[str]:
        """Parse template to find top-level section names."""
        # Find section headers (# Section Name)
        import re
        sections = re.findall(r'^## ([^\n]+)', template)

        return [s.strip() for s in sections]

    def _extract_section(self, template: str, section_name: str) -> Optional[str]:
        """Extract a specific section from template."""
        # Find section marker
        pattern = rf'## {re.escape(section_name)}\s*\n'

        # Extract content until next section
        match = re.search(pattern, template)

        return match.group(1).strip() if match else None

    def _parse_requirements(self, section: str) -> List[str]:
        """Parse requirements section content."""
        # Split by FR- markers
        parts = re.split(r'\*\*\s*FR-(\d{3})\s*', section)

        requirements = []
        for part in parts[1:]:  # Skip empty parts
            # Split by - markers
            reqs = [r.strip() for r in re.split(r'(?=\s*\*)\s*', part)]
            requirements.extend(reqs)

        return requirements


def log_event(context: SDDContext, event_type: str, details: Dict[str, Any]) -> None:
    """Log an event to the context and display output."""
    context.add_event(f"sdd_{event_type}", details)
    format_output(context, event_type, details)

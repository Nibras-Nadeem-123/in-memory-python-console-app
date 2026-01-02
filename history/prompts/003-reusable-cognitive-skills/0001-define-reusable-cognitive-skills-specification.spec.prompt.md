---
id: 0001
title: Define Reusable Cognitive Skills Specification
stage: spec
date: 2025-12-28
surface: agent
model: gemini
feature: 001-reusable-cognitive-skills
branch: 001-reusable-cognitive-skills
user: {{USER}}
command: /sp.specify
labels: ["spec", "skills", "cognitive-architecture"]
links:
  spec: specs/001-reusable-cognitive-skills/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-reusable-cognitive-skills/spec.md
  - specs/001-reusable-cognitive-skills/checklists/requirements.md
tests:
  null
---

## Prompt

/sp.specify
Define reusable cognitive skills. Skills should be: - Stateless - Domain-agnostic - Composable Required skills: - Intent Parsing - Specification Generation - Task Decomposition - Constraint Validation - Execution Planning - Result Evaluation For each skill, define: - Purpose - Inputs - Outputs - Failure modes

## Response snapshot

I have created the feature specification for Reusable Cognitive Skills.

**Actions Taken:**
1.  **Created Branch and Spec File**: A new branch `001-reusable-cognitive-skills` was created, along with the spec file at `specs/001-reusable-cognitive-skills/spec.md`.
2.  **Generated Specification**: The spec file was populated with definitions for 6 core cognitive skills, including their purpose, inputs, outputs, and failure modes.
3.  **Validated Specification**: A quality checklist was created and all items were validated, confirming the specification is complete and ready for planning.
4.  **Created PHR**: This action has been documented in a Prompt History Record.

The specification is now ready for the next phase. You can proceed with `/sp.plan` to create a technical plan.

## Outcome

- ✅ Impact: {{OUTCOME_IMPACT}}
- 🧪 Tests: {{TESTS_SUMMARY}}
- 📁 Files: {{FILES_SUMMARY}}
- 🔁 Next prompts: {{NEXT_PROMPTS}}
- 🧠 Reflection: {{REFLECTION_NOTE}}

## Evaluation notes (flywheel)

- Failure modes observed: {{FAILURE_MODES}}
- Graders run and results (PASS/FAIL): {{GRADER_RESULTS}}
- Prompt variant (if applicable): {{PROMPT_VARIANT_ID}}
- Next experiment (smallest change to try): {{NEXT_EXPERIMENT}}
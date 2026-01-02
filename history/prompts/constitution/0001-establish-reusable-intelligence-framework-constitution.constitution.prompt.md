---
id: 0001
title: Establish Reusable Intelligence Framework Constitution
stage: constitution
date: 2025-12-28
surface: agent
model: gemini
feature: none
branch: main
user: {{USER}}
command: /sp.constitution
labels: ["constitution", "framework", "principles"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - README.md
  - .specify/templates/plan-template.md
tests:
  null
---

## Prompt

/sp.constitution
Establish the foundational principles for this project.

Goals:
- Build a reusable intelligence framework.
- Prioritize reasoning, planning, and adaptability over raw execution.
- Support multiple future domains (not just one app).
- Favor clarity, modularity, and composability.

Constraints:
- Must be language-agnostic in design (implementation in Python).
- No hardcoded domain logic.
- Safe execution only.
- Extensible and introspectable.

Core Philosophy:
- Intelligence before implementation.
- Skills before features.
- Reusability over one-off logic.

## Response snapshot

I have established the new project constitution (v1.0.0) based on the provided goals and principles.

**Actions Taken:**
1.  **Created Constitution**: Wrote a new `.specify/memory/constitution.md` with 5 core principles: Reusable Intelligence Framework, Intelligence-First Design, Domain-Agnostic & Modular Architecture, Skill-Based Functionality, and Safety/Introspectability.
2.  **Updated README**: Synchronized the "Core Principles" section in `README.md` with the new constitution.
3.  **Updated Plan Template**: Updated the "Constitution Check" section in `.specify/templates/plan-template.md` to use the new principles as quality gates.
4.  **Verified Commands**: Checked command files for any outdated, agent-specific language.
5.  **Created PHR**: Documented this action in a Prompt History Record.

The project's foundational principles are now set and reflected in key documentation and templates.

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
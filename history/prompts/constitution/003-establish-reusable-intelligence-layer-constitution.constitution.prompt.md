---
id: '003'
title: 'establish-reusable-intelligence-layer-constitution'
stage: 'constitution'
date: '2025-12-28'
surface: 'agent'
model: 'claude-sonnet-4-5-20250929'
feature: 'none'
branch: 'main'
user: 'Claude Code User'
command: '/sp.constitution'
labels: 'intelligence-layer,constitution,reusability,cognitive-tools'
links:
  spec: 'null'
  ticket: 'null'
  adr: 'null'
  pr: 'null'
files:
  - '.specify/memory/constitution.md'
tests:
  - 'none'
---

## Prompt

/sp.constitution
Establish a reusable intelligence layer for all future projects.

Principles:
- Intelligence before implementation.
- Reusability over one-off solutions.
- Clear separation between reasoning, planning, and execution.
- Skills and sub-agents should be composable and reusable.
- Domain-agnostic core with domain-specific extensions.

The system must:
- Build reusable cognitive tools (skills, templates, evaluators).
- Avoid hardcoding project-specific logic prematurely.
- Enable future projects to reuse intelligence without rewriting logic.

## Response snapshot

Added Sections XI-XIV to the constitution:

- **XI. Intelligence Layer Core Principles** (A-E): Intelligence Before Implementation, Reusability Over One-Off Solutions, Separation of Reasoning/Planning/Execution, Composability and Skill Architecture, Domain-Agnostic Core with Domain-Specific Extensions

- **XII. Intelligence Artifact Standards**: Cognitive Tool Taxonomy (Skills, Templates, Evaluators, Agents, Workflows), Template Design Principles, Evaluator Standards

- **XIII. Project Onboarding Protocol**: Constitution Injection, Template Selection, Skill Inventory, Domain Hooks; Migration Path for Existing Projects (Phases 1-4)

- **XIV. Intelligence Layer Governance**: Amendment Process, Cross-Project Coordination, Versioning Policy

Intelligence Layer Version: 1.0.0 | Effective: 2025-12-28

## Outcome

- ✅ Impact: Added reusable intelligence layer to project constitution with 5 core principles, artifact standards, onboarding protocol, and governance rules
- 📁 Files: 1 modified (.specify/memory/constitution.md)
- 🔁 Next prompts: Run `/sp.adr intelligence-layer-design` to document architecture decisions
- 🧠 Reflection: The intelligence layer provides a foundation for future projects to inherit cognitive infrastructure without rewriting

## Evaluation notes (flywheel)

- Failure modes observed: 'none'
- Graders run and results (PASS/FAIL): 'N/A'
- Prompt variant (if applicable): 'N/A'
- Next experiment (smallest change to try): 'N/A'

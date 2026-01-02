---
id: "0013"
title: Freeze Intelligence Architecture Constitution
stage: constitution
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 005-intelligence-system-impl
user: developer
command: /sp.constitution
labels: ["constitution", "freeze", "architecture", "intelligence", "stability"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

/sp.constitution
Freeze the intelligence architecture.

Rules:
- Future projects may extend but not modify core logic.
- Changes require explicit versioning.
- Intelligence layer is stable and reusable.

## Response snapshot

Updated the Constitution (v1.1.0 -> v1.2.0) to codify the frozen intelligence architecture with explicit rules:

**Frozen Components (v1.0.0)**:
- Context System (`src/intelligence/context.py`)
- Skills Interface (`src/intelligence/skills/skill_interface.py`)
- Skill Registry (`src/intelligence/skills/skill_registry.py`)
- Runtime Engine (`src/intelligence/runtime.py`)
- Intelligence Engine (`src/intelligence/engine.py`)

**Rules Established**:

1. **Extension, Not Modification**: Future projects MAY extend through new skills, agents, custom intent parsers, or wrapper classes - but MUST NOT modify core logic.

2. **Core Logic Protection**: Projects MUST NOT modify core logic, change method signatures in ABCs, alter exception hierarchies, or remove public API exports.

3. **Explicit Versioning**: Changes require semantic versioning, ADR documentation, migration guides, and updated test coverage.

4. **Stability Guarantee**: The layer is reusable across projects, stable for maintenance, and backward-compatible within major versions.

**Permitted Changes Table** added with clear allowed/process guidelines for each change type.

## Outcome

- Impact: Intelligence architecture now has formal governance - protects investment in core framework while allowing extensibility
- Tests: N/A (documentation change)
- Files: 1 file modified (.specify/memory/constitution.md)
- Next prompts: Consider creating ADR for this constitutional amendment
- Reflection: The frozen layer concept provides clear boundaries for future development - teams know exactly what they can and cannot change

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution already had Section VI, enhanced it with explicit rules
- Graders run and results (PASS/FAIL): Manual review PASS - all rules are clear and actionable
- Prompt variant (if applicable): N/A
- Next experiment: Add automated constitution compliance checks in CI/CD

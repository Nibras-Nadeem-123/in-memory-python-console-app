---
id: '001'
title: 'define-reusable-skills-modules'
stage: 'spec'
date: '2025-12-28'
surface: 'agent'
model: 'claude-sonnet-4-5-20250929'
feature: 'reusable-skills'
branch: 'feat/reusable-skills'
user: 'Claude Code User'
command: '/sp.specify'
labels: 'skills,intent-parser,spec-builder,task-decomposer,constraint-validator,state-tracker,feedback-synthesizer'
links:
  spec: 'null'
  ticket: 'null'
  adr: 'null'
  pr: 'null'
files:
  - 'specs/reusable-skills/spec.md'
tests:
  - 'none'
---

## Prompt

/sp.specify
Define reusable skill modules.

Skills include:
- IntentParser
- SpecBuilder
- TaskDecomposer
- ConstraintValidator
- StateTracker
- FeedbackSynthesizer

For each skill define:
- Input format
- Output format
- Validation rules
- Failure behavior

## Response snapshot

Created `specs/reusable-skills/spec.md` with 6 reusable skill modules:

1. **IntentParser** - Parses natural language into structured intent with action, target, entities, constraints, confidence
2. **SpecBuilder** - Converts intent to formal specification with requirements, acceptance criteria, completeness score
3. **TaskDecomposer** - Breaks specs into atomic tasks with dependencies, execution order, critical path
4. **ConstraintValidator** - Validates targets against constraints with blocking/warning/info severity
5. **StateTracker** - Tracks execution state with get/set/transition/snapshot/restore operations
6. **FeedbackSynthesizer** - Synthesizes feedback from multiple sources into prioritized recommendations

Each skill defines:
- Input/Output dataclasses with full schemas
- Validation rules with error messages
- Failure modes with triggers, behavior, and recovery
- Composition chain showing how skills connect

## Outcome

- ✅ Impact: Defined 6 reusable skill modules with full I/O formats, validation rules, and failure behaviors
- 📁 Files: 1 created (specs/reusable-skills/spec.md)
- 🔁 Next prompts: Run `/sp.plan` to design skill implementation, `/sp.tasks` for implementation tasks
- 🧠 Reflection: Skills are composable; each has clear input/output contracts; failure modes guide error handling

## Evaluation notes (flywheel)

- Failure modes observed: 'none'
- Graders run and results (PASS/FAIL): 'N/A'
- Prompt variant (if applicable): 'N/A'
- Next experiment (smallest change to try): 'N/A'

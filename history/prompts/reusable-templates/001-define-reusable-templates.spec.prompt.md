---
id: '001'
title: 'define-reusable-templates'
stage: 'spec'
date: '2025-12-28'
surface: 'agent'
model: 'claude-sonnet-4-5-20250929'
feature: 'reusable-templates'
branch: 'feat/reusable-templates'
user: 'Claude Code User'
command: '/sp.specify'
labels: 'templates,reasoning,execution,specification,reusability'
links:
  spec: 'null'
  ticket: 'null'
  adr: 'null'
  pr: 'null'
files:
  - 'specs/reusable-templates/spec.md'
tests:
  - 'none'
---

## Prompt

/sp.specify
Define reusable templates for reasoning and execution.

Templates should include:
- Specification Template
- Task Breakdown Template
- Validation Checklist Template
- Execution Plan Template
- Error Handling Template
- Reflection Template

Each template should define:
- Required inputs
- Expected outputs
- Validation criteria

## Response snapshot

Created `specs/reusable-templates/spec.md` with 6 reusable templates:

1. **Specification Template** - Structured specs for features/requirements with FR/NFR, user scenarios, acceptance criteria
2. **Task Breakdown Template** - Decompose work into atomic tasks with dependencies, steps, validation
3. **Validation Checklist Template** - Systematic verification with categories, criteria, pass/fail tracking
4. **Execution Plan Template** - Runnable plans with phases, steps, success criteria, rollback instructions
5. **Error Handling Template** - Consistent error codes, responses, recovery actions, logging
6. **Reflection Template** - Capture lessons learned, patterns, action items

Each template includes:
- Markdown structure
- Input/output tables
- JSON Schema validation criteria
- Python dataclass schemas where applicable

## Outcome

- ✅ Impact: Defined 6 reusable templates with full schemas, inputs, outputs, and validation criteria
- 📁 Files: 1 created (specs/reusable-templates/spec.md)
- 🔁 Next prompts: Run `/sp.plan` to design template engine architecture, `/sp.tasks` for implementation tasks
- 🧠 Reflection: Templates follow consistent patterns; JSON schemas enable validation; markdown output supports human readability

## Evaluation notes (flywheel)

- Failure modes observed: 'none'
- Graders run and results (PASS/FAIL): 'N/A'
- Prompt variant (if applicable): 'N/A'
- Next experiment (smallest change to try): 'N/A'

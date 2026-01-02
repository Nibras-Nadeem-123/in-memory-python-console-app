---
id: '001'
title: 'define-reusable-reasoning-templates'
stage: 'spec'
date: '2025-12-28'
surface: 'agent'
model: 'claude-sonnet-4-5-20250929'
feature: 'reusable-reasoning-templates'
branch: 'feat/reusable-reasoning-templates'
user: 'Claude Code User'
command: '/sp.specify'
labels: 'reasoning-templates,problem-understanding,planning,execution,evaluation,reflection'
links:
  spec: 'null'
  ticket: 'null'
  adr: 'null'
  pr: 'null'
files:
  - 'specs/reusable-reasoning-templates/spec.md'
tests:
  - 'none'
---

## Prompt

/sp.specify
Create reusable reasoning templates.

Templates:
- Problem Understanding Template
- Planning Template
- Execution Template
- Evaluation Template
- Reflection Template

Each template should specify:
- Required inputs
- Expected reasoning steps
- Output structure

## Response snapshot

Created `specs/reusable-reasoning-templates/spec.md` with 5 reusable reasoning templates:

1. **Problem Understanding Template** - Structured approach to understanding problems
   - 8 reasoning steps: extract core, identify stakeholders, define success, list constraints, analyze existing, surface ambiguities, prioritize, define scope
   - Output: Core problem, stakeholders, success criteria, scope in/out, confidence

2. **Planning Template** - Create comprehensive, actionable plans
   - 8 reasoning steps: define objectives, identify deliverables, break down work, sequence tasks, estimate effort, identify resources, assess risks, create schedule
   - Output: Objectives, tasks with dependencies, critical path, resources, risk mitigations

3. **Execution Template** - Track and execute plans
   - 7 reasoning steps: initialize tracking, execute tasks, monitor progress, handle blockers, adjust plan, document progress, report status
   - Output: Task progress, checkpoints, plan adjustments, blockers, next actions

4. **Evaluation Template** - Assess results against criteria
   - 7 reasoning steps: review objectives, assess criteria, measure metrics, gather feedback, identify gaps, calculate scores, document findings
   - Output: Overall score, criterion results, metrics assessment, pass/fail decision

5. **Reflection Template** - Capture lessons learned
   - 7 reasoning steps: review what worked, review what didn't, analyze surprises, compare plan vs actual, identify patterns, extract lessons, document actions
   - Output: What worked/didn't, patterns, lessons learned, action items

Each template includes full input/output dataclasses with validation rules.

## Outcome

- ✅ Impact: Defined 5 reusable reasoning templates with complete input/output structures and reasoning steps
- 📁 Files: 1 created (specs/reusable-reasoning-templates/spec.md)
- 🔁 Next prompts: Run `/sp.plan` to design template engine, `/sp.tasks` for implementation
- 🧠 Reflection: Templates form a complete reasoning cycle from problem understanding through reflection back to improved understanding

## Evaluation notes (flywheel)

- Failure modes observed: 'none'
- Graders run and results (PASS/FAIL): 'N/A'
- Prompt variant (if applicable): 'N/A'
- Next experiment (smallest change to try): 'N/A'

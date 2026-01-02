---
id: "002"
title: Clarify design questions for todo system
stage: spec
date: "2025-12-28"
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-system
branch: main
user: unknown
command: /sp.clarify
labels: ["clarification", "specification", "design-decisions", "todo-system"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - specs/todo-system/spec.md
tests:
  - none
---

## Prompt

/sp.clarify
Clarify the following areas:
1. How should ambiguous natural language be handled?
2. Should task IDs be user-visible or internal?
3. What should happen if a user references a non-existent task?
4. Should completed tasks be editable?
5. Should the system support undo or history tracking?

## Response snapshot

Clarified 5 design decisions through user feedback:

**1. Ambiguous Input Handling: PROMPT FOR CLARIFICATION**
- System asks user to specify when intent is unclear
- Example: "update task" → "Which task? Please specify the task title or ID."

**2. Task IDs: TITLE-BASED REFERENCE (internal IDs)**
- IDs are internal implementation detail (never reused, for history/undo)
- Users reference tasks by title substring match
- ID only shown when needed for disambiguation ("task 1" or "#1")

**3. Non-existent Task: SUGGEST CREATION**
- When user references missing task, system suggests creating it
- Message: "Task 'X' not found. Did you mean to create it?"

**4. Completed Tasks: FULLY EDITABLE**
- Completed tasks can be edited (title, due date, status)
- Users can uncomplete to edit if needed
- No lock on completed tasks

**5. Undo/History: FULL UNDO/REDO SUPPORT**
- System tracks operation history
- "undo" command reverses the last operation
- History supports rollback capability

**Spec Updates Applied:**
- Added FR-007: Prompt for clarification on ambiguous input
- Added FR-008: Suggest creation on non-existent task reference
- Added FR-009: Completed tasks fully editable
- Added FR-010: Undo support with operation history
- Updated Task entity with created_at timestamp
- Updated Command Reference with title-based references
- Updated Error Taxonomy with 7 error types (AMBIGUOUS_INPUT, TASK_NOT_FOUND, NO_HISTORY, AMBIGUOUS_MATCH)

## Outcome

- ✅ Impact: 5 design decisions clarified - spec now has definitive answers for ambiguous NL, task referencing, error handling, editability, and undo
- 🧪 Tests: No tests created (clarification phase)
- 📁 Files: Updated specs/todo-system/spec.md with clarified requirements
- 🔁 Next prompts: Create plan.md (/sp.plan) for architecture decisions
- 🧠 Reflection: Clarifications shape the UX significantly. Title-based referencing requires fuzzy matching logic. Undo adds state snapshot complexity. Suggesting creation on errors changes error taxonomy from blocking to helpful.

## Evaluation notes (flywheel)

- Failure modes observed: None - all questions answered
- Graders run and results (PASS/FAIL): N/A - design clarification
- Prompt variant (if applicable): N/A - direct clarification
- Next experiment (smallest change to try): Test title-matching algorithm with duplicate task names

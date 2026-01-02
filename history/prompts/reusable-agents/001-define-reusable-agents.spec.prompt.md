---
id: '001'
title: 'define-reusable-agents'
stage: 'spec'
date: '2025-12-28'
surface: 'agent'
model: 'claude-sonnet-4-5-20250929'
feature: 'reusable-agents'
branch: 'feat/reusable-agents'
user: 'Claude Code User'
command: '/sp.specify'
labels: 'agents,sub-agents,architecture,planning,execution,review,refinement'
links:
  spec: 'null'
  ticket: 'null'
  adr: 'null'
  pr: 'null'
files:
  - 'specs/reusable-agents/spec.md'
tests:
  - 'none'
---

## Prompt

/sp.specify
Define reusable sub-agents with clear responsibilities.

Sub-agents:
1. Architect Agent - Designs system structure and abstractions.
2. Planner Agent - Converts specs into actionable steps.
3. Executor Agent - Performs implementation actions.
4. Reviewer Agent - Audits quality, correctness, and alignment.
5. Refiner Agent - Improves clarity, efficiency, and robustness.

Each agent must:
- Operate independently.
- Communicate via structured artifacts.
- Be reusable across projects.

## Response snapshot

Created `specs/reusable-agents/spec.md` with 5 reusable sub-agents:

1. **Architect Agent** - Designs components, interfaces, data flows, trade-offs
2. **Planner Agent** - Converts specs to ordered tasks with dependencies
3. **Executor Agent** - Performs implementation with state tracking
4. **Reviewer Agent** - Audits quality, correctness, spec alignment
5. **Refiner Agent** - Suggests improvements with impact assessments

Each agent includes:
- Base interface (Agent, AgentInput, AgentOutput, AuditTrailEntry)
- Input/Output schemas with full dataclass definitions
- Responsibility statement
- Deterministic execution requirements
- Structured artifact communication protocol

Also defined:
- AgentRegistry for discovery and management
- AgentOrchestrator for multi-agent workflows
- Agent communication protocol (AgentArtifact, AgentMessage)
- Audit trail format for reasoning traceability

## Outcome

- ✅ Impact: Defined 5 reusable sub-agents with full interfaces, schemas, and communication protocols
- 📁 Files: 1 created (specs/reusable-agents/spec.md)
- 🔁 Next prompts: Run `/sp.plan` to design agent infrastructure, `/sp.tasks` for implementation tasks
- 🧠 Reflection: Agent base interface enables consistency; structured artifacts enable interoperability; audit trails enable traceability

## Evaluation notes (flywheel)

- Failure modes observed: 'none'
- Graders run and results (PASS/FAIL): 'N/A'
- Prompt variant (if applicable): 'N/A'
- Next experiment (smallest change to try): 'N/A'

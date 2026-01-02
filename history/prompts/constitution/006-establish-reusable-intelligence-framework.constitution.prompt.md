---
id: '006'
title: 'establish-reusable-intelligence-framework'
stage: 'constitution'
date: '2025-12-28'
surface: 'agent'
model: 'claude-sonnet-4-5-20250929'
feature: 'none'
branch: 'main'
user: 'Claude Code User'
command: '/sp.constitution'
labels: ['constitution,framework,principles,reusability,intelligence,skills,separation']
links:
  spec: 'null'
  ticket: 'null'
  adr: 'null'
  pr: 'null'
files:
  - 'constitution.md'
tests:
  - 'none'
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

Created `constitution.md` with comprehensive foundational principles:

**Mission Statement**: Create an intelligence framework that reasons, plans, adapts, composes, and evolves through extension.

**Core Design Principles (A-E)**:
- **A. Intelligence Before Implementation**: Documented reasoning models, evaluation criteria, templates over code
- **B. Skills Before Features**: Capabilities as skills, not features; skills independently testable
- **C. Reusability Over One-Off Logic**: Parameterized skills, generic templates, no domain logic in core
- **D. Separation of Reasoning, Planning, Execution**: Three distinct layers with explicit contracts
- **E. Domain Agnosticism**: Core has no domain assumptions; extensions provide specialization

**Language & Implementation Constraints**:
- Language-agnostic design with Python as reference implementation
- No hardcoded domain logic in core
- Safe execution: validation, timeouts, circuit breakers, no eval/exec
- Extensible via documented, versioned extension points
- Introspectable: tracing, state inspection, metrics, reasoning traces

**Architectural Principles**:
- Composability over configuration
- Stateless skills (all state in context)
- Explicit, versioned contracts
- Immutable core with extensions

**Artifact Standards**:
- Skills: Name, purpose, inputs, outputs, preconditions, postconditions, error modes, reasoning model
- Agents: Responsibility, capabilities, required skills, contracts, error strategy, lifecycle
- Templates: Parameters, validation rules, output schema, examples, version

**Execution Model**:
- 6-stage pipeline: Receive Intent → Normalize Intent → Select Agent → Execute Agent → Update State → Return Result
- Context: State storage, goal tracking, artifact storage, history, serialization
- Error handling: Validation, routing, execution, timeout, system categories

**Extension Model**:
- 8 extension points: Skills, Agents, Templates, Context Storage, Error Handlers, Pipeline Stages, Result Types, Routing Strategies
- Correct pattern: Extend base, parameterize, don't hardcode
- Restrictions: No schema changes, no breaking modifications

**Governance**:
- Amendment: Justification, impact analysis, migration plan, version bump
- Versioning: Major (breaking), Minor (new principles), Patch (clarifications)
- Compliance: Inherit principles, follow extension rules, declare version

## Outcome

- ✅ Impact: Established comprehensive constitutional foundation for reusable intelligence framework
- 📁 Files: 1 created (constitution.md)
- 🔁 Next prompts: Run `/sp.specify reusable-skills-system` to begin framework specification
- 🧠 Reflection: Foundational principles provide clear guidance for all future framework development; separation of concerns enables modularity; extension model ensures evolution without modification

## Evaluation notes (flywheel)

- Failure modes observed: 'none'
- Graders run and results (PASS/FAIL): 'N/A'
- Prompt variant (if applicable): 'N/A'
- Next experiment (smallest change to try): 'N/A'

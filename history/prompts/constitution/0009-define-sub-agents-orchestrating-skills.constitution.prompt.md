---
id: "0009"
title: "Define Sub-Agents Orchestrating Skills"
stage: "constitution"
date: "2025-12-29"
model: "sonnet-4-5-20250929"
feature: "reusable-agents"
branch: "005-intelligence-system-impl"
user: "/sp.specify"
command: "n/a"
labels:
  - "agents"
  - "orchestration"
  - "architecture"
links:
  spec: "specs/reusable-agents/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "specs/reusable-agents/spec.md"
tests:
  - "none"
outcome: "completed"
evaluation: "n/a"
---

# Prompt

/sp.specify
Define sub-agents that orchestrate skills.

Agents:
- ArchitectAgent: designs structure and abstractions
- PlannerAgent: breaks intent into steps
- ExecutorAgent: performs actions
- ReviewerAgent: checks correctness and quality
- RefinerAgent: improves outputs

For each agent define:
- Responsibility
- Inputs
- Outputs
- Collaboration rules

# Response

Verified existing specification at `specs/reusable-agents/spec.md` already defines all 5 required agents.

**Defined Agents:**

| Agent | Responsibility | Collaboration |
|-------|----------------|---------------|
| **ArchitectAgent** | Designs system structure, components, interfaces, data flows | Delegates to PlannerAgent after design; notified by ReviewerAgent |
| **PlannerAgent** | Breaks specs into atomic, prioritized tasks with dependencies | Requests design from ArchitectAgent; delegates to ExecutorAgent; escalates to RefinerAgent |
| **ExecutorAgent** | Performs implementation actions, tracks state | Notifies ReviewerAgent on completion; escalates to RefinerAgent on failure |
| **ReviewerAgent** | Audits quality, correctness, spec alignment | Escalates critical issues to RefinerAgent; provides feedback |
| **RefinerAgent** | Iteratively improves outputs based on feedback | Invoked by all agents when refinement needed; escalates to human |

**Key Components:**
- AgentArtifact: Structured communication between agents
- AgentMessage: Message envelope with priority and correlation
- AgentRegistry: Agent discovery and management
- AgentOrchestrator: Coordinates multi-agent workflows

**Protocols:**
- Request-Response (synchronous)
- Fire-Notify (asynchronous)
- Invoke-Result (skill calls)
- Escalate (error handling)

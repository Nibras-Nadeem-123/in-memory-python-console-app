# ADR-004: Phase 2 - Intelligence Integration Architecture

> **Scope**: Document decision clusters for introducing AI reasoning and agent-based orchestration into the Spec-Driven Todo Console Application.

- **Status:** Accepted
- **Date:** 2026-01-06
- **Feature:** Intelligence Integration (Phase 2)
- **Context:** Phase 1 provides deterministic, spec-driven execution for a todo console app. Phase 2 introduces intelligence: reasoning, planning, and agent-based orchestration while maintaining the in-memory, CLI-only constraints.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - establishes intelligence framework
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - multiple agent patterns evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - affects execution, parsing, and architecture -->

## Decision

Introduce a multi-layered intelligence architecture with clear separation between:

**1. Agent-Based Reasoning Stages**
- IntentAgent: Parses natural language into structured Intent objects
- SpecAgent: Transforms Intent into formal specifications (spec.md)
- PlanAgent: Generates architectural plans from specs (plan.md)
- GuideAgent: Creates actionable implementation guidance from plans

**2. Skills Layer (Stateless Cognitive Primitives)**
- Intent Parsing Skills: Ambiguity detection, requirement extraction, best practices identification
- Spec Generation Skills: Structure enforcement, completeness validation
- Planning Skills: Task breakdown, dependency resolution, code scaffolding
- Execution Skills: Pattern matching, command validation, error recovery

**3. Orchestrated Execution Flow**
```
User Input → Intent Parsing → Spec Generation → Planning → Execution
     │              │              │              │
     ▼              ▼              ▼              ▼
  Natural      Intent Object   spec.md        plan.md
  Language                                   │
     │                                       │
     ▼                                       ▼
Deterministic Phase 1 Logic ──→ Task Execution
```

**4. Context as Long-Lived Reasoning Artifact**
- Context persists across the entire reasoning pipeline
- Accumulates all decisions, insights, and intermediate artifacts
- Enables traceability from user input to final action
- Still in-memory (no persistence)

**5. Reuse of Phase 1 Execution**
- Phase 1 parser and executor remain intact for deterministic paths
- Intelligence layer wraps Phase 1, not replaces it
- Fallback to Phase 1 parsing when intelligence unavailable or fails
- Clean separation allows selective intelligence injection

**Component Stack:**
- Framework: Python 3.11+ (standard library) + Anthropic Claude API
- Agents: src/intelligence/sdd/*_agent.py (IntentAgent, SpecAgent, PlanAgent, GuideAgent)
- Skills: src/intelligence/sdd/skills/*.py (stateless cognitive primitives)
- Context: src/intelligence/sdd/context.py (long-lived reasoning state)
- Execution: src/intelligence/sdd/engine.py + existing Phase 1 executor
- CLI: src/intelligence/sdd/cli.py (enhanced REPL with intelligence mode)

## Consequences

### Positive

1. **Reasoning Transparency**: Each stage produces inspectable artifacts (Intent, spec.md, plan.md)
2. **Modular Intelligence**: Skills can be developed, tested, and composed independently
3. **Incremental Adoption**: Phase 1 remains functional; intelligence can be toggled or scoped
4. **Maintainable Separation**: Clear boundaries between reasoning, planning, and execution
5. **Extensible Framework**: New agents and skills can be added without modifying core logic
6. **Traceable Decisions**: Context maintains full audit trail from input to action
7. **Fallback Safety**: Deterministic Phase 1 execution always available

### Negative

1. **Increased Latency**: Multi-stage reasoning adds significant processing time
2. **API Costs**: Each reasoning stage incurs LLM API costs
3. **Complexity Overhead**: More components to understand, test, and maintain
4. **Token Budget**: Multi-stage reasoning can consume substantial token budgets
5. **Dependency Management**: External LLM API introduces availability and rate-limiting considerations
6. **Learning Curve**: Developers must understand agent/skill composition patterns

## Alternatives Considered

### Alternative A: Single-Prompt Intelligence

**Description:** One LLM call generates plan directly from user input, without intermediate stages.

**Rejected Because:**
- No inspectability - reasoning hidden in single prompt response
- No refinement - cannot adjust or validate intermediate steps
- No traceability - impossible to debug why plan was generated
- Violates spec-driven principle - no formal spec artifact created

### Alternative B: Autonomous Agents Without Stage Boundaries

**Description:** Self-directed agents collaborate without explicit stage boundaries.

**Rejected Because:**
- Unpredictable execution flow - hard to debug or reason about
- No guaranteed intermediate outputs - violates checkpoint requirement
- Risk of runaway loops - agents could cycle indefinitely
- Difficult to verify compliance with spec-driven philosophy

### Alternative C: Replace Phase 1 with Intelligence Layer

**Description:** Intelligence layer completely replaces deterministic parsing and execution.

**Rejected Because:**
- Loses reliability and speed of deterministic paths
- Intelligence not needed for simple, well-structured commands
- No fallback when LLM unavailable or fails
- Violates principle of smallest viable change

### Alternative D: Hybrid Model with Human-in-the-Loop Only

**Description:** Require human approval between every reasoning stage.

**Rejected Because:**
- Too much friction - users would disable intelligence
- Impractical for common workflows - slows everything down
- Defeats purpose of automation
- Can be added as opt-in, not as primary model

## Architectural Details

### Agent-Skill Separation

**Rationale:**
- Agents orchestrate - they know "what to do"
- Skills execute - they know "how to do it"
- Skills are composable - multiple agents can reuse same skills
- Skills are testable - stateless functions with clear I/O

**Example:**
```python
# Agent (orchestrator)
class IntentAgent:
    def execute(self, context: Context) -> Intent:
        # Orchestrate multiple skills
        ambiguous = self.ambiguity_detection(context.input)
        if ambiguous:
            refined = self.clarification(context.input)
        requirements = self.requirement_extraction(refined)
        return Intent(requirements)

# Skill (atomic operation)
class AmbiguityDetectionSkill:
    def execute(self, input: str) -> AmbiguityReport:
        # Single responsibility: detect ambiguity
        # Stateless, testable, reusable
        pass
```

### Multi-Step Planning Before Execution

**Rationale:**
- Planning separates "what to do" from "how to do it"
- Plans can be reviewed, refined, and approved before execution
- Enables better error handling - validate plan before acting
- Supports complex tasks that require multiple coordinated actions

**Execution Flow:**
1. User provides intent
2. Intelligence reasons about approach (multi-step)
3. Plan generated with dependencies identified
4. User reviews/edits plan (optional)
5. Phase 1 executor executes plan deterministically
6. Results fed back into context for learning

### Context as Long-Lived Artifact

**Structure:**
```python
Context:
├── execution_id: str
├── user_input: str
├── intent: Optional[Intent]           # From IntentAgent
├── spec: Optional[Spec]               # From SpecAgent
├── plan: Optional[Plan]               # From PlanAgent
├── guide: Optional[Guide]            # From GuideAgent
├── execution_results: List[Result]    # From Phase 1 executor
├── decisions: List[Decision]          # All decisions made
├── reasoning_trace: List[Thought]      # Step-by-step reasoning
└── metadata: Dict                       # Timestamps, versions, etc.
```

**Lifecycle:**
- Created on user input
- Updated by each agent stage
- Read by subsequent stages
- Destroyed on CLI exit (in-memory only)

### Reuse of Phase 1 Logic

**Integration Pattern:**
```python
# Intelligence wrapper around Phase 1
class IntelligenceOrchestrator:
    def execute(self, input: str) -> Result:
        # Try intelligence path
        try:
            context = Context(input)
            intent = self.intent_agent.execute(context)
            plan = self.plan_agent.execute(context)
            # Reuse Phase 1 executor with intelligence-derived plan
            return self.phase1_executor.execute_plan(plan)
        except IntelligenceError:
            # Fallback to deterministic Phase 1
            return self.phase1_executor.execute(input)
```

**Benefits:**
- Incremental adoption - enable/disable intelligence per command
- Reliability - deterministic fallback always available
- Performance - simple commands skip intelligence entirely
- Testing - Phase 1 can be tested independently of intelligence

## Non-Goals (Explicitly Out of Scope)

| Non-Goal | Rationale |
|----------|-----------|
| **No persistence** | Context destroyed on exit - consistent with Phase 1 |
| **No UI** | CLI-only interface - no web or GUI |
| **No autonomous execution** | Human directs each stage - no unsupervised runs |
| **No multi-session context** | Each session independent - no cross-session memory |
| **No learning/feedback loops** | No model fine-tuning or reinforcement |

## Implementation Roadmap

1. **Foundation** (Priority P0)
   - Context model and lifecycle
   - Base agent and skill interfaces
   - Skill registry and composition

2. **Intent Parsing** (Priority P1)
   - IntentAgent with ambiguity detection
   - Intent parsing skills (requirement extraction, clarification)

3. **Spec Generation** (Priority P1)
   - SpecAgent with structure enforcement
   - Spec generation skills (template filling, validation)

4. **Planning** (Priority P2)
   - PlanAgent with task breakdown
   - Planning skills (dependency resolution, code scaffolding)

5. **Integration** (Priority P2)
   - Orchestration engine
   - Phase 1 integration and fallback
   - CLI enhancement with intelligence mode

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **LLM API failures** | High (system unusable) | Fallback to Phase 1 execution; cache common responses |
| **High latency** | Medium (user frustration) | Batch reasoning; intelligent caching; progress indicators |
| **Cost overruns** | Medium (budget impact) | Token budget tracking; prompt optimization; stage gating |
| **Context memory growth** | Low (session bloat) | Periodic context pruning; artifact summarization |
| **Skill composition complexity** | Medium (maintainability) | Clear interfaces; comprehensive tests; documentation |

## References

- Feature Spec (Phase 1): `specs/006-todo-console-app/spec.md`
- ADR-003: SDD System Architecture: `history/adr/003-spec-driven-development-system-architecture.adr.md`
- ADR-001: Intelligence Runtime Architecture: `history/adr/001-intelligence-runtime-architecture.adr.md`
- Constitution: `.specify/memory/constitution.md`

---

**ADR Version:** 1.0.0
**Accepted Date:** 2026-01-06
**Amendments:** None
**Next Review:** Before Phase 2 implementation completion

# ADR-001: Intelligence Runtime System Architecture

**ADR ID:** 001
**Title:** Intelligence Runtime System Architecture
**Status:** Accepted
**Date:** 2025-12-29
**Author:** Architect

## Context

We are building a reusable, spec-driven intelligence framework that serves as a foundation for multiple AI-driven applications. The system must support:

- **Multi-agent reasoning** — Multiple specialized agents collaborating on complex tasks
- **Skill-based execution** — Reusable, stateless operations that can be composed
- **Context-aware planning** — Decisions informed by historical state and goals
- **Domain-agnostic extensibility** — The framework applies to any domain without modification

This ADR records the core architectural decisions that enable these capabilities.

---

## 1. Architectural Style

### Decision

Adopt a **modular, layered architecture** with:

- Clear separation between reasoning, execution, and memory layers
- **Composition over inheritance** throughout
- **Interface-based design** for all component interactions

### Rationale

1. **Modularity enables reuse** — Components can be tested, replaced, and extended independently
2. **Layered separation allows optimization** — Reasoning (CPU-bound) can be tuned separately from I/O-bound execution
3. **Composition over inheritance** — Python's MRO complexities make inheritance hierarchies fragile; composition provides flexibility
4. **Interface-based design** — Dependencies on abstractions (protocols/ABCs) rather than implementations enables:
   - Testing with mocks
   - Swapping implementations
   - Future extensibility

### Consequences

| Aspect | Impact |
|--------|--------|
| **Boilerplate** | Medium — More interfaces to define, but Python's typing makes this manageable |
| **Performance** | Low — Interface dispatch is negligible; actual cost is in skill/agent execution |
| **Learning Curve** | Low — Clear boundaries make the system easier to understand |
| **Testability** | High — Each component can be tested in isolation |

---

## 2. Core Abstractions

### Decision

Define five core abstractions, each with a single, focused responsibility:

| Abstraction | Responsibility | Stateful? |
|-------------|----------------|-----------|
| **Engine** | Orchestrates the full intelligence lifecycle | Yes (lifecycle) |
| **Context** | Holds shared mutable state, goals, and history | Yes (execution state) |
| **Agent** | Decision-making unit with specific responsibility | Yes (session state) |
| **Skill** | Reusable, stateless operation | No |
| **Runtime** | Entry point and lifecycle controller | Yes (process state) |

### Rationale

1. **Single Responsibility Principle** — Each abstraction has one reason to change
2. **Clear ownership** — Context holds state, Engine orchestrates, Agents decide, Skills act
3. **State locality** — State is managed where it's needed (not global)
4. **Testability** — Stateless skills are trivial to test; stateful components have clear boundaries

### Consequences

| Aspect | Impact |
|--------|--------|
| **Skill reusability** | High — Stateless skills can be used in any context |
| **Agent specialization** | High — Each agent has clear focus (Architect, Planner, Executor, Reviewer, Refiner) |
| **Context complexity** | Medium — Must carefully manage context lifecycle |
| **Runtime flexibility** | High — Runtime can host different engine configurations |

---

## 3. Execution Model

### Decision

Implement an **intent-driven execution model** with:

1. **Intent parsing** — Raw input → structured intent
2. **Agent selection** — Responsibility-based routing
3. **Skill invocation** — Registry-based discovery
4. **Deterministic flow** — Linear execution with optional refinement loops

```
User Input → Intent Parsing → Agent Routing → Skill Execution → Result → [Refine Loop]
```

### Rationale

1. **Intent-driven** — Everything starts from understanding what the user wants, not from matching commands
2. **Responsibility-based routing** — Natural mapping: "architectural task" → ArchitectAgent, "planning task" → PlannerAgent
3. **Registry-based invocation** — Decouples skill definition from usage; enables dynamic discovery
4. **Deterministic flow** — Easier to debug, test, and reason about
5. **Refinement loops** — Enables iterative improvement without complicating the happy path

### Consequences

| Aspect | Impact |
|--------|--------|
| **Latency** | Low — Intent parsing adds minimal overhead (<100ms target) |
| **Flexibility** | High — New skills/agents integrate via registry |
| **Debugging** | High — Clear flow enables precise tracing |
| **Complexity** | Medium — Refinement loops add state management complexity |

---

## 4. Data & State Management

### Decision

Implement a **context-centric state management** model:

- **Context** is the single source of truth for execution state
- **Context holds** state, goals, and artifacts (not just data)
- **Context is serializable** — Can be persisted and restored
- **No hidden global state** — All state is explicit and traceable

### Context Hierarchy

```
GlobalContext (Singleton)
    ↓ (parent for sessions)
SessionContext (Per User)
    ↓ (parent for executions)
ExecutionContext (Per Request)
```

### Rationale

1. **Single source of truth** — No confusion about where state lives
2. **Explicit hierarchy** — Global (engine) → Session (user) → Execution (request)
3. **Serialization enables** — Checkpointing, debugging, recovery
4. **No globals** — Avoids pytest fixture conflicts, enables parallel execution, prevents hidden coupling

### Consequences

| Aspect | Impact |
|--------|--------|
| **Memory usage** | Medium — Multiple context layers consume memory, but scoped to execution |
| **Serialization cost** | Low — JSON/YAML is fast; only persist when needed |
| **Isolation** | High — Concurrent executions cannot interfere |
| **Debugging** | High — Full state available at any point |

---

## 5. Extensibility Strategy

### Decision

Design for **three extensibility vectors**:

1. **New agents** — Register via `AgentRegistry` without modifying core
2. **New skills** — Register via `SkillRegistry` without modifying core
3. **New runtimes** — Runtime supports adapters for CLI, API, UI, etc.

### Extension Points

| Extension Point | Mechanism | Example |
|----------------|-----------|---------|
| New agent | Register in `AgentRegistry` | `registry.register(MyAgent())` |
| New skill | Register in `SkillRegistry` | `registry.register(MySkill())` |
| New runtime | Implement `RuntimeAdapter` | HTTP API adapter |

### Rationale

1. **Registry pattern** — Standard, well-understood mechanism for plugin systems
2. **Interface contracts** — New components must implement known interfaces
3. **No monkey patching** — Extensions integrate through defined points
4. **Future-proofing** — Adapters allow the core to be used in different contexts

### Consequences

| Aspect | Impact |
|--------|--------|
| **Plugin ecosystem** | Enabled — Third parties can extend the system |
| **Discovery** | Required — Registry must support discovery queries |
| **Version compatibility** | Risk — New plugins may depend on specific API versions |
| **Documentation** | Required — Extension API must be well-documented |

---

## 6. Error Handling & Safety

### Decision

Implement **explicit, propagatable error handling**:

- All errors are classified in an **error taxonomy**
- Errors **propagate explicitly** through the context
- **No silent errors** — All failures are logged and reported
- **Recoverable execution** where possible (retry, fallback, refine)

### Error Taxonomy

```
RUNTIME ERROR
├── FATAL (no retry)
│   ├── INVALID_INPUT
│   ├── PERMISSION_DENIED
│   ├── ASSERTION_FAILURE
│   └── VALIDATION_ERROR
├── RETRYABLE (retry with backoff)
│   ├── TIMEOUT
│   ├── TRANSIENT_FAILURE
│   └── RATE_LIMITED
└── WARN (non-blocking)
    ├── PERFORMANCE_WARNING
    ├── QUALITY_WARNING
    └── STYLE_SUGGESTION
```

### Rationale

1. **Explicit error taxonomy** — Enables appropriate handling (retry vs. fail fast vs. warn)
2. **Error propagation via context** — Errors travel with the execution, enabling debugging
3. **No silent failures** — Critical for production reliability; nothing hiding failures
4. **Recoverability** — Enables resilience patterns (retry, fallback, circuit breaker)

### Consequences

| Aspect | Impact |
|--------|--------|
| **Error handling code** | Increased — More cases to handle, but clearer |
| **User experience** | Improved — Better error messages, recovery paths |
| **Debugging** | Improved — Full error context preserved |
| **Complexity** | Medium — Error taxonomy must be maintained |

---

## 7. Non-Goals

### Decision

Explicitly exclude the following:

| Non-Goal | Rationale |
|----------|-----------|
| **Not building a chatbot** | This is an intelligence framework, not a conversational interface. Chat is one possible UI layer. |
| **Not hardcoding domain logic** | The framework is domain-agnostic. Domain logic lives in configurable skills/agents. |
| **Not coupling to a specific LLM** | LLM integration is abstracted. Multiple providers can be plugged in. |
| **Not supporting real-time streaming** | Initial version is request-response. Streaming can be added as an adapter. |
| **Not building a multi-node distributed system** | Single-node focus initially. Distribution is a future enhancement. |

### Rationale

1. **Scope discipline** — Explicit non-goals prevent scope creep
2. **Clear focus** — The team knows what to build and what to defer
3. **Architecture simplification** — Excluded features don't constrain the design

### Consequences

| Aspect | Impact |
|--------|--------|
| **Feature requests** | Clear rejection criteria for out-of-scope items |
| **Architecture simplicity** | Focused design without extraneous concerns |
| **Future roadmap** | Clear items to add later (streaming, distribution) |

---

## 8. Summary of Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Modular layered architecture | Reusability, testability | More interfaces, boilerplate |
| Five core abstractions | Clear responsibility | Learning curve for new developers |
| Intent-driven execution | Flexibility, user-centric | Intent parsing complexity |
| Context hierarchy | Isolation, debuggability | Memory overhead, serialization |
| Registry-based extensibility | Plugin ecosystem | Discovery complexity |
| Explicit error taxonomy | Reliability, debuggability | Error handling code |
| Excluded non-goals | Focused scope | Cannot address out-of-scope requests |

---

## 9. Related Documents

- **Constitution:** `.specify/memory/constitution.md`
- **Intelligence Model:** `specs/core-intelligence-model/spec.md`
- **Skills:** `specs/reusable-cognitive-skills/spec.md`
- **Agents:** `specs/reusable-agents/spec.md`
- **Runtime:** `specs/core-runtime-architecture/spec.md`
- **Context:** `specs/context-memory-system/spec.md`
- **Implementation Plan:** `specs/implementation-plan/plan.md`

---

## 10. Appendix: Module Dependency Rules

To maintain architectural integrity, enforce these dependency rules:

```
# Allowed dependencies (direction of import)
core/          ← (no dependencies, foundation)
    ↓
context/       ← imports: core/
    ↓
skills/        ← imports: core/, context/
    ↓
runtime/       ← imports: core/, context/, skills/
    ↓
agents/        ← imports: core/, context/, skills/, runtime/
    ↓
introspection/ ← imports: core/, context/, skills/, runtime/, agents/
    ↓
llm/           ← imports: core/ (independent layer)
```

**Rule:** No backward dependencies. Always import from lower-numbered layer.

---

**ADR Version:** 1.0.0
**Accepted Date:** 2025-12-29
**Amendments:** None yet
**Next Review:** Before Phase 4 implementation (Agents)

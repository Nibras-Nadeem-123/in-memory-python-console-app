# ADR-002: Technology Stack and Dependency Strategy

> **Scope**: This ADR documents the foundational technology decisions for the in-memory, spec-driven intelligence framework—clustering Python version, dependency strategy, and persistence approach as an integrated stack decision.

- **Status:** Accepted
- **Date:** 2025-12-29
- **Feature:** 005-intelligence-system-impl
- **Context:** Building a reusable intelligence runtime for reasoning, planning, and execution. The framework must be portable, minimal, and easy to deploy without complex environment setup.

## Decision

We adopt a **minimal-dependency, standard-library-first** technology stack:

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Language** | Python 3.9+ | Modern typing (generics, TypedDict), broad compatibility, async support |
| **Dependencies** | Standard Library Only | Zero external deps in core; pytest/ruff/mypy for dev only |
| **Persistence** | In-memory + Optional JSON | Fast default, portable serialization when needed |
| **Testing** | pytest + pytest-cov | Standard Python testing ecosystem |
| **Code Quality** | ruff (lint/format) + mypy (types) | Modern, fast, comprehensive tooling |

### Key Constraints

1. **No runtime external dependencies** — Core intelligence framework uses only stdlib
2. **Dev dependencies are acceptable** — Testing and quality tools are dev-only
3. **JSON for serialization** — No pickle (security), no external formats (portability)
4. **Python 3.9 floor** — Enables TypedDict, Protocol, modern generics without requiring 3.10+

## Consequences

### Positive

- **Zero-dependency deployment** — No pip install failures, no version conflicts, no vendoring
- **Maximum portability** — Works on any Python 3.9+ environment (serverless, containers, bare metal)
- **Predictable behavior** — No third-party surprises; stdlib is stable and well-documented
- **Fast startup** — No import overhead from heavy frameworks
- **Security** — Smaller attack surface; no supply chain risk from dependencies
- **Easy testing** — No complex mocking of external libraries

### Negative

- **More code to write** — Can't leverage existing frameworks (LangChain, etc.)
- **No async/await by default** — Stdlib asyncio requires manual integration
- **JSON limitations** — No native datetime, must handle serialization manually
- **Reinventing patterns** — Registry, DI, etc. must be hand-rolled
- **Python 3.9 constraints** — No match statements (3.10), no TypeVarTuple (3.11)

## Alternatives Considered

### Alternative A: Framework-Based Stack
- **Components:** LangChain + Redis + SQLAlchemy
- **Pros:** Rich features, battle-tested, community support
- **Cons:** Heavy dependencies, version churn, vendor lock-in, complex debugging
- **Rejected:** Conflicts with reusability principle; creates external coupling

### Alternative B: Modern Python Stack
- **Components:** Python 3.11+ + pydantic + SQLite
- **Pros:** Better typing, built-in validation, persistent storage
- **Cons:** Requires newer Python, adds pydantic dependency, SQLite complexity
- **Rejected:** 3.11 adoption not universal; pydantic is a heavy dependency

### Alternative C: Hybrid Approach
- **Components:** Python 3.9 + optional extras (e.g., pydantic as optional)
- **Pros:** Flexibility for users who want richer features
- **Cons:** Complexity in maintaining two code paths, testing burden
- **Deferred:** Could be added later via adapter pattern without core changes

## References

- Feature Spec: `specs/005-intelligence-system-impl/spec.md`
- Implementation Plan: `specs/005-intelligence-system-impl/plan.md`
- Related ADRs: ADR-001 (Intelligence Runtime Architecture)
- Constitution: `.specify/memory/constitution.md` (Principle III: Domain-Agnostic & Modular)

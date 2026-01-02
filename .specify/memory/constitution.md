<!--
Sync Impact Report:
- Version change: 1.1.0 → 1.2.0
- Modified principles: VI. Frozen Intelligence Architecture - enhanced with explicit rules.
- Added sections: None.
- Removed sections: None.
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md
  - ✅ .specify/templates/spec-template.md
  - ✅ .specify/templates/tasks-template.md
  - ⚠ .claude/commands/*.md (Manual check for agent-specific names recommended)
  - ✅ README.md
- Follow-up TODOs: None.
-->
# Reusable Intelligence Framework Constitution

## Core Principles

### I. Reusable Intelligence Framework
The primary goal is to build a framework for reusable intelligence, not a single-purpose application. All components, from skills to agents, MUST be designed for broad applicability and reusability over one-off logic.

### II. Intelligence-First Design
Prioritize reasoning, planning, and adaptability over raw execution. The system MUST understand "why" a task is being performed before executing "how," clearly separating the planning/reasoning layer from the execution layer.

### III. Domain-Agnostic & Modular Architecture
The framework's core design and concepts MUST be language-agnostic and contain no hardcoded, domain-specific logic. The architecture MUST be composed of clear, modular, and composable components (e.g., skills, agents, tools) with well-defined interfaces.

### IV. Skill-Based Functionality
All functional capabilities MUST be developed as discrete, independently testable "skills." Skills are the fundamental, reusable building blocks of all system functionality, not monolithic features.

### V. Safety and Introspectability
The framework MUST enforce safe execution environments and provide deep introspectability. The system's state, reasoning process, and execution history must be transparent, auditable, and easy to debug.

### VI. Frozen Intelligence Architecture

The core intelligence layer is considered **stable, frozen, and reusable**. This section codifies the rules governing its maintenance and evolution.

#### Frozen Components (v1.0.0)

The following modules constitute the frozen intelligence layer:

| Module | Path | Purpose |
|--------|------|---------|
| Context System | `src/intelligence/context.py` | State management, history, persistence |
| Skills Interface | `src/intelligence/skills/skill_interface.py` | Skill ABC, types, exceptions |
| Skill Registry | `src/intelligence/skills/skill_registry.py` | Skill registration and discovery |
| Runtime Engine | `src/intelligence/runtime.py` | Plan execution, agent routing |
| Intelligence Engine | `src/intelligence/engine.py` | Goal-to-outcome transformation |

#### Rules for Frozen Layer

1. **Extension, Not Modification**: Future projects MAY extend the framework through:
   - New skills implementing the `Skill` interface
   - New agents implementing the `Agent` interface
   - Custom intent parsers via composition
   - Wrapper classes adding domain-specific logic

2. **Core Logic Protection**: Projects MUST NOT:
   - Modify the core logic of frozen modules
   - Change method signatures in abstract base classes
   - Alter exception hierarchies
   - Remove or rename public API exports

3. **Explicit Versioning**: Any change to frozen modules requires:
   - Semantic versioning bump (major for breaking, minor for additions)
   - ADR documenting the rationale
   - Migration guide for downstream consumers
   - Updated test coverage for changes

4. **Stability Guarantee**: The intelligence layer is designed to be:
   - Reusable across multiple projects
   - Stable for long-term maintenance
   - Backward-compatible within major versions

#### Permitted Changes

| Change Type | Allowed | Process Required |
|-------------|---------|------------------|
| Add new skills | Yes | None |
| Add new agents | Yes | None |
| Bug fixes in frozen modules | Yes | Patch version bump |
| New optional parameters | Yes | Minor version bump + ADR |
| Breaking interface changes | No | Major version bump + ADR + Migration |
| Performance optimizations | Yes | Patch/minor version bump |
| Documentation updates | Yes | None |

## Development Workflow

### Spec-Driven Development
All new features or significant changes MUST begin with a specification (`spec.md`). The spec defines the "what" and "why" and must be approved before planning or implementation begins.

### Test-Driven Development (TDD)
TDD is mandatory. For any new skill or component, failing tests MUST be written and approved before the implementation code is created, following a strict Red-Green-Refactor cycle.

## Governance

This Constitution is the single source of truth for all architectural and development principles. It supersedes all other practices and documents.

- **Compliance**: All code reviews and architectural decisions MUST verify compliance with these principles. Any deviation requires a formal exception process documented in an ADR (Architecture Decision Record).
- **Amendments**: Changes to this Constitution require a proposal, review, and a documented migration plan if the changes are backward-incompatible.
- **Guidance**: Use this document as the primary guidance for all runtime development activities.

**Version**: 1.2.0 | **Ratified**: 2025-12-28 | **Last Amended**: 2025-12-29

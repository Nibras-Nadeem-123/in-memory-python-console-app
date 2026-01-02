---
id: '001'
title: 'define-skill-registry'
stage: 'spec'
date: '2025-12-28'
surface: 'agent'
model: 'claude-sonnet-4-5-20250929'
feature: 'skill-registry'
branch: 'main'
user: 'Claude Code User'
command: '/sp.specify'
labels: ['skill-registry,registration,invocation,validation,composition,dependencies']
links:
  spec: 'null'
  ticket: 'null'
  adr: 'null'
  pr: 'null'
files:
  - 'specs/skill-registry/spec.md'
tests:
  - 'none'
---

## Prompt

/sp.specify
Define a Skill Registry system.

Requirements:
- Skills registered with unique names
- Skills declare inputs and outputs
- Skills are stateless
- Skills can be composed

Define:
- Registration mechanism
- Invocation interface
- Validation rules

## Response snapshot

Created `specs/skill-registry/spec.md` with complete Skill Registry System:

**Skill Definition**:
- `Skill` abstract base class with `execute(context)` as primary method
- `SkillMetadata`: name, category, version, inputs, outputs, dependencies, capabilities
- `SkillCategory`: PARSING, GENERATION, ANALYSIS, TRANSFORMATION, REASONING, VALIDATION, ORCHESTRATION, MEMORY, EVALUATION
- `SkillStatus`: EXPERIMENTAL, STABLE, DEPRECATED, REMOVED
- Stateless execution via SkillContext (no internal state between invocations)

**Skill Context**:
- `SkillContext`: Input values, shared context, injected dependencies, metrics
- `get_input(name, default)`, `get_shared(key)`, `require_input(name)`, `get_dependency(name)`

**Registration Mechanism**:
- `SkillRegistry`: Central catalog with register, unregister, get, find_by_* methods
- Capability index, tag index for fast discovery
- `register_batch` for bulk registration
- `resolve_dependencies` for dependency injection
- `validate_dependencies` for pre-execution validation
- Version management with deprecation support

**Invocation Interface**:
- `SkillInvoker`: Executes skills with validation and error handling
- `invoke(skill_name, inputs, config, shared_context)` with validation
- `invoke_with_version` for specific version
- `invoke_chain` for linear chaining
- `validate_input/output` against schemas

**Validation Rules**:
- Registration validation: metadata, name format, semver, input/output schema
- Schema compatibility: producer output ↔ consumer input type matching
- Invocation validation: required inputs, type checking, custom rules
- Access validation: capability and tag-based filtering

**Composition**:
- `SkillComposer`: Linear chaining, parallel execution, fan-out/fan-in patterns
- `ComposedSkill`: Wraps multiple skills with combined metadata
- Dependency injection via set_dependency/get_dependency

**Key Features**:
- 50ms registration, 5ms lookup, <1ms invocation overhead
- 1000+ skills supported
- Thread-safe operations
- Metrics tracking per skill
- Version compatibility checking (major version must match)

## Outcome

- ✅ Impact: Defined complete Skill Registry with registration, discovery, invocation, validation, and composition
- 📁 Files: 1 created (specs/skill-registry/spec.md)
- 🔁 Next prompts: Run `/sp.plan` for registry implementation, `/sp.tasks` for task breakdown
- 🧠 Reflection: Registry enables pluggable skills; composition enables complex workflows; validation ensures type safety across skill chains

## Evaluation notes (flywheel)

- Failure modes observed: 'none'
- Graders run and results (PASS/FAIL): 'N/A'
- Prompt variant (if applicable): 'N/A'
- Next experiment (smallest change to try): 'N/A'

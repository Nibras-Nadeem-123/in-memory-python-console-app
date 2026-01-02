# Tasks: Spec-Driven Development System

**Input**: Design documents from `/specs/005-intelligence-system-impl/`
**Prerequisites**: plan.md, spec.md

**Organization**: Tasks are grouped by component to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (SDD1, SDD2, SDD3)
- Include exact file paths in descriptions

## Path Conventions

- **Source**: `src/intelligence/`
- **SDD Agents**: `src/intelligence/sdd/`
- **Tests**: `tests/unit/intelligence/`, `tests/integration/`

---

## Phase 1: Setup (Project Infrastructure)

**Purpose**: Project initialization and package structure

- [X] T001 [P] Create SDD agents directory structure at src/intelligence/sdd/__init__.py
- [X] T002 [P] Create test package structure at tests/unit/intelligence/__init__.py
- [X] T003 [P] Create integration test structure at tests/integration/__init__.py
- [X] T004 [P] Update pyproject.toml with test configurations for new modules

**Checkpoint**: Package structure ready - SDD component implementation can begin

---

## Phase 2: Core Infrastructure

**Purpose**: Foundation that all components depend on

- [X] T005 Create data model definitions at src/intelligence/sdd/data_models.py
  - Intent, Spec, Plan, Task, Artifact, Decision dataclasses
- [X] T006 [P] Implement SDD context container in src/intelligence/sdd/context.py
  - Extends ExecutionContext with SDD-specific fields (intent, artifacts)
- [X] T007 [P] Implement base agent interface at src/intelligence/sdd/agent_base.py
  - Agent ABC with name, can_handle, execute methods
- [X] T008 [P] Add logging and debugging utilities in src/intelligence/sdd/utils.py
  - Structured logging, error formatting, context helpers
- [X] T009 [P] Update src/intelligence/__init__.py to export SDD components

**Checkpoint**: Foundation ready - agent implementation can begin

---

## Phase 3: Agent System

**Purpose**: Implement SDD stage agents

### Stage 1: Intent Parsing (Clarification)

- [X] T010 [SDD1] Implement IntentAgent in src/intelligence/sdd/intent_agent.py
  - Parse natural language into Intent object
  - Extract confidence score and metadata
- [X] T011 [SDD1] Add intent parsing skill in src/intelligence/sdd/skills/intent_parsing_skill.py
  - Skill: IntentType classification, entity extraction
- [X] T012 [SDD1] Add ambiguity detection skill in src/intelligence/sdd/skills/ambiguity_detection.py
  - Skill: Identify unclear phrases requiring clarification
- [X] T013 [SDD1] Test IntentAgent in tests/unit/intelligence/test_intent_agent.py
  - Test parsing, confidence thresholds, metadata extraction

**Checkpoint**: IntentAgent ready - specification generation can begin

### Stage 2: Specification Generation

- [X] T014 [SDD2] Implement SpecAgent in src/intelligence/sdd/spec_agent.py
  - Generate spec.md from Intent object
  - Use template-based generation with required sections
- [X] T015 [SDD2] Create spec template in src/intelligence/sdd/templates/spec_template.md
  - Markdown template with Overview, Requirements, Acceptance Criteria sections
- [X] T016 [SDD2] Add requirement elicitation skill in src/intelligence/sdd/skills/requirement_extraction.py
  - Skill: Extract requirements from parsed intent
- [X] T017 [SDD2] Test SpecAgent in tests/unit/intelligence/test_spec_agent.py
  - Test spec generation, template application, validation

**Checkpoint**: SpecAgent ready - planning can begin

### Stage 3: Planning

- [X] T018 [SDD3] Implement PlanAgent in src/intelligence/sdd/plan_agent.py
  - Generate plan.md from spec.md
  - Decompose requirements into tasks
  - Identify dependencies and sequence
- [X] T019 [SDD3] Add task decomposition skill in src/intelligence/sdd/skills/task_breakdown.py
  - Skill: Break spec into actionable tasks with estimates
- [X] T020 [SDD3] Add dependency resolution skill in src/intelligence/sdd/skills/dependency_resolution.py
  - Skill: Identify task prerequisites and ordering
- [X] T021 [SDD3] Test PlanAgent in tests/unit/intelligence/test_plan_agent.py
  - Test plan generation, task breakdown, dependencies

**Checkpoint**: PlanAgent ready - guidance generation can begin

### Stage 4: Execution Guidance

- [X] T022 [SDD4] Implement GuideAgent in src/intelligence/sdd/guide_agent.py
  - Generate guide.md from plan.md
  - Provide code scaffolding templates
  - Suggest best practices for language/framework
- [X] T023 [SDD4] Add scaffolding skill in src/intelligence/sdd/skills/code_scaffolding.py
  - Skill: Generate project structure, base files, patterns
- [X] T024 [SDD4] Add best practices lookup skill in src/intelligence/sdd/skills/best_practices.py
  - Skill: Return language/framework-specific patterns and conventions
- [X] T025 [SDD4] Test GuideAgent in tests/unit/intelligence/test_guide_agent.py
  - Test guide generation, scaffolding output, pattern application

**Checkpoint**: All agents implemented - integration can begin

---

## Phase 4: Integration & Orchestration

**Purpose**: Connect agents into working system

- [X] T026 Implement SDD Engine in src/intelligence/sdd/engine.py
  - Orchestrate all agents in sequence
  - Handle stage transitions and errors
  - Manage agent registry for routing
- [X] T027 Update RuntimeEngine to support SDD agents in src/intelligence/main.py
  - Add SDD CLI command routing
  - Route requests to appropriate agents
- [X] T028 [P] Create workflow manager in src/intelligence/sdd/workflow_manager.py
  - Coordinate multi-stage execution
  - Handle human intervention points
  - Manage checkpoints and resumption
- [X] T029 Add error handling for SDD stages in src/intelligence/sdd/sdd_errors.py
  - Custom exceptions for parsing, generation, planning errors
- [X] T030 Update AgentRegistry in src/intelligence/sdd/__init__.py
  - Register SDD agents as discoverable components
- [X] T031 [P] Update src/intelligence/sdd/__init__.py to export all agents

**Checkpoint**: SDD system integrated - ready for testing

---

## Phase 5: Skill System Extensions

**Purpose**: Add SDD-specific skills to skill registry

- [X] T032 Register SDD skills in SYSTEM_SKILL_REGISTRY in src/intelligence/sdd/__init__.py
  - Auto-register intent parsing, requirement extraction, task breakdown skills
- [X] T033 Add skill composition utilities in src/intelligence/sdd/skill_composition.py
  - Combine multiple skills in sequence
  - Handle skill chaining and output passing
- [X] T034 [P] Test skill composition in tests/unit/intelligence/test_skill_composition.py
  - Test skill chaining, error propagation, output validation

**Checkpoint**: Skill system complete - all SDD capabilities available

---

## Phase 6: CLI Integration

**Purpose**: User interface for SDD system

- [X] T035 Add SDD CLI commands in src/intelligence/sdd/cli.py
  - parse-spec, generate-plan, generate-guide commands
  - Add help text for all SDD commands
- [X] T036 Update main.py to register SDD commands in src/intelligence/main.py
  - Wire SDD CLI into main entry point
  - Add example workflows demonstrating SDD pipeline
- [X] T037 [P] Add quickstart documentation in specs/005-intelligence-system-impl/quickstart.md
  - Step-by-step guide for using SDD system
  - Example from intent to final artifacts
- [X] T038 [P] Update README.md with SDD section in README.md
  - Document SDD system capabilities and usage

**Checkpoint**: User interface complete - ready for use

---

## Phase 7: Testing & Validation

**Purpose**: Validate SDD system functionality

- [X] T039 Test IntentAgent in tests/unit/intelligence/test_intent_agent.py
- [X] T040 Test SpecAgent in tests/unit/intelligence/test_spec_agent.py
- [X] T041 Test PlanAgent in tests/unit/intelligence/test_plan_agent.py
- [X] T042 Test GuideAgent in tests/unit/intelligence/test_guide_agent.py
- [X] T043 Test skill composition in tests/unit/intelligence/test_skill_composition.py
- [X] T044 Test SDD workflow in tests/integration/test_sdd_workflow.py
  - End-to-end test: intent → spec → plan → guide
  - Validate artifacts produced at each stage
- [X] T045 Run pytest tests with coverage in tests/unit/intelligence/
- [X] T046 Verify test coverage meets threshold (>80%)

**Checkpoint**: All tests passing - system validated

---

## Phase 8: Documentation & Polish

**Purpose**: Finalize documentation and quality checks

- [X] T047 Update SDD documentation in specs/005-intelligence-system-impl/data-model.md
  - Document Intent, Spec, Plan, Artifact entities
- [X] T048 Add architecture documentation in specs/005-intelligence-system-impl/architecture.md
  - Agent composition, data flow, component interactions
- [X] T049 [P] Run ruff linting on src/intelligence/sdd/
- [X] T050 [P] Run mypy type checking on src/intelligence/sdd/
- [X] T051 Add inline docstrings to all public APIs in src/intelligence/sdd/
- [X] T052 Create PHR for SDD implementation

**Checkpoint**: SDD system complete and documented

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Core Infrastructure (Phase 2)**: Depends on Setup - BLOCKS all agent work
- **Agent System (Phase 3)**: Depends on Core Infrastructure
- **Integration (Phase 4)**: Depends on Agent System completion
- **Skill Extensions (Phase 5)**: Depends on Integration completion
- **CLI (Phase 6)**: Depends on Skill Extensions
- **Testing (Phase 7)**: Depends on CLI completion
- **Documentation (Phase 8)**: Depends on Testing completion

### Parallel Opportunities

**Phase 1 (Setup):**
- T001, T002, T003, T004 can run in parallel

**Phase 2 (Core):**
- T005, T006, T007, T008, T009 can run in parallel

**Phase 3 (IntentAgent):**
- T010, T011, T012 can run in parallel

**Phase 3 (SpecAgent):**
- T014, T015, T016 can run in parallel

**Phase 3 (PlanAgent):**
- T018, T019, T020 can run in parallel

**Phase 3 (GuideAgent):**
- T022, T023, T024 can run in parallel

**Phase 6 (CLI):**
- T035, T037 can run in parallel

**Phase 7 (Testing):**
- All test tasks can run in parallel after implementation

### Within Each Phase

- Tests must be written and FAIL before implementation
- Implementation tasks follow dependency order within phase
- Phase complete before moving to dependent phase

---

## Summary

| Phase | Tasks | Tests | Parallel Tasks |
|-------|-------|-------|----------------|
| 1: Setup | 4 | 0 | 4 |
| 2: Core Infrastructure | 5 | 0 | 4 |
| 3: Agent System | 16 | 4 | 6 |
| 4: Integration | 6 | 0 | 0 |
| 5: Skills | 4 | 1 | 2 |
| 6: CLI | 4 | 0 | 2 |
| 7: Testing | 8 | 1 | 8 |
| 8: Documentation | 6 | 0 | 3 |
| **Total** | **53** | **6** | **29** |

---

## Implementation Strategy

### MVP First (Phase 1-3 + Setup)

1. Complete Phase 1: Setup
2. Complete Phase 2: Core Infrastructure
3. Complete Phase 3: IntentAgent only
4. **STOP and VALIDATE**: Test intent parsing → spec generation flow
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup → Core Infrastructure → All Agents
2. Integrate agents into SDD Engine
3. Add CLI interface
4. Add tests incrementally
5. Polish documentation

### Testing Strategy

- Write tests BEFORE implementation for each component
- Unit tests for individual agents and skills
- Integration test for full SDD workflow
- Aim for >80% coverage on SDD modules

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to SDD user story (SDD1, SDD2, SDD3, SDD4)
- Each phase should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate component independently
- Avoid: vague tasks, same file conflicts, cross-phase dependencies that break independence

---
id: '004'
title: 'freeze-intelligence-layer'
stage: 'constitution'
date: '2025-12-28'
surface: 'agent'
model: 'claude-sonnet-4-5-20250929'
feature: 'none'
branch: 'main'
user: 'Claude Code User'
command: '/sp.constitution'
labels: 'intelligence-layer,freeze,stable,permanent,constitution'
links:
  spec: 'null'
  ticket: 'null'
  adr: 'null'
  pr: 'null'
files:
  - '.specify/memory/constitution.md'
tests:
  - 'none'
---

## Prompt

/sp.constitution
Freeze the intelligence layer as stable.
All future projects must build on top of it without modification.

## Response snapshot

Added Section XV to constitution:

**Frozen Intelligence Layer Declaration**:
- Status: FROZEN / STABLE
- Effective: 2025-12-28
- 8 frozen artifacts listed with locations

**Core Rules**:
- Core principles (XI.A-XI.E): CANNOT be modified, reinterpreted, or superseded
- Artifact standards (XII): CANNOT be changed without deprecation path
- Governance rules (XIII-XIV): CANNOT be altered without unanimous committee approval

**Extension Over Modification**:
- All future capabilities MUST be extensions, not modifications
- Project-specific extensions go in `intelligence/extensions/`
- Example pattern provided for extending vs modifying

**Breaking Changes Prohibited**:
- Removing/renaming skills, templates, agents, interfaces
- Changing input/output schemas
- Altering validation rules
- Modifying agent responsibilities
- Adding required parameters

**Exception Process** (Requires Unanimous Approval):
- Unanimous committee vote
- Full impact assessment
- Migration plan required
- 6-month minimum deprecation
- Major version bump

**Project Compliance**:
- Compliance check class defined
- 4 verification checks
- Migration path for existing projects (9 weeks)

**Committee**: Intelligence Layer Architecture Committee (Claude Code + human architect)

## Outcome

- ✅ Impact: Frozen intelligence layer as permanent, immutable foundation for all projects
- 📁 Files: 1 modified (.specify/memory/constitution.md)
- 🔁 Next prompts: Run `/sp.adr intelligence-layer-governance` for committee rules
- 🧠 Reflection: Frozen layer provides stability; extension pattern enables evolution without modification

## Evaluation notes (flywheel)

- Failure modes observed: 'none'
- Graders run and results (PASS/FAIL): 'N/A'
- Prompt variant (if applicable): 'N/A'
- Next experiment (smallest change to try): 'N/A'

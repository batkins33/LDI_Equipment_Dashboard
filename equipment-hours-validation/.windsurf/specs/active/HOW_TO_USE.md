# How to Use Build Specs for DocTR_Process

This guide explains how to execute the Track B architecture phases using the build spec workflow.

## Quick Start

To execute a phase:

1. **Copy the phase start prompt:**
   ```
   Start Phase 2: Entrypoint Drift Fix.
   
   Follow execute-spec.md Step 2 exactly:
   
   1) Announce the phase (goal + acceptance criteria).
   2) Read every file listed in `reads` before editing anything.
   3) Execute tasks in order. After each task, run the task's `testing` commands.
   4) After all tasks, run EVERY command in the phase `verify` list.
   5) Post the Phase End Report and ask: "Proceed to Phase 3?"
   ```

2. **Paste into Windsurf chat** and let the agent execute

3. **Review Phase End Report** when agent completes

4. **Approve or request changes** before proceeding to next phase

---

## Phase Execution Order

**Recommended sequence:**

```
Phase 1: Track B Docker Parity ✅ COMPLETE
    ↓
Phase 2: Entrypoint Drift Fix (1-2 hours)
    ↓
Phase 3: CI Guards (3-5 hours)
    ↓
Phase 4: Adapter Design (1-2 days, design only)
```

**Can run in parallel:**
- Phase 2 and Phase 3 are independent (can do either first)
- Phase 4 requires Phase 3 complete

---

## Workflow Files Reference

### Core Workflow
- **`execute-spec.md`** - Master workflow definition
  - Defines how to parse and execute build specs
  - Includes Git commit policy
  - Includes UI verification requirements
  - Includes Phase End Report template

### Phase Templates
- **`PHASE_START_PROMPT.md`** - Standard prompt for starting any phase
  - Copy/paste template with phase number filled in
  - Ensures consistent execution across phases
  
- **`PHASE_END_PROMPT.md`** - Standard prompt for completing any phase
  - Verification checklist
  - Documentation requirements
  - Archive process
  - Commit guidelines

### Specialized Workflows
- **`ui-debug-playwright.md`** - UI testing with Playwright (not needed for Track B phases)

---

## Build Spec Format

Each phase YAML file contains:

```yaml
project: DocTR_Process
phase_number: N
phase_name: "Phase Name"
description: "What this phase accomplishes"
context: "Background and dependencies"

reads:
  - "Files to read for context before editing"

phases:
  - name: "Phase N — Name"
    tasks:
      - task_id: "unique-id"
        name: "Task name"
        description: "What the task does"
        acceptance_criteria:
          - "Condition that must be true"
        implementation_notes: "How to implement"
        documentation:
          - "Docs to update"
        testing:
          - "Commands to run after task"
        files_to_modify:
          - "Files this task changes"
    
    verify:
      - "Phase-level verification commands"
    
    done_when: "Conditions for phase completion"

follow_up:
  - "Future work items"
```

---

## Verification Requirements

After each phase, the agent MUST:

1. **Run all verify commands** and paste full output
2. **Check acceptance criteria** - all must be met
3. **Update documentation** as specified in tasks
4. **Create Phase End Report** using template
5. **Commit changes** with standardized message
6. **Archive build spec** to `.windsurf/specs/archived/`
7. **Wait for approval** before proceeding

---

## Git Workflow

Each phase follows this Git pattern:

```bash
# 1. Create branch (if not already on one)
git checkout -b phase-N-short-name

# 2. Make changes (agent does this)

# 3. Verify (agent runs all verify commands)

# 4. Commit (agent does this after verification passes)
git add .
git commit -m "DocTR_Process: Phase N — Phase Name

<summary>

Changes:
- file1
- file2

Verification:
- All verify commands passed
- Phase End Report: docs/dev/PHASE_N_COMPLETION_REPORT.md"

# 5. Push (agent does this)
git push origin phase-N-short-name

# 6. Archive spec (agent does this)
mv .windsurf/specs/active/PHASE_N_*.yaml \
   .windsurf/specs/archived/PHASE_N_*_completed_$(date +%Y-%m-%d).yaml
```

---

## Customizations for DocTR_Process

The workflow files are generic but work for DocTR_Process with these notes:

### Not Applicable
- **DOCUMENTATION_INDEX.md** - DocTR doesn't use this (skip this requirement)
- **WORKSPACE.yaml** - DocTR doesn't use this (skip this requirement)
- **Coaching patterns** - DocTR doesn't use this (skip this requirement)
- **Policy rule IDs** - DocTR doesn't use this (skip this requirement)

### Applicable
- **CHANGELOG.md** - Update for user-facing changes
- **Git commit policy** - Follow exactly as specified
- **Phase End Report** - Required for all phases
- **Verify commands** - Must all pass before completion
- **Documentation updates** - Required as specified in tasks

---

## Example: Running Phase 2

1. **Start the phase:**
   ```
   Start Phase 2: Entrypoint Drift Fix.
   
   Follow execute-spec.md Step 2 exactly:
   
   1) Announce the phase (goal + acceptance criteria).
   2) Read every file listed in `reads` before editing anything.
   3) Execute tasks in order. After each task, run the task's `testing` commands.
   4) After all tasks, run EVERY command in the phase `verify` list.
   5) Post the Phase End Report and ask: "Proceed to Phase 3?"
   ```

2. **Agent will:**
   - Read: `pyproject.toml`, `gui.py`, `gui_unified.py`, `web/app.py`, `web/app_clean.py`, `launcher.bat`
   - Execute 4 tasks in order
   - Run testing commands after each task
   - Run all verify commands
   - Create Phase End Report

3. **You review:**
   - Check Phase End Report
   - Verify all acceptance criteria met
   - Review git diff
   - Test console scripts manually if desired

4. **You approve:**
   - Reply: "Approved, proceed to Phase 3"
   - Or: "Hold, I need to review X"

---

## Troubleshooting

**If a verify command fails:**
- Agent MUST stop and report failure
- Do NOT proceed to next phase
- Fix the issue, re-run verify
- Only proceed when all verify commands pass

**If acceptance criteria not met:**
- Agent MUST report which criteria failed
- Do NOT mark phase complete
- Fix the issue, verify again

**If documentation is incomplete:**
- Agent MUST complete all docs in task `documentation` fields
- Do NOT defer documentation to later
- Phase cannot be marked complete until docs are done

---

## See Also

- **Architecture Decision:** `artifacts/reports/ARCHITECTURE_DECISION_RECOMMENDATION.md`
- **Track B Report:** `artifacts/reports/TRACK_B_IMPLEMENTATION_REPORT.md`
- **Workflow Master:** `.windsurf/workflows/execute-spec.md`
- **Phase Templates:** `.windsurf/workflows/PHASE_START_PROMPT.md`, `PHASE_END_PROMPT.md`

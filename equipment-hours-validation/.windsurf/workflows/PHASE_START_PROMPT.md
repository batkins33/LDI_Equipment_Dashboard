---
title: LDI Equipment Dashboard Phase Start Prompt
description: Customized prompt for starting phase execution in LDI Equipment Dashboard build spec workflow
status: active
created: 2026-03-01
customized_for: LDI_Equipment_Dashboard
---

# LDI Equipment Dashboard Phase Start Prompt

Use this prompt template when starting any phase execution in LDI Equipment Dashboard. Copy/paste and fill in the phase number and name from the active build spec.

---

## Template

```text
Start Phase <N>: <PHASE NAME>.

Follow execute-spec.md Step 2 exactly:

1) Announce the phase (goal + acceptance criteria).

2) Read every file listed in `reads` before editing anything.

3) Execute tasks in order. After each task, run the task's `testing` commands and paste full stdout + exit code.

4) After all tasks, run EVERY command in the phase `verify` list exactly as written; paste full stdout + exit codes.
   - If any verify step fails: STOP, report failure, and do not proceed.

5) Post the Phase End Report and ask: "Proceed to Phase <N+1>: <NAME>?" and wait for approval.

---

UI Verify Policy:

Any verify line labeled Manual/UI (or otherwise a UI verify step per the workflow classification rule in execute-spec.md) must be satisfied per the UI Verification Requirement section:
- either Playwright/Puppeteer automation with artifacts (≥2 screenshots: landing + target page + 1 interaction screenshot), OR
- a guided checklist (≤12 steps) where you record my PASS/FAIL per step.

Code inspection alone is not acceptable.

---

DocTR_Process requirements:

- Update CHANGELOG.md if user-facing changes are made.
- Update docs/ as specified in task `documentation` fields.
- Follow git commit policy: one commit per phase with standardized message format.
- Archive completed spec to .windsurf/specs/archived/ with completion date.

---

Output policy: no narration. Only actions, commands+stdout, diffs, and the Phase End Report.
```

---

## How to Use

1. Copy the template above
2. Replace `<N>` with phase number (e.g., "2", "3", "4", "5")
3. Replace `<PHASE NAME>` with phase name from build spec (see examples below)
4. Replace `<N+1>` and `<NAME>` in step 5 with the next phase number and name
5. Paste into the Windsurf chat when starting phase execution

---

## Active Phases for LDI Equipment Dashboard

### Unified Ops Dashboard (Mock MVP)

**Phase 1:** UI Screens Implementation

- Next: Phase 2

**Phase 2:** Database Persistence Integration

- Next: Phase 3

**Phase 3:** Real API Connectors

- Next: (Production readiness review)

### Equipment Hours Validation

**Phase P0:** Repo, DB, and Config Loader Setup

- Next: Phase P1

**Phase P1:** Connectors and Bronze Store

- Next: Phase P2

**Phase P2:** Silver Normalization and Crosswalk Mapping

- Next: Phase P3

**Phase P3:** Gold Reconciliation, Flags, and Exceptions

- Next: Phase P4

**Phase P4:** Scheduling, Backfill, and Health Checks

- Next: Phase P5

**Phase P5:** Dashboard Views, Runbooks, and UAT

- Next: (Production readiness review)

---

## Example: Starting Phase P1

```text
Start Phase P1: Connectors and Bronze Store.

Follow execute-spec.md Step 2 exactly:

1) Announce the phase (goal + acceptance criteria).

2) Read every file listed in `reads` before editing anything.

3) Execute tasks in order. After each task, run the task's `testing` commands and paste full stdout + exit code.

4) After all tasks, run EVERY command in the phase `verify` list exactly as written; paste full stdout + exit codes.
   - If any verify step fails: STOP, report failure, and do not proceed.

5) Post the Phase End Report and ask: "Proceed to Phase P2: Silver Normalization and Crosswalk Mapping?" and wait for approval.

---

UI Verify Policy:

Any verify line labeled Manual/UI (or otherwise a UI verify step per the workflow classification rule in execute-spec.md) must be satisfied per the UI Verification Requirement section:
- either Playwright/Puppeteer automation with artifacts (≥2 screenshots: landing + target page + 1 interaction screenshot), OR
- a guided checklist (≤12 steps) where you record my PASS/FAIL per step.

Code inspection alone is not acceptable.

---

LDI Equipment Dashboard requirements:

- Update README.md or relevant docs if user-facing changes are made.
- Update docs/ as specified in task `documentation` fields.
- Follow git commit policy: one commit per phase with standardized message format.
- Archive completed spec to .windsurf/specs/archived/ with completion date.

---

Output policy: no narration. Only actions, commands+stdout, diffs, and the Phase End Report.
```

---

## Key Points

- **Step 2 reference:** Points agent to execute-spec.md workflow (single source of truth)
- **UI Verify Policy:** Explicit, non-negotiable, with concrete artifact requirements (≥3 screenshots)
- **LDI Equipment Dashboard requirements:** Specific to this repo (README.md updates, git policy, spec archival)
- **Output policy:** No fluff, just actions and reports
- **Classification rule:** References execute-spec.md so agent knows what counts as "UI verify step"

---

## See Also

- `.windsurf/workflows/execute-spec.md` — Master workflow (Step 2 + UI Verification Requirement)
- `.windsurf/specs/active/README.md` — Guide to build specs and execution order
- `.windsurf/specs/active/PHASE_P0_REPO_DB_CONFIG.yaml` — Equipment Hours Validation Phase P0
- `.windsurf/specs/active/PHASE_1_UNIFIED_OPS_UI_SCREENS.yaml` — Unified Ops Dashboard Phase 1
- `.windsurf/specs/archived/` — Completed build specs

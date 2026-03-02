---
title: LDI Equipment Dashboard Phase End Prompt
description: Customized prompt for completing any phase execution in LDI Equipment Dashboard build spec workflow
status: active
created: 2026-03-01
customized_for: LDI_Equipment_Dashboard
---

# Phase End Template

Use this prompt template when completing any phase execution in LDI Equipment Dashboard.
Copy/paste and fill in the phase number and name from the active build spec.

---

## Template

```text
Phase <N>: <PHASE NAME> — Completion Checklist

Follow execute-spec.md Step 2.4-2.6 exactly:

1) Run ALL phase verify commands (paste full output + exit codes).
   - If any verify fails: STOP, report failure, do not mark phase complete.

2) Complete documentation requirements:
   - Update README.md if docs were added/modified/removed
   - Update relevant docs/ files as specified in task "documentation" fields
   - Complete any docs listed in task "documentation" fields
   - Verify all doc links are valid

3) Post the Phase End Report using the template from execute-spec.md:

   - Status (✅/⚠️/❌)
   - Phase Scope (what was done vs. spec)
   - Reads Confirmed (list files read)
   - Changes Made (git diff --stat + file list)
   - Verification (all verify command outputs)
   - Behavioral Impact (user/CI/dev changes)
   - Documentation (files touched + needed)
   - Risks & Rollback plan
   - Deferred Items (if any)

4) Commit all changes (follow Git Commit Policy in execute-spec.md):

   - Stage all files: `git add .`
   - Verify with `git status` (only expected changes)
   - Commit with standardized message format: `<project>: Phase <N> — <PHASE NAME>`
   - Include summary, file list, and verification statement in commit body
   - Paste commit SHA into Phase End Report (section 0, "Commit(s)" field)

5) Push the dev branch to remote:

   - `git push origin phase-<N>-<short-name>` (pushes current branch)
   - Verify push succeeded: `git log --oneline -1` should show your commit
   - Branch is now backed up on remote and ready for PR/merge review

6) Archive this phase build spec:

   - Move .windsurf/specs/active/PHASE_<N>_<NAME>.yaml to
   - .windsurf/specs/archived/PHASE_<N>_<NAME>_completed_<YYYY-MM-DD>.yaml
   
   **IMPORTANT:** Archive the INDIVIDUAL phase spec file, NOT the master spec.
   The master layered reorganization spec should remain in archived/ as reference.

7) Create phase completion report:

   - docs/dev/PHASE_<N>_COMPLETION_REPORT.md
   - Include: scope, changes, test results, known issues, next steps

8) Ask for approval: "Phase <N> complete. Proceed to Phase <N+1>: <NAME>?"

   - ⛔ Wait for explicit user approval before continuing

---

Documentation Verification Checklist:

Before marking phase complete, verify:
- [ ] All files in task "documentation" fields updated
- [ ] CHANGELOG.md updated with user-facing changes
- [ ] All doc internal links valid (no broken references)
- [ ] Code comments updated for major changes

---

Archive Process:

```bash
# 1. Move spec to archived with completion date
mv .windsurf/specs/active/PHASE_<N>_<NAME>.yaml \
   .windsurf/specs/archived/PHASE_<N>_<NAME>_completed_$(date +%Y-%m-%d).yaml

# 2. Create completion report
cat > docs/dev/PHASE_<N>_COMPLETION_REPORT.md << 'EOF'
# Phase <N> Completion Report

## Summary
[Brief overview]

## Changes Made
[List of files changed]

## Test Results
[Verify command outputs]

## Known Issues
[Any remaining issues]

## Next Steps
[What comes next]
EOF
```

---

LDI Equipment Dashboard requirements:

- README.md or relevant docs must be updated if user-facing changes made
- Git diff --stat must be included in Phase End Report
- Full verify output must be pasted (not summarized)
- Spec must be archived to .windsurf/specs/archived/ with completion date

---

## How to Use

1. Copy the template above
2. Replace `<N>` with phase number
3. Replace `<PHASE NAME>` with phase name from build spec
4. Replace `<N+1>` and `<NAME>` with next phase info
5. Replace `<SPEC>` with spec filename
6. Paste into agent prompt when phase is ready for completion

---

## Example: Completing Phase P1

```text
Phase P1: Connectors and Bronze Store — Completion Checklist

Follow execute-spec.md Step 2.4-2.6 exactly:

1) Run ALL phase verify commands (paste full output + exit codes).
   - If any verify fails: STOP, report failure, do not mark phase complete.

2) Complete documentation requirements:
   - Update README.md or relevant docs if user-facing changes were made
   - Complete any docs listed in task "documentation" fields
   - Verify all doc links are valid

3) Post the Phase End Report using the template from execute-spec.md:
   - Status (✅/⚠️/❌)
   - Phase Scope (what was done vs. spec)
   - Reads Confirmed (list files read)
   - Changes Made (git diff --stat + file list)
   - Verification (all verify command outputs)
   - Behavioral Impact (user/CI/dev changes)
   - Documentation (files touched + needed)
   - Risks & Rollback plan
   - Deferred Items (if any)

4) Archive this phase build spec:
   - Move .windsurf/specs/active/PHASE_P1_CONNECTORS_BRONZE.yaml to
   - .windsurf/specs/archived/PHASE_P1_CONNECTORS_BRONZE_completed_2026-03-01.yaml

5) Create phase completion report:
   - docs/dev/PHASE_P1_COMPLETION_REPORT.md
   - Include: scope, changes, test results, known issues, next steps

6) Ask for approval: "Phase P1 complete. Proceed to Phase P2: Silver Normalization and Crosswalk Mapping?"
   - ⛔ Wait for explicit user approval before continuing

---

Documentation Verification Checklist:

Before marking phase complete, verify:
- [x] All files in task "documentation" fields updated
- [x] CHANGELOG.md updated with user-facing changes
- [x] All doc internal links valid
- [x] Code comments updated

---

Archive Process:

```bash
mv .windsurf/specs/active/PHASE_3_CI_GUARDS.yaml \
   .windsurf/specs/archived/PHASE_3_CI_GUARDS_completed_2026-02-24.yaml
```

---

## Key Design Decisions (Git Commit Policy)

- **Phase-level commits (not per-task):** Keeps git history clean
  and aligned with your phase-based workflow structure.
  Each phase is a logical unit of work with a single commit.
- **Commit after verification:** Ensures only working code gets committed.
  All verify commands must pass before the commit is made.
- **Standardized format:** Makes commit history readable and traceable
  to build specs. Future developers can instantly see which phase
  introduced which changes.
- **SHA tracking:** Phase End Report now captures the exact commit SHA
  for each phase completion. Enables precise rollback and audit trails.

## Key Points

- **Documentation verification:** Explicit checklist prevents forgotten docs
- **Archive process:** Moves spec with completion date to archived/
- **Completion report:** Creates permanent record of phase results
- **Approval gate:** Explicit user approval required before next phase
- **No shortcuts:** All verify commands must pass before completion

---

## See Also

- `.windsurf/workflows/execute-spec.md` — Master workflow
- `.windsurf/workflows/PHASE_START_PROMPT.md` — Phase start template
- `.windsurf/specs/active/README.md` — Guide to build specs and execution order
- `.windsurf/specs/active/PHASE_P0_REPO_DB_CONFIG.yaml` — Equipment Hours Validation Phase P0
- `.windsurf/specs/active/PHASE_1_UNIFIED_OPS_UI_SCREENS.yaml` — Unified Ops Dashboard Phase 1
- `.windsurf/specs/archived/` — Completed build specs

---

description: Execute a structured build spec pasted from an external LLM. Parses YAML task packages and works through phases sequentially.
---



# Execute Spec Workflow



When the user pastes a **build spec** (YAML block or markdown with YAML frontmatter), follow this process:



## Step 1: Parse the Spec



1. Look for a YAML block (fenced with ```yaml or in frontmatter) in the user's message.

2. Identify the top-level fields:

   - `project` — context about what repo/system this targets

   - `phases` — ordered list of work phases

3. Confirm with the user: "I found [N] phases targeting [project]. Ready to start Phase 1: [name]?"



## Step 2: Execute Phases Sequentially



For each phase in `phases`:



1. **Announce the phase:** Print the phase name, goal, and context (from `context` field).

2. **Read context files:** Read all files listed in `reads` (these are files the agent needs to understand before editing).

3. **Execute tasks:** For each task in `tasks`:

   - **Read target files** if they exist

   - **Understand the task:** Review `description`, `acceptance_criteria`, and `implementation_notes`

   - **Perform the action:** (`create`, `modify`, `delete`)

   - **Follow implementation guidance:** Use `details` field for specific code/logic

   - **Respect code style:** Match indentation, naming, and patterns already in codebase

   - **Document as you go:** Update files listed in `documentation` field

   - **Test incrementally:** Run commands from `testing` field after each task

4. **Verify phase completion:** After all tasks in a phase:

   - Run all commands listed in `verify` (tests, linting, type checks)

   - Confirm all `acceptance_criteria` are met

   - Check `done_when` conditions

5. **Complete phase-end checklist:** Use PHASE_END_PROMPT.md template:

   - Run all verify commands (paste full output)

   - Complete documentation requirements

   - Post Phase End Report

   - Archive build spec to .windsurf/specs/archived/

   - Create phase completion report in docs/dev/

   - **Commit all changes** (see Git Commit Policy below)

6. **Ask to continue:** "Phase [N] complete. Proceed to Phase [N+1]: [name]?" and wait for approval



## Step 3: Completion



After all phases:

1. Summarize all changes made across all phases

2. List any items from `follow_up` that need future attention

3. Suggest a commit message based on the work done



## Spec Format: Supported Fields



Each phase should include:



```yaml

phases:

  - name: "Phase N — [Name]"

    description: "What this phase accomplishes"

    context: "Background / why this matters / dependencies"

    reads: ["path/to/file.py", "path/to/other.py"]  # Files to read for context

    tasks:

      - task_id: "unique-id"

        name: "Task name"

        description: "What the task does"

        acceptance_criteria:

          - "Condition A holds"

          - "Condition B holds"

        implementation_notes: "Guidance on how to implement"

        documentation:

          - "Update docs/foo.md with X"

          - "Add docstring to function Y"

        testing:

          - "pytest tests/test_x.py -q"

          - "ruff check ."

        files_to_create: ["path/to/new_file.py"]

        files_to_modify: ["path/to/existing_file.py"]

    verify:

      - "pytest tests/ -q"

      - "ruff check ."

    done_when: |

      All acceptance criteria met and all verify commands pass.

```



**Field explanations:**

- `reads` — Files the agent must read to understand context before editing

- `context` — Background/rationale for the phase

- `acceptance_criteria` — Per-task conditions that must be true when done

- `implementation_notes` — Guidance on how to implement (not what to do, but how)

- `documentation` — Specific doc updates required

- `testing` — Test/lint commands to run per task

- `verify` — Phase-level verification commands (run after all tasks)

- `done_when` — Conditions for phase completion



## Rules



- **Never skip phases.** They are ordered for a reason (later phases depend on earlier ones).

- **Never skip reads.** Context files exist so you understand the codebase before editing.

- **Ask before proceeding** to the next phase. The user may want to review or adjust.

- **If a task is ambiguous**, ask for clarification rather than guessing.

- **If a verify step fails**, stop and report. Don't proceed to the next phase with broken state.

- **Respect existing code style.** Match indentation, naming conventions, and patterns already in the codebase.

- **Each phase should leave the codebase in a working state.** No half-finished refactors.

- **Document as you implement.** Don't defer documentation to the end.

- **Commit at phase completion.** All changes for a phase must be committed before approval (see Git Commit Policy).




---



## Git Commit Policy



**When to commit:** At the end of each phase, after all tasks are complete and all verify commands pass.



**Commit scope:** All changes made during the phase (code, docs, configs, specs).



**Commit message format:**



```text

<project>: Phase <N> — <PHASE NAME>



<1-2 sentence summary of what was accomplished>



Changes:

- <file/change 1>

- <file/change 2>

- <file/change 3>



Verification:

- All phase verify commands passed

- All acceptance criteria met

- Phase End Report: docs/dev/PHASE_<N>_COMPLETION_REPORT.md

```



**Example:**



```text

TF_REGISTRY: Phase 1 — Critical Protection (Write Coordination + Hooks + CI)



Implemented optimistic locking in sync tools, pre-commit hooks, GitHub Actions CI validation, and branch protection rules to prevent registry data corruption.



Changes:

- tools/notion-sync/registry-lock.js (new)

- tools/notion-sync/sync.js (modified)

- tools/gumroad-integration/sync-products.js (modified)

- canonical/.git/hooks/pre-commit (new)

- canonical/.github/workflows/validate-registry.yml (new)

- canonical/REGISTRY_GOVERNANCE.md (updated)



Verification:

- All phase verify commands passed

- All acceptance criteria met

- Phase End Report: docs/dev/PHASE_1_COMPLETION_REPORT.md

```



**Pre-commit checklist:**



- [ ] All files staged (`git add .`)

- [ ] `git status` shows expected changes only

- [ ] No unintended files included

- [ ] Commit message follows format above

- [ ] Phase End Report created and linked in commit message



**After commit:**



- Paste commit SHA in Phase End Report (section 0, "Commit(s)" field)

- Push to branch (if working on feature branch)

- Request user approval to proceed to next phase



---



## UI Verification Requirement (applies to any verify line labeled "Manual test" or "UI test")



**Classification rule:** Any `verify` entry containing `Manual test`, `UI test`, `Dashboard`, `Streamlit`, `Browser`, `Playwright`, or `Puppeteer` is treated as a UI verify step and must follow this section.



If a phase `verify` list contains a line that is a **Manual test** / **UI test**, the agent must NOT satisfy it via code inspection alone.



### Acceptable ways to satisfy a UI verify line:



#### A) Agent-run automation (preferred)

- Use Playwright (preferred) or Puppeteer to launch a browser session, navigate to the UI, and perform a smoke path.

- The agent must capture evidence artifacts (minimum requirements):

  - **2 screenshots minimum:** landing page + target page

  - **1 interaction screenshot:** after clicking a tab/button/action

  - (Optional) Playwright trace/video if available

- If automation cannot run (missing browser deps), the agent must:

  - report the blocker with exact error output

  - propose the smallest fix

  - **STOP** (do not mark the verify step as passed)



#### B) Guided manual session (when automation cannot run)

- The agent provides a short, numbered checklist (≤12 steps) that the user performs in their browser.

- After each step, the agent pauses and records the user's feedback as PASS/FAIL/BLOCKED.

- The verify step is only marked ✅ PASS if the user confirms all steps pass.



### Anti-fake rule (prevents code inspection loophole)

**A UI verify step cannot be marked PASS unless either (A) automation produced artifacts (screenshots/trace), or (B) the user explicitly confirmed all checklist steps PASS.** Running the dashboard + inspecting code is not sufficient.



### For all UI verify lines, the phase report MUST include:

- the tool used (Playwright/Puppeteer) OR the guided checklist + user confirmations

- commands used to launch the app

- artifact paths (screenshots/trace) if automated

- explicit PASS/FAIL and rationale



---



## Phase End Report Template



After completing all tasks in a phase, use this template to document scope, proofs, verification, and approval gating. Copy/paste at the end of each phase execution.



### Full Version



```md

# Phase End Report — Phase <N>: <PHASE NAME>



## 0) Status

- **Status:** ✅ Complete / ⚠️ Blocked / ❌ Failed

- **Approval Gate:** ⛔ Waiting for user approval to proceed to Phase <N+1>

- **Branch:** <branch>

- **Commit(s):** <sha(s)> (or "uncommitted changes")

- **Date:** <YYYY-MM-DD>



## 1) Phase Scope (What was supposed to happen)

- **Phase Goal:** <1–2 sentences>

- **In-Scope Tasks (from build spec):**

  - <T1> — ✅/⚠️/❌

  - <T2> — ✅/⚠️/❌

- **Out-of-Scope Work:** None / <list + why>



## 2) Reads Confirmed (execute-spec "reads" compliance)

- Read these before changes:

  - <file/path 1>

  - <file/path 2>

- Notes / key constraints discovered:

  - <bullet>



## 3) Changes Made (Proof + Summary)

### Files Changed

- **Modified:**

  - <path>

  - <path>

- **Added:**

  - <path>

- **Removed:**

  - <path>



### Git Diff

- **Diff Stats:** <paste `git diff --stat` output>

- **Full Diff / Patch:** <paste `git diff` OR attach patch / link>



## 4) Verification (Required)

### Task-Level Testing (per-task "testing" commands)

- Command(s) run + output + exit code:

  - ```bash

    <cmd>

    ```

    Output:

    ```

    <paste>

    ```

    Exit code: <0/1>



### Phase Verify (MUST match build spec "verify" block)

- Verify commands executed (paste exact list):

  - ```bash

    <verify cmd 1>

    <verify cmd 2>

    ```

- Full output + exit codes:

  - ```

    <paste>

    ```

- **Result:** ✅ Pass / ❌ Fail

- If fail: **Stopped here** (no further phases started)



### Environment (so results are reproducible)

- OS: <windows/mac/linux>

- Python: <version>

- Tooling: <poetry/pip/uv/etc>

- Notes: <any env gotchas>



## 5) Behavioral Impact (What changes for users & CI)

### User-Facing

- <what users can do now / what breaks / new rules>



### CI / Governance / Policy Outcomes

- <new checks/rules, new failures possible, severity/weight changes>



### Developer Impact

- <new tests, fixtures, scripts, migration notes>



## 6) Documentation (Required)

### Docs Touched

- <README.md?>

- <WORKSPACE.yaml?>

- <DOCUMENTATION_INDEX.md?>

- <relevant docs/*?>

- <other>



### Docs Needed (Must finish before leaving phase unless explicitly approved to defer)

- <file> — <what must be added/updated>

- <file> — <what must be added/updated>



### Docs Conflicts / Notes

- If code and docs conflict: <how resolved>



## 7) Risks & Rollback

- **Risk flags:** None / <breaking change risk, CI risk, behavior change risk>

- **Rollback plan:** <revert commit(s) / restore config / disable rule / feature flag>

- **Migration steps (if any):** <steps>



## 8) Deferred Items (Logged, not implemented)

- <item> — why deferred + target phase + file/line pointers if possible



## 9) Approval Request

- **Request:** Please approve proceeding to **Phase <N+1>: <NEXT PHASE NAME>**

- **User decisions needed (if any):**

  - <decision 1>

  - <decision 2>

```



### Ultra-Compact Version (one screen)



```md

# Phase <N> End — <PHASE NAME> (⛔ awaiting approval)



✅ Tasks: <T1>, <T2> (In-scope only; out-of-scope: none/<list>)

🧾 Files: +<n> ~<n> -<n> (paste diffstat below)

🧪 Tests (paste cmds + outputs + exit codes)

✅ Phase Verify (paste verify cmds + outputs + exit codes)

📌 Impact: <1–3 bullets>

📚 Docs touched: <list> | Docs needed: <list>

⚠️ Risks: <none/list> | Rollback: <1 line>

➡️ Approve Phase <N+1>? <yes/no>

```



### Repo-Specific Customizations



For **tangent-forge-repo-manager**, enforce these additional requirements:



- **DOCUMENTATION_INDEX.md:** Must be updated if any docs are added/modified/removed

- **WORKSPACE.yaml:** Update if workspace structure or governance markers change

- **Policy Rule IDs:** Document any new/changed rule IDs (e.g., DOCS-002, P1-T1)

- **Audit Discrepancies:** If audit claims differ from code reality, note the discrepancy and correction

- **Coaching Patterns:** If new patterns are created, register them in coaching/patterns/registry.yaml

- **Schema Changes:** If schemas are modified, validate against all existing artifacts
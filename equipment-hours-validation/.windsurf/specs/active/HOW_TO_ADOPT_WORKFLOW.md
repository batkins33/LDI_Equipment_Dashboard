# How to Adopt the Build Spec Workflow in a New Repository

This guide explains how to take the generic build spec workflow files (`execute-spec.md`, `PHASE_START_PROMPT.md`, `PHASE_END_PROMPT.md`) and customize them for a brand new repository.

The build spec workflow allows you to use AI agents to sequentially execute complex, multi-phase technical plans (written in YAML) in a safe, verifiable, and documentable manner.

## Files to Copy

To adopt this workflow in a new repo, you need to copy these 3 files into your new repository's `.windsurf/workflows/` (or equivalent AI instruction) folder:

1. **`execute-spec.md`**: The master rules engine. (Usually requires **zero** changes)
2. **`PHASE_START_PROMPT.md`**: The template you paste to start a phase. (Requires **minor** repo-specific customization)
3. **`PHASE_END_PROMPT.md`**: The template you paste to finish a phase. (Requires **minor** repo-specific customization)

---

## 1. Customizing `execute-spec.md`

**Status:** Usually requires NO changes.

This file acts as the universal "engine". It tells the AI how to parse the YAML spec, what the `reads` array means, how to handle `verify` blocks, etc. 

*Optional Tweaks:*
- If your new repo has a specific UI verification tool (e.g., Cypress instead of Playwright), you might tweak the `UI Verification Requirement` section.
- If your new repo uses a different Git strategy (e.g., squash merges instead of phase-commits), you might tweak the Git Rules section.

---

## 2. Customizing `PHASE_START_PROMPT.md`

**Status:** Requires customization for your specific repo.

This file contains the actual prompt you will copy/paste to the AI to kick off a phase.

### What to change:
1. **Update the Title/Metadata:** Change `DocTR_Process` to your repo's name.
2. **Update Repo-Specific Requirements:** 
   Locate the section that looks like this:
   ```markdown
   RepoName requirements:
   - Update CHANGELOG.md if user-facing changes are made.
   - Update docs/ as specified in task `documentation` fields.
   - Follow git commit policy...
   ```
   *Modify this list to match the hygiene rules of your new repo.* (e.g., Do you use a `docs/` folder or a `wiki/` folder? Do you require updating a specific architecture diagram?)
3. **Update the "Active Phases" List (Optional):**
   Update the examples at the bottom of the file to reflect the actual roadmap/phases of your new project.

---

## 3. Customizing `PHASE_END_PROMPT.md`

**Status:** Requires customization for your specific repo.

This file contains the checklist the AI must complete before a phase is considered "done".

### What to change:
1. **Update the Title/Metadata:** Change `DocTR_Process` to your repo's name.
2. **Update the Git Commands:**
   Look at Step 4 and 5 in the template:
   ```markdown
   - Commit with standardized message format: `<project>: Phase <N> — <PHASE NAME>`
   ```
   *Change `<project>` to your actual project name or Jira ticker prefix.*
3. **Update Documentation Requirements:**
   Look at Step 2 in the template:
   ```markdown
   - Update DOCUMENTATION_INDEX.md if docs were added/modified/removed
   - Update WORKSPACE.yaml if workspace structure changed
   ```
   *If your new repo doesn't use `DOCUMENTATION_INDEX.md` or `WORKSPACE.yaml`, remove those lines.* Replace them with the actual documentation standards of your new repo.
4. **Update File Paths:**
   Ensure the archival paths match your new repo's structure. For example, if you prefer storing specs in `docs/specs/` instead of `.windsurf/specs/`, update the `mv` commands in the Archive Process section.

---

## Directory Structure Setup

In your new repository, ensure you create the following directory structure to support the workflow:

```text
.windsurf/
  ├── workflows/
  │   ├── execute-spec.md
  │   ├── PHASE_START_PROMPT.md
  │   └── PHASE_END_PROMPT.md
  └── specs/
      ├── active/        # Where you place the YAML specs you want to run
      └── archived/      # Where specs go after completion
```

*(You can change `.windsurf` to `.cursor` or `.github/prompts` depending on your AI tooling, just remember to update the file paths in the prompt templates).*

# SysPulse Phase 2 Implementation Plan

**Status**: 🚧 In Progress
**Version**: 2.0.0 (in development)
**Started**: 2025-01-24

---

## Overview

Phase 2 adds **actionable controls** to SysPulse. While Phase 1 (v1.0) was read-only analysis with recommendations, Phase 2 allows users to take action directly from the tool.

---

## Core Principle: Safety First

All Phase 2 features follow these rules:

1. ✅ **Confirmations required** - No auto-actions without explicit user approval
2. ✅ **Backups before changes** - Create restore points before modifying anything
3. ✅ **Dry-run mode** - Show what WOULD happen before actually doing it
4. ✅ **Logging** - Record all actions taken for audit trail
5. ✅ **Graceful failures** - If something fails, explain why and how to fix

---

## Implementation Order

### ✅ Phase 2.1: Browser Cache Cleanup
**Commit**: `phase2/browser-cleanup`
**Status**: Pending

**Features**:
- Clear cache for specific browser profiles
- Batch clear multiple profiles
- Show size to be freed before confirming
- Option to keep last N days of cache
- Backup profile preferences before clearing

**Safety**:
- Only deletes cache files, never profile data
- Preserves bookmarks, passwords, history
- Confirmation with exact size to be deleted
- Can target specific profiles or all

**Files to modify**:
- `modules/browser_scanner.py` - Add `clear_cache()` method
- `modules/actions/browser_actions.py` - New action module
- `syspulse.py` - Add `--clean-browser-cache` flag

---

### ✅ Phase 2.2: Storage Cleanup Actions
**Commit**: `phase2/storage-cleanup`
**Status**: Pending

**Features**:
- Clear temp files
- Empty recycle bin
- Delete old downloads (with review)
- Safe removal with confirmation

**Safety**:
- Show list of files to be deleted
- Require confirmation per category
- Option to move to recycle bin instead of permanent delete
- Skip files in use

**Files to modify**:
- `modules/storage_sense.py` - Add cleanup methods
- `modules/actions/storage_actions.py` - New action module
- `syspulse.py` - Add `--cleanup-storage` flag

---

### ✅ Phase 2.3: Startup Manager
**Commit**: `phase2/startup-manager`
**Status**: Pending

**Features**:
- Disable startup items
- Re-enable startup items
- Backup startup configuration
- Restore previous configuration
- Test boot time changes

**Safety**:
- Backup registry before changes
- Never delete entries, only disable
- Can undo all changes
- Warn about system-critical items

**Files to modify**:
- `modules/startup_analyzer.py` - Add enable/disable methods
- `modules/actions/startup_actions.py` - New action module
- `syspulse.py` - Add `--manage-startup` flag

---

### ✅ Phase 2.4: Report Generation
**Commit**: `phase2/reports`
**Status**: Pending

**Features**:
- Export scan results to JSON
- Generate HTML reports
- Before/after comparisons
- Save scan history
- Email reports (optional)

**Safety**:
- No sensitive data in reports (passwords, etc.)
- Option to anonymize data
- Local storage only (no auto-upload)

**Files to modify**:
- `modules/reporting.py` - New module
- `reports/templates/` - HTML templates
- `syspulse.py` - Add `--export` flag

---

### ✅ Phase 2.5: Interactive Mode
**Commit**: `phase2/interactive-mode`
**Status**: Pending

**Features**:
- Interactive CLI menu
- Step-by-step guided cleanup
- Real-time feedback
- Undo functionality

**Safety**:
- Always ask before each action
- Show what will happen
- Confirm before executing

**Files to modify**:
- `ui/interactive.py` - New interactive UI module
- `syspulse.py` - Add `--interactive` flag

---

## Commit Strategy

Each feature above gets **its own commit** following this format:

```
[Phase2] Add browser cache cleanup actions

- Add clear_cache() method to BrowserScanner
- Create browser_actions module with safe cleanup
- Add --clean-browser-cache CLI flag
- Include confirmation and dry-run mode
- Update tests

Implements Phase 2.1 from PHASE2_PLAN.md
```

This allows:
- ✅ Clear progression tracking
- ✅ Easy rollback of individual features
- ✅ Isolated testing of each feature
- ✅ Understanding what changed when

---

## Testing Strategy

Each feature commit includes:

1. **Unit tests** - Test the action module directly
2. **Integration tests** - Test CLI flags work correctly
3. **Safety tests** - Verify confirmations work, backups created
4. **Manual testing** - Actually run it on a test system

Test files:
- `tests/test_browser_actions.py`
- `tests/test_storage_actions.py`
- `tests/test_startup_actions.py`
- `tests/test_reporting.py`

---

## Documentation Updates

Each feature commit updates:

1. **README.md** - Add new features to feature list
2. **QUICKSTART.md** - Add usage examples
3. **ROADMAP.md** - Mark features as completed
4. **CHANGELOG.md** - Document what changed

---

## Version Numbering

- **v1.0.0** - Phase 1 (MVP, read-only analysis) ✅
- **v2.0.0-alpha.1** - Phase 2.1 (browser cleanup)
- **v2.0.0-alpha.2** - Phase 2.2 (storage cleanup)
- **v2.0.0-alpha.3** - Phase 2.3 (startup manager)
- **v2.0.0-alpha.4** - Phase 2.4 (reports)
- **v2.0.0-alpha.5** - Phase 2.5 (interactive mode)
- **v2.0.0-beta** - All Phase 2 features complete, testing
- **v2.0.0** - Phase 2 stable release

---

## Rollback Plan

If any feature needs to be reverted:

```bash
# Revert specific commit
git revert <commit-hash>

# Or reset to Phase 1 stable
git reset --hard a42ca12  # v1.0.0 commit

# Or create a branch from Phase 1
git checkout -b phase1-stable a42ca12
```

---

## Current Status

| Feature | Status | Commit | Version |
|---------|--------|--------|---------|
| Phase 1 MVP | ✅ Complete | `a42ca12` | v1.0.0 |
| Browser Cleanup | ⏳ Pending | - | v2.0.0-alpha.1 |
| Storage Cleanup | ⏳ Pending | - | v2.0.0-alpha.2 |
| Startup Manager | ⏳ Pending | - | v2.0.0-alpha.3 |
| Reports | ⏳ Pending | - | v2.0.0-alpha.4 |
| Interactive Mode | ⏳ Pending | - | v2.0.0-alpha.5 |

---

## Questions to Answer Before Each Feature

Before implementing each Phase 2 feature, verify:

1. ✅ Does this maintain Phase 1 stability?
2. ✅ Can this be safely reverted?
3. ✅ Is there a confirmation step?
4. ✅ Is there a backup/undo mechanism?
5. ✅ Are errors handled gracefully?
6. ✅ Is it tested?
7. ✅ Is it documented?

---

## Next Action

Starting with **Phase 2.1: Browser Cache Cleanup** (safest to implement first)

After that's committed and tested, move to Phase 2.2, then 2.3, etc.

Each can be reviewed independently before proceeding to the next.

# Active Build Specs

This directory contains executable phase-based build specs aligned with the `execute-spec.md` workflow.

## DocTR_Process Track B Architecture Phases

### Phase 1: Track B Docker Parity ✅ COMPLETE
**Status:** Merged to `develop` and `main`  
**Completion Date:** 2026-02-24  
**Report:** `artifacts/reports/TRACK_B_IMPLEMENTATION_REPORT.md`

Implemented platform-centric Docker architecture with both `truck_tickets` and `loadmatcher` packages.

---

### Phase 1.5: LOM Production Readiness ✅ MERGED
**Status:** Merged to `develop` (2026-02-24)  
**Branch:** `feature/lom-production-readiness-phase4`  
**Key Deliverables:**
- Canonical extraction schema with confidence scoring
- 3-tier fallback orchestrator (local → vision → cloud)
- Production hardening: shutdown handlers, circuit breaker, timeouts
- Comprehensive metrics collection (latency percentiles, error rates, cost tracking)
- Request tracing with correlation IDs and credential sanitization
- 15 test files covering all LOM modules
- **Status:** 8.5/10 production-ready (minor fixes applied)

**Pre-merge fixes applied:**
- ✅ Circuit breaker thread safety (threading.Lock)
- ✅ Vision integration test (test_vision_integration.py)

---

### Phase 2: Entrypoint Drift Fix
**File:** `PHASE_2_ENTRYPOINT_DRIFT.yaml`  
**Priority:** HIGH  
**Effort:** 1-2 hours  
**Status:** Ready to execute  
**Dependencies:** Phase 1 (Track B) merged to main

Align console script entrypoints with actual implementation modules.

**Key Tasks:**
- Update `truck-tickets-gui` → `truck_tickets.gui_unified:main`
- Update `truck-tickets-web` → `truck_tickets.web.app_clean:main`
- Update `launcher.bat` Web button
- Verify deprecation headers remain

---

### Phase 3: CI Guards for Cross-Package Imports
**File:** `PHASE_3_CI_GUARDS.yaml`  
**Priority:** HIGH  
**Effort:** 3-5 hours  
**Status:** Ready after Phase 2  
**Dependencies:** Phase 1 complete, Phase 2 recommended

Add CI enforcement to prevent unguarded `truck_tickets <-> loadmatcher` coupling.

**Key Tasks:**
- Extend `check_cross_imports.py` to detect cross-package imports
- Add CI workflow step for import checking
- Document exception rules with inline comments
- Test violation detection

---

### Phase 4: Adapter Seam Design Document
**File:** `PHASE_4_ADAPTER_DESIGN.yaml`  
**Priority:** MEDIUM  
**Effort:** 1-2 days  
**Status:** Ready after Phase 3  
**Dependencies:** Phase 3 complete (CI guards in place)

Design (not implement) the adapter layer for Option B decoupling.

**Key Tasks:**
- Design adapter protocol and interface
- Define adapter location and loading strategy
- Document deprecation timeline for direct imports
- Create example LLM adapter design
- Design review checklist

---

## Execution Instructions

### To Start a Phase:

1. **Read the phase spec** thoroughly
2. **Use the canonical phase start prompt:**
   ```
   Start Phase <N>: <PHASE NAME>.
   
   Follow execute-spec.md Step 2 exactly:
   
   1) Announce the phase (goal + acceptance criteria).
   2) Read every file listed in `reads` before editing anything.
   3) Execute tasks in order. After each task, run the task's `testing` commands.
   4) After all tasks, run EVERY command in the phase `verify` list.
   5) Post the Phase End Report and ask: "Proceed to Phase <N+1>?"
   ```

3. **Complete Phase End Report** (template in execute-spec.md)
4. **Update documentation** as specified in phase spec
5. **Archive the build spec** when complete:
   - Move to `.windsurf/specs/archived/PHASE_<N>_<NAME>_completed_YYYY-MM-DD.yaml`
6. **Create completion summary** in `docs/dev/PHASE_<N>_COMPLETION_REPORT.md`
7. **Get user approval** before proceeding to next phase

---

## Recommended Execution Order

**Completed:**
1. ✅ Phase 1 (Track B Docker Parity) - Platform-centric architecture
2. ✅ Phase 1.5 (LOM Production Readiness) - Merged to develop

**Next (Choose based on priority):**
- Phase 2 (Entrypoint Drift) - HIGH priority, 1-2 hours
- Phase 3 (CI Guards) - HIGH priority, 3-5 hours  
- Phase 4 (Adapter Design) - MEDIUM priority, 1-2 days
- Phase 5 (LOM Deployment) - HIGH priority, 2-3 hours (NEW - validates LOM in staging)

**Note:** Phases 2-5 can be executed in order or in parallel after Phase 1 completion.

---

## Archival Process

When a phase is complete:

1. **Verify all acceptance criteria met**
2. **Run all verify commands** and document results
3. **Complete Phase End Report** with full details
4. **Update all documentation** as specified
5. **Move build spec to archived:**
   ```powershell
   Move-Item ".windsurf/specs/active/PHASE_<N>_*.yaml" `
             ".windsurf/specs/archived/PHASE_<N>_*_completed_$(Get-Date -Format 'yyyy-MM-dd').yaml"
   ```
6. **Create completion report:**
   ```powershell
   # Create docs/dev/PHASE_<N>_COMPLETION_REPORT.md with summary
   ```
7. **Update this README** to mark phase as complete

---

## See Also

- `.windsurf/workflows/execute-spec.md` - Master execution workflow
- `.windsurf/workflows/PHASE_START_PROMPT.md` - Standard phase start template
- `.windsurf/specs/archived/` - Completed phase specs
- `docs/dev/` - Phase completion reports

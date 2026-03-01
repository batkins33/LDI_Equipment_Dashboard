# Executive Summary — Equipment Hours Validation

## Problem
Equipment hours are reported across multiple sources that often conflict:
- GPS/telematics runtime (objective engine hours)
- Foreman-entered equipment hours on timecards (subjective + allocation)
- Daily inspections (hour meter readings + photos)
- Equipment360 meter readings (shop-maintained)

The current process delays validation because **timecard hours are not available quickly** due to the approval workflow.

## Why the current approach fails
- Validation waits for approvals → issues found days later
- Equipment identifiers differ across systems → mismatches/manual reconciliation
- No normalized daily grain (Equipment × Day) → comparisons are ad hoc
- No exceptions queue → discrepancies don’t become actionable tasks

## Solution
Build an **Equipment Hours Validation Hub** that produces:
- **Provisional** (“Yesterday by 6am”) from submitted timecards + GPS + inspections + E360
- **Final** overlay as approvals occur + nightly backfill

Normalize all sources into a canonical schema with crosswalk mapping, compute variances, score confidence, and drive an exceptions queue.

## Business outcomes
- Same-day visibility into missing/incorrect hours
- Better equipment utilization truth (under-reporting vs true idle)
- Less downstream churn (payroll/job-cost corrections)
- Higher confidence in cost and productivity reporting


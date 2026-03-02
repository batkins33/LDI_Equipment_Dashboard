# Mock Data Guide

## Overview

This guide explains the mock data fixtures used in Phase P0.5 demo and how to regenerate them.

## Mock Data Fixtures

### 1. mock_heavyjob.json
**Source:** HeavyJob timecard system

**Contents:**
- 5 jobs across 3 business units
- 10 pieces of equipment
- 3 foremen
- 296 timecards (30-day history)

**Variance Scenarios:**
- Approval delays: 0-5 days (realistic workflow delays)
- Mixed status: APPROVED, PENDING
- Hours range: 4-10 hours per equipment-day

### 2. mock_telematics.json
**Source:** GPS/telematics system

**Contents:**
- 10 equipment devices
- 300 daily engine hour readings (30 days × 10 equipment)
- Cumulative engine hours: 5,000-15,000 range

**Variance Scenarios:**
- Daily hours: 3-9 hours (realistic equipment usage)
- GPS active: 85% of days (15% offline/no signal)
- Cumulative progression: realistic meter advancement

### 3. mock_safety.json
**Source:** Safety/inspections system

**Contents:**
- 10 equipment
- 253 inspection records (85% coverage, 15% missing)
- Hour meter readings (start/end)
- Photo counts: 2-8 per inspection
- Issues: 0-3 per inspection

**Variance Scenarios:**
- Missing inspections: 15% of equipment-days
- Meter delta: 2-8 hours (realistic daily usage)
- Issues detected: common maintenance findings

### 4. mock_equipment360.json
**Source:** Equipment360 meter readings

**Contents:**
- 10 equipment
- 100 readings (every 3 days, 30-day period)
- Cumulative engine hours: 5,000-15,000 range

**Variance Scenarios:**
- Sparse readings: every 3 days (not daily)
- Meter advancement: 15-30 hours per 3-day period
- Realistic shop-maintained meter progression

## Variance Scenarios Explained

### High Variance (GPS > Timecard)
**Scenario:** Equipment worked longer than foreman reported
- GPS shows 8 hours, timecard shows 5 hours
- **Flag:** HIGH_VARIANCE
- **Action:** Verify with foreman; may indicate under-reporting or allocation error

### Low Variance (GPS < Timecard)
**Scenario:** Foreman reported more hours than GPS shows
- Timecard shows 8 hours, GPS shows 4 hours
- **Flag:** HIGH_VARIANCE
- **Action:** Verify GPS device; may indicate device offline or miscalibration

### Missing Inspection
**Scenario:** No daily inspection for active equipment
- Equipment worked (GPS + timecard), but no meter reading
- **Flag:** MISSING_INSPECTION
- **Action:** Schedule inspection; affects confidence score

### Missing Telematics
**Scenario:** No GPS data for equipment-day
- Timecard and inspection exist, but GPS offline
- **Flag:** MISSING_TELEMATICS
- **Action:** Check device; may indicate connectivity issue

### Approval Delay
**Scenario:** Timecard not approved same-day
- Submitted 6pm, approved 3 days later
- **Flag:** APPROVAL_DELAY
- **Action:** Expedite approval; delays provisional visibility

## Regenerating Mock Data

### Prerequisites
- Python 3.8+
- No external dependencies (uses only stdlib)

### Command
```bash
python 02-equipment-hours-validation/scripts/generate_mock_data.py
```

### Output
Generates 4 JSON files in `02-equipment-hours-validation/data/fixtures/`:
- `mock_heavyjob.json`
- `mock_telematics.json`
- `mock_safety.json`
- `mock_equipment360.json`

### Customization

To modify variance patterns, edit `generate_mock_data.py`:

**Increase approval delays:**
```python
approval_delay = random.choice([0, 1, 2, 3, 5, 7])  # Add 7-day delays
```

**Increase missing inspections:**
```python
if random.random() > 0.10:  # Change from 0.15 to 0.10 (10% missing)
```

**Adjust equipment count:**
```python
equipment = [
    {"equipment_id": f"EQ-{i:03d}", ...}
    for i in range(1, 21)  # 20 equipment instead of 10
]
```

**Adjust date range:**
```python
base_date = datetime.now() - timedelta(days=60)  # 60 days instead of 30
for day_offset in range(60):  # Update loop range
```

## Data Validation

### Check fixture files exist
```bash
ls -la 02-equipment-hours-validation/data/fixtures/
```

### Validate JSON syntax
```bash
python -c "import json; json.load(open('02-equipment-hours-validation/data/fixtures/mock_heavyjob.json'))"
```

### Count records
```bash
python -c "
import json
for fixture in ['mock_heavyjob', 'mock_telematics', 'mock_safety', 'mock_equipment360']:
    data = json.load(open(f'02-equipment-hours-validation/data/fixtures/{fixture}.json'))
    print(f'{fixture}: {len(data.get(\"timecards\", data.get(\"readings\", data.get(\"inspections\", []))))} records')
"
```

## Integration with Demo

The demo script (`scripts/demo.py`) automatically:
1. Generates mock data if fixtures don't exist
2. Loads fixtures into database
3. Runs normalizers and reconciliation
4. Populates dashboard views

No manual data loading required—just run `python scripts/demo.py`.

## Notes

- Mock data is **deterministic** (uses `random.seed()` if needed for reproducibility)
- All timestamps are relative to current date (rolling 30-day window)
- Equipment IDs match across all fixtures (EQ-001, EQ-002, etc.)
- Job IDs are HeavyJob-specific (HJ-001, HJ-002, etc.)
- Variance patterns are realistic but exaggerated for demo visibility

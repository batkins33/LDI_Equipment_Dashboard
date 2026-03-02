# Equipment Hours Validation MVP

## Overview

The Equipment Hours Validation Hub normalizes equipment hours from multiple sources (GPS/telematics, timecards, inspections, Equipment360) into a canonical schema, computes variances, and drives an exceptions queue for operational visibility.

## Project Structure

```
02-equipment-hours-validation/
├── src/                    # Source code
│   └── config.py          # Configuration loader
├── tests/                 # Test suite
│   └── test_config.py     # Configuration tests
├── config/                # Configuration files
│   └── settings.yaml      # Default settings
├── data/                  # Data directory
│   └── db.sqlite          # SQLite database
├── specs/                 # Database schema
│   └── db_schema.sql      # Schema definition
└── README.md              # This file
```

## Database Schema

The system uses a dimensional modeling approach with three layers:

- **Dimension tables** (dim_*): Business entities (date, business unit, job, employee, equipment, cost code)
- **Fact tables** (f_*): Transactional data (timecard hours, telematics, inspections, meter readings)
- **Gold tables** (g_*): Reconciliation results, flags, and exceptions

See `specs/db_schema.sql` for complete schema definition.

## Configuration

Configuration is managed via YAML files and environment variables. The config loader (`src/config.py`) supports:

- **YAML configuration** (`config/settings.yaml`)
- **Environment variable overrides** (e.g., `LOG_LEVEL`, `DEBUG`, `DATABASE_PATH`)
- **Nested key access** using dot notation (e.g., `config.get('sources.telematics.enabled')`)

### Default Settings

```yaml
database_path: "data/db.sqlite"
log_level: "INFO"
debug: false
sources:
  telematics: enabled
  timecards: enabled
  inspections: enabled
  equipment360: enabled
validation:
  max_variance_tc_vs_gps: 2.0 hours
  max_variance_meter_vs_gps: 1.5 hours
  min_confidence_score: 70%
```

## Setup

### Prerequisites

- Python 3.8+
- SQLite3
- pip

### Installation

1. Install dependencies:
```bash
pip install pyyaml python-dotenv pytest
```

2. Database is pre-initialized at `data/db.sqlite` with schema from `specs/db_schema.sql`.

3. Configuration is loaded from `config/settings.yaml` with environment variable overrides.

## Testing

Run the configuration loader tests:

```bash
python -m pytest tests/test_config.py -v
```

All tests should pass (9/9).

## Next Steps

Phase P1 will implement:
- Data connectors for each source system
- Bronze store ingestion pipeline
- Data validation and quality checks

## References

- Executive Summary: `../src/docs/EXECUTIVE_SUMMARY.md`
- Database Schema: `specs/db_schema.sql`
- Configuration: `config/settings.yaml`

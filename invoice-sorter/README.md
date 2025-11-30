# Invoice Sorter - AP/Construction Automation Tool

## One-Liner
"Drop invoices into a folder, and the tool auto-renames and routes them into the right vendor/job folders."

## Overview
Invoice Sorter is an automation tool designed for AP clerks, small-to-mid construction office staff, and operations admin to automatically process, rename, and file invoices into the correct vendor/job folders.

### Job-to-be-Done
"I want invoices automatically named and filed so I can find them instantly and reduce manual data entry."

## Target Users
- AP (Accounts Payable) clerks
- Small-to-mid construction office staff
- Operations administrators

## Architecture

### Platform & Stack (v1)
- **Host**: Google Drive + simple web dashboard (or Workspace Add-on)
- **Backend**: Python (Cloud Run / App Engine)
- **OCR**: Google Vision API
- **LLM**: Optional - for vendor detection and field extraction from complex layouts
- **Storage**: Firestore / Google Sheets for vendor/job mapping and logs

### Tech Stack
- Python 3.9+
- Google Cloud Vision API
- Google Drive API
- Google Sheets API (optional)
- Firestore (optional)
- Flask/FastAPI for web dashboard

## Core Features (v1)

### 1. Watched Input Folder
- User configures a single "Incoming Invoices" folder in Google Drive
- Script triggers on new files (time-based or Drive event)
- Monitors for new PDF uploads

### 2. Field Extraction
Extracts key fields from each PDF invoice:
- Vendor name (or best guess)
- Invoice number
- Invoice date
- Total amount (nice-to-have)

**Extraction Strategy**:
1. Template rules for known vendors (fast path)
2. Fallback to OCR + regex/LLM parsing for unknown formats

### 3. Vendor & Job Mapping
- Configuration table (Google Sheet or Firestore):
  - `vendor_name_pattern` → `target_folder_path`
  - Example: `/Vendors/ACME/2025/Invoices`
- Automatic filename generation:
  - Pattern: `Vendor__InvoiceNumber__YYYY-MM-DD.pdf`
  - Example: `ACME__INV-12345__2025-03-15.pdf`
- File moved to mapped destination folder

### 4. Logging & Review
- Central log (Google Sheet):
  - Original filename
  - New filename
  - Detected vendor
  - Destination folder
  - Status (success / needs review)
- Unknown vendors → "Needs Review" folder
- Manual review workflow for unmatched invoices

## Data Model

### VendorMapping
```python
{
    "id": str,
    "name_pattern": str,  # string or regex
    "target_folder_id": str,  # Google Drive folder ID
    "preferred_filename_pattern": str  # optional custom pattern
}
```

### InvoiceLog
```python
{
    "id": str,
    "original_name": str,
    "new_name": str,
    "vendor_detected": str,
    "invoice_number": str,
    "invoice_date": str,
    "total_amount": float,
    "status": str,  # success, needs_review, error
    "error_message": str,  # if any
    "processed_at": datetime
}
```

## User Flow (v1)

### Setup
1. User opens web setup page or add-on sidebar
2. Choose input folder
3. Choose log destination (Google Sheet)
4. Define vendor mapping table or point to existing sheet

### Processing
1. User (or workflows) drops invoices into input folder
2. Cron/trigger processes new files:
   - Extract fields
   - Generate new filename
   - Move to destination folder
   - Log results

### Review
1. User reviews "Needs Review" folder periodically
2. Fix vendor mappings as needed
3. Re-run processing for reviewed invoices

## Non-Goals (v1)
- ❌ No deep accounting integration (QuickBooks, Spectrum, etc.)
- ❌ No line-item parsing
- ❌ No multi-company / multi-entity logic beyond simple vendor routing

## Project Structure
```
invoice-sorter/
├── src/
│   ├── core/           # Core processing logic
│   ├── extractors/     # PDF extraction and OCR
│   ├── mappers/        # Vendor mapping logic
│   └── utils/          # Utility functions
├── config/             # Configuration files
├── tests/              # Unit and integration tests
├── docs/               # Additional documentation
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Installation

```bash
# Clone repository
cd invoice-sorter

# Install dependencies
pip install -r requirements.txt

# Set up Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

## Configuration

Create a `config/settings.yaml` file:

```yaml
google_drive:
  input_folder_id: "YOUR_INPUT_FOLDER_ID"
  review_folder_id: "YOUR_REVIEW_FOLDER_ID"

google_vision:
  enabled: true

logging:
  sheet_id: "YOUR_LOG_SHEET_ID"

vendor_mapping:
  source: "sheet"  # or "firestore"
  sheet_id: "YOUR_MAPPING_SHEET_ID"
```

## Usage

```bash
# Run processor manually
python -m src.core.processor

# Run web dashboard
python -m src.web.app

# Deploy to Cloud Run
./deploy.sh
```

## Development Status
- [x] Project structure created
- [ ] Field extraction module
- [ ] Vendor mapping logic
- [ ] Google Drive integration
- [ ] Logging system
- [ ] Web dashboard
- [ ] Cloud deployment configuration

## License
MIT

## Support
For issues or questions, please contact the development team.

# Invoice Sorter - Quick Start Guide

## Prerequisites

1. **Python 3.9+** installed on your system
2. **Google Cloud Project** with the following APIs enabled:
   - Google Drive API
   - Google Sheets API
   - Google Cloud Vision API (optional, for better OCR)
3. **Google Cloud Service Account** with credentials JSON file
4. **Google Drive folder** for incoming invoices
5. **Google Drive folder** for invoices needing review
6. **Google Sheet** for logging (optional)

## Step 1: Setup

### Clone and Install

```bash
cd invoice-sorter
chmod +x setup.sh
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create a `.env` file from the example

### Activate Virtual Environment

```bash
source venv/bin/activate
```

## Step 2: Configure Google Cloud

### Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to IAM & Admin > Service Accounts
3. Create a new service account
4. Grant it the following roles:
   - Cloud Vision API User (if using Vision API)
   - Editor (for Drive and Sheets access)
5. Create and download a JSON key
6. Save it as `credentials/credentials.json`

### Enable APIs

```bash
gcloud services enable drive.googleapis.com
gcloud services enable sheets.googleapis.com
gcloud services enable vision.googleapis.com
```

### Share Folders with Service Account

1. Get your service account email from the credentials JSON file
2. Share the following folders with this email (Editor access):
   - Input folder
   - Review folder
   - Any vendor-specific folders

## Step 3: Configure Settings

### Edit `.env` file

```bash
nano .env
```

Update these values:

```env
GOOGLE_APPLICATION_CREDENTIALS=./credentials/credentials.json
INPUT_FOLDER_ID=<your_drive_folder_id>
REVIEW_FOLDER_ID=<your_review_folder_id>
LOG_SHEET_ID=<your_sheet_id>
VENDOR_MAPPING_SHEET_ID=<your_mapping_sheet_id>
```

**Finding Folder IDs:**
- Open folder in Google Drive
- URL will be: `https://drive.google.com/drive/folders/<FOLDER_ID>`
- Copy the `<FOLDER_ID>` part

**Finding Sheet IDs:**
- Open sheet in Google Sheets
- URL will be: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`
- Copy the `<SHEET_ID>` part

### Edit `config/settings.yaml`

```yaml
google_drive:
  input_folder_id: "your_input_folder_id"
  review_folder_id: "your_review_folder_id"

google_vision:
  enabled: true

logging:
  sheet_id: "your_log_sheet_id"

vendor_mapping:
  source: "sheet"
  sheet_id: "your_vendor_mapping_sheet_id"
```

## Step 4: Set Up Vendor Mappings

### Option A: Google Sheet

1. Create a new Google Sheet
2. Add columns: `id`, `name_pattern`, `target_folder_id`, `preferred_filename_pattern`
3. Add vendor mappings:

| id | name_pattern | target_folder_id | preferred_filename_pattern |
|----|--------------|------------------|----------------------------|
| 1  | ACME         | folder_id_123    |                           |
| 2  | ABC Company  | folder_id_456    |                           |

4. Share the sheet with your service account
5. Update `VENDOR_MAPPING_SHEET_ID` in `.env`

### Option B: Code (for testing)

Edit `src/core/processor.py` and modify the `_load_vendor_mappings` method to add your vendors.

## Step 5: Run the Processor

### Manual Run

```bash
python -m src.core.processor
```

### Expected Output

```
============================================================
Invoice Sorter - Processing Started
============================================================
Input folder: 1234abcd...
Review folder: 5678efgh...
Using Vision API: True
============================================================
Found 3 PDF files to process

Processing: invoice_acme_march.pdf
  Using Vision API for extraction...
  Status: success
✓ Successfully processed: ACME__INV-12345__2025-03-15.pdf

Processing: unknown_vendor.pdf
  Using PDF text extraction...
  Status: needs_review
⚠️  No mapping found for vendor: Unknown Corp

Processing: incomplete_invoice.pdf
  Using PDF text extraction...
  Status: needs_review
⚠️  Incomplete extraction (confidence: 0.40)

============================================================
Processing Complete - 3 files processed
✓ Success: 1
⚠ Needs Review: 2
✗ Errors: 0
============================================================
```

## Step 6: Review Results

### Check Google Drive

1. **Input Folder**: Successfully processed files should be moved out
2. **Vendor Folders**: Check that invoices are in the correct vendor folders with new names
3. **Review Folder**: Check for invoices that need manual review

### Check Google Sheets Log

Open your log sheet to see:
- Original filename
- New filename
- Detected vendor
- Invoice number
- Date
- Amount
- Status
- Any error messages

## Step 7: Handle "Needs Review" Items

For invoices in the "Needs Review" folder:

1. **Missing Vendor Mapping**: Add a new mapping to your vendor mapping sheet
2. **Poor OCR Quality**: Consider enabling Vision API or manual entry
3. **Unusual Format**: May need custom extraction patterns

## Automation (Optional)

### Set Up Cron Job (Local)

```bash
crontab -e
```

Add:
```
0 */6 * * * cd /path/to/invoice-sorter && source venv/bin/activate && python -m src.core.processor
```

This runs every 6 hours.

### Deploy to Google Cloud Run

```bash
chmod +x deploy.sh
./deploy.sh
```

Then set up Cloud Scheduler for periodic runs.

## Troubleshooting

### "No credentials found"
- Check `GOOGLE_APPLICATION_CREDENTIALS` path
- Ensure credentials JSON file exists

### "Failed to download file"
- Check folder permissions
- Ensure service account has access to folders

### "No mapping found for vendor"
- Add vendor to mapping sheet
- Check name_pattern matches vendor name

### "Vision API error"
- Ensure Vision API is enabled
- Check service account has Vision API User role
- Verify billing is enabled

## Next Steps

1. **Add More Vendors**: Update vendor mapping sheet
2. **Customize Filename Pattern**: Edit `config/settings.yaml`
3. **Improve Extraction**: Add custom patterns in `src/extractors/pdf_extractor.py`
4. **Set Up Automation**: Deploy to Cloud Run with Cloud Scheduler

## Support

For issues or questions:
- Check the main README.md
- Review logs in Google Sheets
- Check console output for errors

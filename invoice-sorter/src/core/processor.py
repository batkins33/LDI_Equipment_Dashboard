"""Main invoice processing orchestration"""

import os
import uuid
import tempfile
from typing import List, Optional
from datetime import datetime

from .models import (
    InvoiceStatus,
    VendorMapping,
    ExtractedInvoiceData,
    InvoiceLog,
    ProcessingConfig
)
from .config import get_config
from ..extractors import PDFExtractor, VisionExtractor
from ..mappers import VendorMapper
from ..utils import DriveClient, SheetsLogger


class InvoiceProcessor:
    """Main processor for invoice automation"""

    def __init__(
        self,
        config: Optional[ProcessingConfig] = None,
        credentials_path: Optional[str] = None
    ):
        """Initialize invoice processor

        Args:
            config: Processing configuration
            credentials_path: Path to Google Cloud credentials
        """
        self.config = config or get_config().get_processing_config()
        self.credentials_path = credentials_path

        # Initialize components
        self.drive_client = DriveClient(credentials_path)
        self.pdf_extractor = PDFExtractor()
        self.vision_extractor = VisionExtractor(credentials_path) if self.config.use_vision_api else None
        self.vendor_mapper = VendorMapper()
        self.sheets_logger = None

        if self.config.log_sheet_id:
            self.sheets_logger = SheetsLogger(
                sheet_id=self.config.log_sheet_id,
                credentials_path=credentials_path
            )

        # Load vendor mappings
        self._load_vendor_mappings()

    def _load_vendor_mappings(self) -> None:
        """Load vendor mappings from configuration"""
        # In production, this would load from Google Sheets or Firestore
        # For now, use some sample mappings
        sample_mappings = [
            VendorMapping(
                id="1",
                name_pattern="ACME",
                target_folder_id="acme_folder_id",
            ),
            VendorMapping(
                id="2",
                name_pattern="ABC Company",
                target_folder_id="abc_folder_id",
            ),
        ]
        self.vendor_mapper.mappings = sample_mappings

    def process_folder(self, folder_id: Optional[str] = None) -> List[InvoiceLog]:
        """Process all invoices in a folder

        Args:
            folder_id: Folder ID to process (uses config default if None)

        Returns:
            List of processing logs
        """
        folder_id = folder_id or self.config.input_folder_id

        if not folder_id:
            print("Error: No input folder specified")
            return []

        # List PDF files in folder
        files = self.drive_client.list_files(
            folder_id=folder_id,
            mime_type='application/pdf'
        )

        print(f"Found {len(files)} PDF files to process")

        logs = []
        for file_info in files:
            log = self.process_file(file_info)
            logs.append(log)

        return logs

    def process_file(self, file_info: dict) -> InvoiceLog:
        """Process a single invoice file

        Args:
            file_info: File metadata from Drive API

        Returns:
            InvoiceLog with processing results
        """
        file_id = file_info['id']
        original_name = file_info['name']

        print(f"\nProcessing: {original_name}")

        # Create log entry
        log = InvoiceLog(
            id=str(uuid.uuid4()),
            original_name=original_name,
            source_file_id=file_id,
            status=InvoiceStatus.PENDING
        )

        try:
            # Download file to temp location
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, original_name)

                if not self.drive_client.download_file(file_id, temp_path):
                    log.status = InvoiceStatus.ERROR
                    log.error_message = "Failed to download file"
                    self._log_result(log)
                    return log

                # Extract invoice data
                invoice_data = self._extract_data(temp_path)

                log.vendor_detected = invoice_data.vendor_name
                log.invoice_number = invoice_data.invoice_number
                log.invoice_date = invoice_data.invoice_date
                log.total_amount = invoice_data.total_amount

                # Check if extraction was successful
                if not invoice_data.is_complete():
                    print(f"⚠️  Incomplete extraction (confidence: {invoice_data.confidence:.2f})")
                    log.status = InvoiceStatus.NEEDS_REVIEW
                    log.error_message = "Incomplete invoice data extraction"

                    # Move to review folder
                    if self.config.review_folder_id:
                        self.drive_client.move_file(
                            file_id=file_id,
                            destination_folder_id=self.config.review_folder_id
                        )
                        log.destination_folder_id = self.config.review_folder_id

                    self._log_result(log)
                    return log

                # Find vendor mapping
                mapping = self.vendor_mapper.find_mapping(invoice_data.vendor_name)

                if not mapping:
                    print(f"⚠️  No mapping found for vendor: {invoice_data.vendor_name}")
                    log.status = InvoiceStatus.NEEDS_REVIEW
                    log.error_message = f"No mapping for vendor: {invoice_data.vendor_name}"

                    # Move to review folder
                    if self.config.review_folder_id:
                        self.drive_client.move_file(
                            file_id=file_id,
                            destination_folder_id=self.config.review_folder_id
                        )
                        log.destination_folder_id = self.config.review_folder_id

                    self._log_result(log)
                    return log

                # Generate new filename
                new_filename = self.vendor_mapper.generate_filename(
                    invoice_data=invoice_data,
                    mapping=mapping,
                    pattern=self.config.filename_pattern
                )

                log.new_name = new_filename

                # Move and rename file
                success = self.drive_client.move_file(
                    file_id=file_id,
                    destination_folder_id=mapping.target_folder_id,
                    new_name=new_filename
                )

                if success:
                    log.status = InvoiceStatus.SUCCESS
                    log.destination_folder_id = mapping.target_folder_id
                    print(f"✓ Successfully processed: {new_filename}")
                else:
                    log.status = InvoiceStatus.ERROR
                    log.error_message = "Failed to move file"
                    print(f"✗ Failed to move file")

        except Exception as e:
            log.status = InvoiceStatus.ERROR
            log.error_message = str(e)
            print(f"✗ Error processing file: {e}")

        # Log result
        self._log_result(log)
        return log

    def _extract_data(self, pdf_path: str) -> ExtractedInvoiceData:
        """Extract data from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            ExtractedInvoiceData
        """
        # Try Vision API first if enabled
        if self.config.use_vision_api and self.vision_extractor:
            print("  Using Vision API for extraction...")
            data = self.vision_extractor.extract(pdf_path)

            # If Vision API extraction is good enough, return it
            if data.confidence > 0.7:
                return data

        # Fallback to PDF text extraction
        print("  Using PDF text extraction...")
        return self.pdf_extractor.extract(pdf_path)

    def _log_result(self, log: InvoiceLog) -> None:
        """Log processing result

        Args:
            log: InvoiceLog to write
        """
        # Log to console
        print(f"  Status: {log.status.value if hasattr(log.status, 'value') else log.status}")

        # Log to Google Sheets if configured
        if self.sheets_logger:
            try:
                self.sheets_logger.log(log)
            except Exception as e:
                print(f"  Warning: Failed to log to sheets: {e}")

    def run(self) -> None:
        """Run the processor once"""
        print("=" * 60)
        print("Invoice Sorter - Processing Started")
        print("=" * 60)
        print(f"Input folder: {self.config.input_folder_id}")
        print(f"Review folder: {self.config.review_folder_id}")
        print(f"Using Vision API: {self.config.use_vision_api}")
        print("=" * 60)

        logs = self.process_folder()

        print("\n" + "=" * 60)
        print(f"Processing Complete - {len(logs)} files processed")

        # Summary
        success = sum(1 for log in logs if log.status == InvoiceStatus.SUCCESS)
        needs_review = sum(1 for log in logs if log.status == InvoiceStatus.NEEDS_REVIEW)
        errors = sum(1 for log in logs if log.status == InvoiceStatus.ERROR)

        print(f"✓ Success: {success}")
        print(f"⚠ Needs Review: {needs_review}")
        print(f"✗ Errors: {errors}")
        print("=" * 60)


def main():
    """Main entry point"""
    processor = InvoiceProcessor()
    processor.run()


if __name__ == "__main__":
    main()

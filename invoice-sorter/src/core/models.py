"""Data models for Invoice Sorter"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class InvoiceStatus(Enum):
    """Status of invoice processing"""
    SUCCESS = "success"
    NEEDS_REVIEW = "needs_review"
    ERROR = "error"
    PENDING = "pending"


@dataclass
class VendorMapping:
    """Vendor mapping configuration

    Attributes:
        id: Unique identifier
        name_pattern: String or regex pattern to match vendor names
        target_folder_id: Google Drive folder ID for this vendor
        preferred_filename_pattern: Optional custom filename pattern
    """
    id: str
    name_pattern: str
    target_folder_id: str
    preferred_filename_pattern: Optional[str] = None

    def matches(self, vendor_name: str) -> bool:
        """Check if vendor name matches this mapping"""
        import re
        # Try exact match first
        if self.name_pattern.lower() in vendor_name.lower():
            return True
        # Try regex match
        try:
            return bool(re.search(self.name_pattern, vendor_name, re.IGNORECASE))
        except re.error:
            return False


@dataclass
class ExtractedInvoiceData:
    """Data extracted from an invoice

    Attributes:
        vendor_name: Detected vendor name
        invoice_number: Invoice number
        invoice_date: Invoice date
        total_amount: Total amount (optional)
        confidence: Confidence score for extraction (0-1)
        raw_text: Raw extracted text
    """
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    total_amount: Optional[float] = None
    confidence: float = 0.0
    raw_text: str = ""

    def is_complete(self) -> bool:
        """Check if essential fields are extracted"""
        return bool(self.vendor_name and self.invoice_number)


@dataclass
class InvoiceLog:
    """Log entry for processed invoice

    Attributes:
        id: Unique identifier
        original_name: Original filename
        new_name: New filename after processing
        vendor_detected: Detected vendor name
        invoice_number: Extracted invoice number
        invoice_date: Extracted invoice date
        total_amount: Extracted total amount
        status: Processing status
        error_message: Error message if processing failed
        processed_at: Timestamp when processed
        source_file_id: Original Google Drive file ID
        destination_file_id: Destination Google Drive file ID
        destination_folder_id: Destination folder ID
    """
    id: str
    original_name: str
    vendor_detected: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    total_amount: Optional[float] = None
    status: InvoiceStatus = InvoiceStatus.PENDING
    error_message: Optional[str] = None
    processed_at: datetime = field(default_factory=datetime.now)
    new_name: Optional[str] = None
    source_file_id: Optional[str] = None
    destination_file_id: Optional[str] = None
    destination_folder_id: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for logging"""
        return {
            "id": self.id,
            "original_name": self.original_name,
            "new_name": self.new_name,
            "vendor_detected": self.vendor_detected,
            "invoice_number": self.invoice_number,
            "invoice_date": self.invoice_date,
            "total_amount": self.total_amount,
            "status": self.status.value if isinstance(self.status, InvoiceStatus) else self.status,
            "error_message": self.error_message,
            "processed_at": self.processed_at.isoformat() if isinstance(self.processed_at, datetime) else self.processed_at,
            "source_file_id": self.source_file_id,
            "destination_file_id": self.destination_file_id,
            "destination_folder_id": self.destination_folder_id,
        }


@dataclass
class ProcessingConfig:
    """Configuration for invoice processing

    Attributes:
        input_folder_id: Google Drive folder ID to monitor
        review_folder_id: Google Drive folder ID for unmatched invoices
        log_sheet_id: Google Sheets ID for logging
        vendor_mapping_sheet_id: Google Sheets ID for vendor mappings
        use_vision_api: Whether to use Google Vision API
        use_llm: Whether to use LLM for extraction
        filename_pattern: Default filename pattern
    """
    input_folder_id: str
    review_folder_id: str
    log_sheet_id: Optional[str] = None
    vendor_mapping_sheet_id: Optional[str] = None
    use_vision_api: bool = True
    use_llm: bool = False
    filename_pattern: str = "{vendor}__{invoice_number}__{date}.pdf"

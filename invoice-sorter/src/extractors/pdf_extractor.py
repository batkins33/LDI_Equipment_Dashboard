"""PDF text extraction and parsing"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import PyPDF2

from ..core.models import ExtractedInvoiceData


class PDFExtractor:
    """Extract text and data from PDF invoices"""

    def __init__(self):
        """Initialize PDF extractor"""
        self.vendor_patterns = self._load_vendor_patterns()
        self.date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or DD-MM-YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',  # YYYY-MM-DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',  # Month DD, YYYY
        ]
        self.invoice_number_patterns = [
            r'(?:invoice|inv)[\s#:]*([A-Z0-9-]+)',
            r'(?:invoice number|inv no|invoice no)[\s#:]*([A-Z0-9-]+)',
            r'#([A-Z0-9-]{5,})',
        ]
        self.amount_patterns = [
            r'\$\s*([0-9,]+\.?\d{0,2})',
            r'(?:total|amount due|balance)[\s:$]*([0-9,]+\.?\d{0,2})',
        ]

    def _load_vendor_patterns(self) -> Dict[str, str]:
        """Load vendor name patterns

        Returns:
            Dictionary of vendor patterns
        """
        # In production, this could load from a config file
        return {
            'acme': r'ACME\s+(?:Corp|Corporation|Inc)?',
            'abc': r'ABC\s+(?:Company|Co\.)?',
            'xyz': r'XYZ\s+(?:Ltd|Limited)?',
        }

    def extract_text(self, pdf_path: str) -> str:
        """Extract raw text from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")

        return text

    def extract_vendor_name(self, text: str) -> Optional[str]:
        """Extract vendor name from text

        Args:
            text: Raw text from invoice

        Returns:
            Vendor name if found
        """
        # Try known vendor patterns first
        for vendor, pattern in self.vendor_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        # Fallback: look for company names in first few lines
        lines = text.split('\n')[:5]
        for line in lines:
            # Look for lines with Inc, LLC, Corp, etc.
            if re.search(r'\b(?:Inc|LLC|Corp|Corporation|Ltd|Limited|Co\.)\b', line, re.IGNORECASE):
                return line.strip()

        return None

    def extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number from text

        Args:
            text: Raw text from invoice

        Returns:
            Invoice number if found
        """
        for pattern in self.invoice_number_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Return the captured group
                return match.group(1) if match.lastindex else match.group(0)

        return None

    def extract_invoice_date(self, text: str) -> Optional[str]:
        """Extract invoice date from text

        Args:
            text: Raw text from invoice

        Returns:
            Invoice date in YYYY-MM-DD format if found
        """
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(0)
                # Try to parse and standardize the date
                try:
                    # Try various date formats
                    for fmt in ['%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d', '%B %d, %Y', '%b %d, %Y']:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            return date_obj.strftime('%Y-%m-%d')
                        except ValueError:
                            continue
                except Exception:
                    pass

                # Return as-is if parsing fails
                return date_str

        return None

    def extract_total_amount(self, text: str) -> Optional[float]:
        """Extract total amount from text

        Args:
            text: Raw text from invoice

        Returns:
            Total amount if found
        """
        amounts = []
        for pattern in self.amount_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    amount_str = match.group(1)
                    # Remove commas and convert to float
                    amount = float(amount_str.replace(',', ''))
                    amounts.append(amount)
                except (ValueError, IndexError):
                    continue

        # Return the largest amount found (likely the total)
        return max(amounts) if amounts else None

    def extract(self, pdf_path: str) -> ExtractedInvoiceData:
        """Extract all invoice data from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            ExtractedInvoiceData with extracted fields
        """
        # Extract raw text
        text = self.extract_text(pdf_path)

        # Extract individual fields
        vendor_name = self.extract_vendor_name(text)
        invoice_number = self.extract_invoice_number(text)
        invoice_date = self.extract_invoice_date(text)
        total_amount = self.extract_total_amount(text)

        # Calculate confidence based on what was found
        confidence = 0.0
        if vendor_name:
            confidence += 0.4
        if invoice_number:
            confidence += 0.4
        if invoice_date:
            confidence += 0.1
        if total_amount:
            confidence += 0.1

        return ExtractedInvoiceData(
            vendor_name=vendor_name,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            total_amount=total_amount,
            confidence=confidence,
            raw_text=text
        )

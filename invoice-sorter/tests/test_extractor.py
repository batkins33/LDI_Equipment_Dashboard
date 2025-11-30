"""Tests for PDF extraction"""

import pytest
from src.extractors import PDFExtractor
from src.core.models import ExtractedInvoiceData


class TestPDFExtractor:
    """Test PDF extraction functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.extractor = PDFExtractor()

    def test_extract_vendor_name_from_text(self):
        """Test vendor name extraction"""
        text = """
        ACME Corporation
        123 Main Street
        Invoice #12345
        """
        vendor = self.extractor.extract_vendor_name(text)
        assert vendor is not None
        assert "ACME" in vendor

    def test_extract_invoice_number(self):
        """Test invoice number extraction"""
        text = "Invoice Number: INV-12345"
        number = self.extractor.extract_invoice_number(text)
        assert number == "INV-12345"

    def test_extract_invoice_number_alternate_format(self):
        """Test invoice number extraction with alternate format"""
        text = "Invoice #ABC-9876"
        number = self.extractor.extract_invoice_number(text)
        assert "ABC-9876" in number

    def test_extract_invoice_date(self):
        """Test date extraction"""
        text = "Date: 03/15/2025"
        date = self.extractor.extract_invoice_date(text)
        assert date == "2025-03-15"

    def test_extract_total_amount(self):
        """Test amount extraction"""
        text = """
        Subtotal: $100.00
        Tax: $10.00
        Total: $110.00
        """
        amount = self.extractor.extract_total_amount(text)
        assert amount == 110.00

    def test_extract_multiple_amounts(self):
        """Test that largest amount is returned"""
        text = """
        Item 1: $50.00
        Item 2: $75.00
        Total: $125.00
        """
        amount = self.extractor.extract_total_amount(text)
        assert amount == 125.00

    def test_extract_with_no_data(self):
        """Test extraction with empty text"""
        text = ""
        data = ExtractedInvoiceData()
        assert not data.is_complete()
        assert data.confidence == 0.0

    def test_extract_with_partial_data(self):
        """Test extraction with incomplete data"""
        text = "Invoice #12345"
        number = self.extractor.extract_invoice_number(text)
        vendor = self.extractor.extract_vendor_name(text)

        assert number == "12345"
        assert vendor is None

    def test_date_formats(self):
        """Test various date formats"""
        test_cases = [
            ("03/15/2025", "2025-03-15"),
            ("2025-03-15", "2025-03-15"),
            ("March 15, 2025", "2025-03-15"),
            ("Mar 15, 2025", "2025-03-15"),
        ]

        for input_text, expected in test_cases:
            date = self.extractor.extract_invoice_date(input_text)
            assert date == expected, f"Failed for input: {input_text}"


class TestExtractedInvoiceData:
    """Test ExtractedInvoiceData model"""

    def test_is_complete_with_full_data(self):
        """Test completeness check with full data"""
        data = ExtractedInvoiceData(
            vendor_name="ACME Corp",
            invoice_number="INV-123",
            invoice_date="2025-03-15",
            total_amount=100.00
        )
        assert data.is_complete()

    def test_is_complete_with_minimal_data(self):
        """Test completeness check with minimal required data"""
        data = ExtractedInvoiceData(
            vendor_name="ACME Corp",
            invoice_number="INV-123"
        )
        assert data.is_complete()

    def test_is_incomplete_missing_vendor(self):
        """Test incompleteness when missing vendor"""
        data = ExtractedInvoiceData(
            invoice_number="INV-123"
        )
        assert not data.is_complete()

    def test_is_incomplete_missing_invoice_number(self):
        """Test incompleteness when missing invoice number"""
        data = ExtractedInvoiceData(
            vendor_name="ACME Corp"
        )
        assert not data.is_complete()

    def test_confidence_calculation(self):
        """Test confidence score"""
        data = ExtractedInvoiceData(
            vendor_name="ACME Corp",
            invoice_number="INV-123",
            confidence=0.8
        )
        assert data.confidence == 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

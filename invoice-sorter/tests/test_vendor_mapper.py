"""Tests for vendor mapping"""

import pytest
from src.mappers import VendorMapper
from src.core.models import VendorMapping, ExtractedInvoiceData


class TestVendorMapper:
    """Test vendor mapping functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mapper = VendorMapper()
        self.mapper.add_mapping(
            VendorMapping(
                id="1",
                name_pattern="ACME",
                target_folder_id="folder_acme"
            )
        )
        self.mapper.add_mapping(
            VendorMapping(
                id="2",
                name_pattern="ABC Company",
                target_folder_id="folder_abc"
            )
        )

    def test_find_mapping_exact_match(self):
        """Test finding mapping with exact match"""
        mapping = self.mapper.find_mapping("ACME Corporation")
        assert mapping is not None
        assert mapping.id == "1"
        assert mapping.target_folder_id == "folder_acme"

    def test_find_mapping_partial_match(self):
        """Test finding mapping with partial match"""
        mapping = self.mapper.find_mapping("ABC Company Ltd")
        assert mapping is not None
        assert mapping.id == "2"

    def test_find_mapping_case_insensitive(self):
        """Test case-insensitive matching"""
        mapping = self.mapper.find_mapping("acme corp")
        assert mapping is not None
        assert mapping.id == "1"

    def test_find_mapping_no_match(self):
        """Test no mapping found"""
        mapping = self.mapper.find_mapping("Unknown Vendor")
        assert mapping is None

    def test_find_mapping_empty_vendor(self):
        """Test with empty vendor name"""
        mapping = self.mapper.find_mapping("")
        assert mapping is None

    def test_generate_filename_default_pattern(self):
        """Test filename generation with default pattern"""
        data = ExtractedInvoiceData(
            vendor_name="ACME Corp",
            invoice_number="INV-12345",
            invoice_date="2025-03-15"
        )
        filename = self.mapper.generate_filename(data)
        assert filename == "ACME_Corp__INV-12345__2025-03-15.pdf"

    def test_generate_filename_custom_pattern(self):
        """Test filename generation with custom pattern"""
        data = ExtractedInvoiceData(
            vendor_name="ACME Corp",
            invoice_number="INV-12345",
            invoice_date="2025-03-15",
            total_amount=100.50
        )
        pattern = "{vendor}_{date}_{invoice_number}_{amount}.pdf"
        filename = self.mapper.generate_filename(data, pattern=pattern)
        assert filename == "ACME_Corp_2025-03-15_INV-12345_100.5.pdf"

    def test_sanitize_filename(self):
        """Test filename sanitization"""
        dirty_name = "ACME/Corp\\Inc:2025"
        clean = self.mapper._sanitize_filename(dirty_name)
        assert "/" not in clean
        assert "\\" not in clean
        assert ":" not in clean

    def test_sanitize_filename_spaces(self):
        """Test space replacement in filename"""
        name = "ACME   Corporation"
        clean = self.mapper._sanitize_filename(name)
        assert clean == "ACME_Corporation"

    def test_format_date_iso_format(self):
        """Test date formatting with ISO format"""
        date = self.mapper._format_date("2025-03-15")
        assert date == "2025-03-15"

    def test_format_date_us_format(self):
        """Test date formatting with US format"""
        date = self.mapper._format_date("03/15/2025")
        assert date == "2025-03-15"

    def test_format_date_none(self):
        """Test date formatting with None returns current date"""
        date = self.mapper._format_date(None)
        assert len(date) == 10  # YYYY-MM-DD format
        assert date.count("-") == 2

    def test_get_destination_folder(self):
        """Test getting destination folder"""
        data = ExtractedInvoiceData(vendor_name="ACME Corp")
        folder = self.mapper.get_destination_folder(data)
        assert folder == "folder_acme"

    def test_get_destination_folder_no_mapping(self):
        """Test getting destination folder with no mapping"""
        data = ExtractedInvoiceData(vendor_name="Unknown Vendor")
        folder = self.mapper.get_destination_folder(data)
        assert folder is None

    def test_load_from_dict(self):
        """Test loading mappings from dictionary"""
        data = [
            {
                "id": "3",
                "name_pattern": "XYZ Corp",
                "target_folder_id": "folder_xyz"
            }
        ]
        mapper = VendorMapper()
        mapper.load_from_dict(data)

        assert len(mapper.mappings) == 1
        assert mapper.mappings[0].id == "3"
        assert mapper.mappings[0].name_pattern == "XYZ Corp"

    def test_get_mappings_summary(self):
        """Test getting mappings summary"""
        summary = self.mapper.get_mappings_summary()
        assert len(summary) == 2
        assert summary[0]["id"] == "1"
        assert summary[1]["pattern"] == "ABC Company"


class TestVendorMapping:
    """Test VendorMapping model"""

    def test_matches_exact(self):
        """Test exact pattern matching"""
        mapping = VendorMapping(
            id="1",
            name_pattern="ACME",
            target_folder_id="folder_1"
        )
        assert mapping.matches("ACME Corporation")
        assert mapping.matches("ACME Inc")

    def test_matches_case_insensitive(self):
        """Test case-insensitive matching"""
        mapping = VendorMapping(
            id="1",
            name_pattern="ACME",
            target_folder_id="folder_1"
        )
        assert mapping.matches("acme corp")
        assert mapping.matches("Acme Corporation")

    def test_matches_regex(self):
        """Test regex pattern matching"""
        mapping = VendorMapping(
            id="1",
            name_pattern=r"ACME\s+(Corp|Inc)",
            target_folder_id="folder_1"
        )
        assert mapping.matches("ACME Corp")
        assert mapping.matches("ACME Inc")
        assert not mapping.matches("ACME Ltd")

    def test_no_match(self):
        """Test no match"""
        mapping = VendorMapping(
            id="1",
            name_pattern="ACME",
            target_folder_id="folder_1"
        )
        assert not mapping.matches("ABC Company")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

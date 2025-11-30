"""Vendor mapping and routing logic"""

import re
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..core.models import VendorMapping, ExtractedInvoiceData


class VendorMapper:
    """Map vendors to destination folders and generate filenames"""

    def __init__(self, mappings: Optional[List[VendorMapping]] = None):
        """Initialize vendor mapper

        Args:
            mappings: List of vendor mappings
        """
        self.mappings = mappings or []

    def add_mapping(self, mapping: VendorMapping) -> None:
        """Add a vendor mapping

        Args:
            mapping: VendorMapping to add
        """
        self.mappings.append(mapping)

    def load_from_dict(self, data: List[Dict[str, Any]]) -> None:
        """Load mappings from dictionary list

        Args:
            data: List of mapping dictionaries
        """
        self.mappings = [
            VendorMapping(
                id=m.get("id", ""),
                name_pattern=m.get("name_pattern", ""),
                target_folder_id=m.get("target_folder_id", ""),
                preferred_filename_pattern=m.get("preferred_filename_pattern")
            )
            for m in data
        ]

    def find_mapping(self, vendor_name: str) -> Optional[VendorMapping]:
        """Find vendor mapping for given vendor name

        Args:
            vendor_name: Vendor name to match

        Returns:
            VendorMapping if found, None otherwise
        """
        if not vendor_name:
            return None

        # Try each mapping in order
        for mapping in self.mappings:
            if mapping.matches(vendor_name):
                return mapping

        return None

    def generate_filename(
        self,
        invoice_data: ExtractedInvoiceData,
        mapping: Optional[VendorMapping] = None,
        pattern: Optional[str] = None
    ) -> str:
        """Generate filename for invoice

        Args:
            invoice_data: Extracted invoice data
            mapping: Vendor mapping (optional)
            pattern: Filename pattern override (optional)

        Returns:
            Generated filename
        """
        # Determine which pattern to use
        if pattern:
            filename_pattern = pattern
        elif mapping and mapping.preferred_filename_pattern:
            filename_pattern = mapping.preferred_filename_pattern
        else:
            # Default pattern
            filename_pattern = "{vendor}__{invoice_number}__{date}.pdf"

        # Sanitize values for filename
        vendor = self._sanitize_filename(invoice_data.vendor_name or "Unknown")
        invoice_number = self._sanitize_filename(invoice_data.invoice_number or "NoNumber")
        date = self._format_date(invoice_data.invoice_date)

        # Format filename
        try:
            filename = filename_pattern.format(
                vendor=vendor,
                invoice_number=invoice_number,
                date=date,
                amount=invoice_data.total_amount or 0
            )
        except KeyError as e:
            # Fallback to default if pattern has issues
            print(f"Error formatting filename: {e}. Using default pattern.")
            filename = f"{vendor}__{invoice_number}__{date}.pdf"

        return filename

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use in filename

        Args:
            name: String to sanitize

        Returns:
            Sanitized string
        """
        # Remove/replace invalid characters
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        # Remove multiple consecutive underscores
        name = re.sub(r'_+', '_', name)
        # Remove leading/trailing underscores
        name = name.strip('_')
        # Limit length
        return name[:100]

    def _format_date(self, date_str: Optional[str]) -> str:
        """Format date string for filename

        Args:
            date_str: Date string

        Returns:
            Formatted date (YYYY-MM-DD) or current date if invalid
        """
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')

        # If already in YYYY-MM-DD format, return as-is
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str

        # Try to parse and reformat
        try:
            for fmt in ['%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d', '%B %d, %Y', '%b %d, %Y']:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        except Exception:
            pass

        # Fallback to current date
        return datetime.now().strftime('%Y-%m-%d')

    def get_destination_folder(
        self,
        invoice_data: ExtractedInvoiceData
    ) -> Optional[str]:
        """Get destination folder ID for invoice

        Args:
            invoice_data: Extracted invoice data

        Returns:
            Folder ID if vendor mapped, None otherwise
        """
        if not invoice_data.vendor_name:
            return None

        mapping = self.find_mapping(invoice_data.vendor_name)
        if mapping:
            return mapping.target_folder_id

        return None

    def get_mappings_summary(self) -> List[Dict[str, str]]:
        """Get summary of all mappings

        Returns:
            List of mapping summaries
        """
        return [
            {
                "id": m.id,
                "pattern": m.name_pattern,
                "folder_id": m.target_folder_id,
            }
            for m in self.mappings
        ]

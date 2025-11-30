"""Google Sheets logger for invoice processing logs"""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account

from ..core.models import InvoiceLog


class SheetsLogger:
    """Logger that writes to Google Sheets"""

    def __init__(
        self,
        sheet_id: str,
        credentials_path: Optional[str] = None,
        sheet_name: str = "Invoice Log"
    ):
        """Initialize Sheets logger

        Args:
            sheet_id: Google Sheets ID
            credentials_path: Path to service account credentials JSON
            sheet_name: Name of the sheet tab
        """
        self.sheet_id = sheet_id
        self.sheet_name = sheet_name
        self.credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.service = self._get_service()
        self._ensure_headers()

    def _get_service(self):
        """Get Sheets API service instance"""
        if self.credentials_path and os.path.exists(self.credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            return build('sheets', 'v4', credentials=credentials)
        else:
            print("Warning: No credentials found. Sheets logging will fail.")
            return None

    def _ensure_headers(self) -> None:
        """Ensure the sheet has proper headers"""
        if not self.service:
            return

        try:
            # Check if sheet exists
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()

            sheets = spreadsheet.get('sheets', [])
            sheet_exists = any(s['properties']['title'] == self.sheet_name for s in sheets)

            if not sheet_exists:
                # Create the sheet
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.sheet_id,
                    body={
                        'requests': [{
                            'addSheet': {
                                'properties': {
                                    'title': self.sheet_name
                                }
                            }
                        }]
                    }
                ).execute()

            # Check if headers exist
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=f'{self.sheet_name}!A1:K1'
            ).execute()

            values = result.get('values', [])

            if not values or len(values[0]) == 0:
                # Add headers
                headers = [
                    'ID',
                    'Timestamp',
                    'Original Filename',
                    'New Filename',
                    'Vendor',
                    'Invoice Number',
                    'Invoice Date',
                    'Amount',
                    'Status',
                    'Error Message',
                    'Destination Folder ID'
                ]

                self.service.spreadsheets().values().update(
                    spreadsheetId=self.sheet_id,
                    range=f'{self.sheet_name}!A1:K1',
                    valueInputOption='RAW',
                    body={'values': [headers]}
                ).execute()

        except Exception as e:
            print(f"Error ensuring headers: {e}")

    def log(self, invoice_log: InvoiceLog) -> bool:
        """Log invoice processing result

        Args:
            invoice_log: InvoiceLog to write

        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False

        try:
            # Convert log to row
            row = [
                invoice_log.id,
                invoice_log.processed_at.isoformat() if isinstance(invoice_log.processed_at, datetime) else invoice_log.processed_at,
                invoice_log.original_name,
                invoice_log.new_name or "",
                invoice_log.vendor_detected or "",
                invoice_log.invoice_number or "",
                invoice_log.invoice_date or "",
                invoice_log.total_amount or "",
                invoice_log.status.value if hasattr(invoice_log.status, 'value') else invoice_log.status,
                invoice_log.error_message or "",
                invoice_log.destination_folder_id or ""
            ]

            # Append row
            self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=f'{self.sheet_name}!A:K',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row]}
            ).execute()

            return True

        except Exception as e:
            print(f"Error logging to sheets: {e}")
            return False

    def log_batch(self, logs: List[InvoiceLog]) -> bool:
        """Log multiple invoice processing results

        Args:
            logs: List of InvoiceLogs to write

        Returns:
            True if successful, False otherwise
        """
        if not self.service or not logs:
            return False

        try:
            # Convert logs to rows
            rows = []
            for log in logs:
                row = [
                    log.id,
                    log.processed_at.isoformat() if isinstance(log.processed_at, datetime) else log.processed_at,
                    log.original_name,
                    log.new_name or "",
                    log.vendor_detected or "",
                    log.invoice_number or "",
                    log.invoice_date or "",
                    log.total_amount or "",
                    log.status.value if hasattr(log.status, 'value') else log.status,
                    log.error_message or "",
                    log.destination_folder_id or ""
                ]
                rows.append(row)

            # Append rows
            self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=f'{self.sheet_name}!A:K',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': rows}
            ).execute()

            return True

        except Exception as e:
            print(f"Error logging batch to sheets: {e}")
            return False

    def get_logs(
        self,
        limit: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get logs from sheet

        Args:
            limit: Maximum number of logs to return
            status_filter: Filter by status

        Returns:
            List of log dictionaries
        """
        if not self.service:
            return []

        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=f'{self.sheet_name}!A2:K'  # Skip header row
            ).execute()

            values = result.get('values', [])

            logs = []
            for row in values:
                if len(row) < 9:
                    continue

                log = {
                    'id': row[0] if len(row) > 0 else '',
                    'timestamp': row[1] if len(row) > 1 else '',
                    'original_name': row[2] if len(row) > 2 else '',
                    'new_name': row[3] if len(row) > 3 else '',
                    'vendor': row[4] if len(row) > 4 else '',
                    'invoice_number': row[5] if len(row) > 5 else '',
                    'invoice_date': row[6] if len(row) > 6 else '',
                    'amount': row[7] if len(row) > 7 else '',
                    'status': row[8] if len(row) > 8 else '',
                    'error_message': row[9] if len(row) > 9 else '',
                    'destination_folder_id': row[10] if len(row) > 10 else ''
                }

                if status_filter and log['status'] != status_filter:
                    continue

                logs.append(log)

            # Apply limit
            if limit:
                logs = logs[:limit]

            return logs

        except Exception as e:
            print(f"Error getting logs: {e}")
            return []

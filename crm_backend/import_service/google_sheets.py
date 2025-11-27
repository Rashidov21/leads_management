"""Google Sheets integration service."""
import os
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from django.conf import settings


class GoogleSheetsService:
    """Service for connecting to and reading from Google Sheets."""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def __init__(self, credentials_file: Optional[str] = None):
        """
        Initialize Google Sheets service.
        
        Args:
            credentials_file: Path to service account credentials JSON file
        """
        self.credentials_file = credentials_file or settings.GOOGLE_SHEETS_CREDENTIALS_FILE
        self.service = self._create_service()
    
    def _create_service(self):
        """Create and return Google Sheets API service."""
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=self.SCOPES
            )
            
            # Try using google-api-python-client
            try:
                from googleapiclient.discovery import build
                return build('sheets', 'v4', credentials=credentials)
            except ImportError:
                # Fallback if google-api-python-client not available
                return None
        except Exception as e:
            print(f"Error creating Google Sheets service: {e}")
            return None
    
    def read_sheet(self, sheet_id: str, range_name: str = 'Sheet1!A:B') -> List[List[str]]:
        """
        Read data from a Google Sheet.
        
        Args:
            sheet_id: Google Sheet ID
            range_name: Range to read (e.g., 'Sheet1!A1:B100')
        
        Returns:
            List of rows with data
        """
        if not self.service:
            return []
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            return result.get('values', [])
        except Exception as e:
            print(f"Error reading sheet: {e}")
            return []
    
    def parse_sheet_data(self, sheet_data: List[List[str]]) -> List[Dict]:
        """
        Parse raw sheet data into lead dictionaries.
        
        Expects:
            Row 1: Headers (Name, Phone)
            Rows 2+: Data
        
        Returns:
            List of dictionaries with 'name' and 'phone' keys
        """
        if len(sheet_data) < 2:
            return []
        
        headers = sheet_data[0]
        leads = []
        
        # Find column indices
        name_idx = None
        phone_idx = None
        
        for idx, header in enumerate(headers):
            header_lower = header.lower().strip()
            if 'name' in header_lower:
                name_idx = idx
            elif 'phone' in header_lower or 'mobile' in header_lower:
                phone_idx = idx
        
        if name_idx is None or phone_idx is None:
            return []
        
        # Parse data rows
        for row in sheet_data[1:]:
            if len(row) > max(name_idx, phone_idx):
                lead = {
                    'name': row[name_idx].strip() if name_idx < len(row) else '',
                    'phone': row[phone_idx].strip() if phone_idx < len(row) else '',
                }
                if lead['name'] and lead['phone']:
                    leads.append(lead)
        
        return leads

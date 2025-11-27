"""
Services for leads app, including Google Sheets sync.
"""
from django.conf import settings
from django.utils import timezone
from typing import List, Dict, Optional
import gspread
from google.oauth2.service_account import Credentials
from .models import Lead, Seller


class GoogleSheetsSyncService:
    """Service for syncing leads with Google Sheets."""
    
    def __init__(self):
        """Initialize the Google Sheets service."""
        self.credentials_file = settings.GOOGLE_SHEETS_CREDENTIALS_FILE
        self.spreadsheet_id = settings.GOOGLE_SHEETS_SPREADSHEET_ID
        self.worksheet_name = settings.GOOGLE_SHEETS_WORKSHEET_NAME
        
        if not self.credentials_file or not self.spreadsheet_id:
            raise ValueError("Google Sheets credentials and spreadsheet ID must be configured")
        
        # Authenticate
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file(
            self.credentials_file,
            scopes=scope
        )
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        self.worksheet = self.spreadsheet.worksheet(self.worksheet_name)
    
    def sync_from_sheets(self, auto_assign_seller: Optional[Seller] = None) -> Dict[str, int]:
        """
        Sync leads from Google Sheets to database.
        
        Expected sheet format:
        Row 1: Headers (Name, Email, Phone, Company, Notes, Status, Seller, etc.)
        Row 2+: Data rows
        
        Returns dict with sync statistics.
        """
        try:
            # Get all values from the sheet
            all_values = self.worksheet.get_all_values()
            
            if not all_values:
                return {'created': 0, 'updated': 0, 'errors': 0}
            
            headers = all_values[0]
            data_rows = all_values[1:]
            
            # Map headers to indices
            header_map = {h.lower().strip(): i for i, h in enumerate(headers)}
            
            # Required fields
            name_idx = header_map.get('name', 0)
            email_idx = header_map.get('email', -1)
            phone_idx = header_map.get('phone', -1)
            company_idx = header_map.get('company', -1)
            notes_idx = header_map.get('notes', -1)
            status_idx = header_map.get('status', -1)
            seller_idx = header_map.get('seller', -1)
            
            created = 0
            updated = 0
            errors = 0
            
            for row_num, row in enumerate(data_rows, start=2):  # Start at 2 (row 1 is headers)
                try:
                    if not row or len(row) <= name_idx or not row[name_idx]:
                        continue  # Skip empty rows
                    
                    name = row[name_idx].strip()
                    email = row[email_idx].strip() if email_idx >= 0 and len(row) > email_idx else ''
                    phone = row[phone_idx].strip() if phone_idx >= 0 and len(row) > phone_idx else ''
                    company = row[company_idx].strip() if company_idx >= 0 and len(row) > company_idx else ''
                    notes = row[notes_idx].strip() if notes_idx >= 0 and len(row) > notes_idx else ''
                    status = row[status_idx].strip().lower() if status_idx >= 0 and len(row) > status_idx else 'new'
                    seller_name = row[seller_idx].strip() if seller_idx >= 0 and len(row) > seller_idx else ''
                    
                    # Validate status
                    valid_statuses = [s[0] for s in Lead.STATUS_CHOICES]
                    if status not in valid_statuses:
                        status = 'new'
                    
                    # Find or assign seller
                    seller = None
                    if seller_name:
                        # Try to find seller by username or full name
                        try:
                            from django.contrib.auth.models import User
                            user = User.objects.filter(
                                username__iexact=seller_name
                            ).first() or User.objects.filter(
                                first_name__icontains=seller_name
                            ).first()
                            if user and hasattr(user, 'seller_profile'):
                                seller = user.seller_profile
                        except:
                            pass
                    
                    if not seller and auto_assign_seller:
                        seller = auto_assign_seller
                    
                    # Create or update lead
                    lead, created_flag = Lead.objects.update_or_create(
                        sheets_row_id=row_num,
                        defaults={
                            'name': name,
                            'email': email,
                            'phone': phone,
                            'company': company,
                            'notes': notes,
                            'status': status,
                            'seller': seller,
                            'source': 'google_sheets',
                            'last_synced_at': timezone.now(),
                        }
                    )
                    
                    if created_flag:
                        created += 1
                    else:
                        updated += 1
                        
                except Exception as e:
                    print(f"Error syncing row {row_num}: {e}")
                    errors += 1
            
            return {
                'created': created,
                'updated': updated,
                'errors': errors,
                'total_rows': len(data_rows)
            }
            
        except Exception as e:
            print(f"Error syncing from Google Sheets: {e}")
            raise
    
    def sync_to_sheets(self, leads: Optional[List[Lead]] = None) -> Dict[str, int]:
        """
        Sync leads from database to Google Sheets.
        
        If leads is None, syncs all leads.
        """
        try:
            if leads is None:
                leads = Lead.objects.filter(source='google_sheets').exclude(sheets_row_id__isnull=True)
            
            updated = 0
            errors = 0
            
            for lead in leads:
                try:
                    if not lead.sheets_row_id:
                        continue  # Skip leads without row ID
                    
                    row_num = lead.sheets_row_id
                    
                    # Prepare row data
                    row_data = [
                        lead.name,
                        lead.email,
                        lead.phone,
                        lead.company,
                        lead.notes,
                        lead.get_status_display(),
                        lead.seller.user.username if lead.seller else '',
                        lead.created_at.strftime('%Y-%m-%d %H:%M:%S') if lead.created_at else '',
                    ]
                    
                    # Update the row
                    self.worksheet.update(f'A{row_num}:H{row_num}', [row_data])
                    updated += 1
                    
                except Exception as e:
                    print(f"Error syncing lead {lead.id} to sheets: {e}")
                    errors += 1
            
            return {
                'updated': updated,
                'errors': errors
            }
            
        except Exception as e:
            print(f"Error syncing to Google Sheets: {e}")
            raise


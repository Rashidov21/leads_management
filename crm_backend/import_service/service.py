"""Import service for handling lead imports from various sources."""
import re
from typing import List, Dict, Tuple
from django.conf import settings


class DuplicateChecker:
    """Check for duplicate leads."""
    
    def __init__(self, check_field='phone'):
        self.check_field = check_field
    
    def is_duplicate(self, value, existing_values: set) -> bool:
        """Check if value exists in existing values."""
        normalized_value = self._normalize_value(value)
        return normalized_value in existing_values
    
    def _normalize_value(self, value: str) -> str:
        """Normalize value for comparison (e.g., remove spaces from phone)."""
        if self.check_field == 'phone':
            return re.sub(r'\D', '', str(value))
        return str(value).strip().lower()
    
    def get_existing_values(self):
        """Get set of existing values in database."""
        from leads.models import Lead
        
        if self.check_field == 'phone':
            values = Lead.objects.values_list('phone', flat=True)
            return {self._normalize_value(v) for v in values}
        
        values = Lead.objects.values_list(self.check_field, flat=True)
        return {self._normalize_value(v) for v in values}


class LeadDataValidator:
    """Validate lead data before import."""
    
    @staticmethod
    def validate_row(row: Dict) -> Tuple[bool, str, Dict]:
        """
        Validate a single lead row.
        
        Returns: (is_valid, error_message, cleaned_data)
        """
        errors = []
        cleaned_data = {}
        
        # Validate name
        name = row.get('name', '').strip()
        if not name:
            errors.append('Name is required')
        else:
            if len(name) > 255:
                errors.append('Name is too long (max 255 characters)')
            cleaned_data['name'] = name
        
        # Validate phone
        phone = row.get('phone', '').strip()
        if not phone:
            errors.append('Phone is required')
        else:
            normalized_phone = re.sub(r'\D', '', phone)
            if len(normalized_phone) < 10:
                errors.append('Phone must have at least 10 digits')
            else:
                cleaned_data['phone'] = phone
        
        is_valid = len(errors) == 0
        error_message = '; '.join(errors) if errors else ''
        
        return is_valid, error_message, cleaned_data
    
    @staticmethod
    def validate_batch(rows: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate a batch of rows.
        
        Returns: (valid_rows, invalid_rows_with_errors)
        """
        valid_rows = []
        invalid_rows = []
        
        for idx, row in enumerate(rows):
            is_valid, error_msg, cleaned_data = LeadDataValidator.validate_row(row)
            
            if is_valid:
                cleaned_data['row_index'] = idx
                valid_rows.append(cleaned_data)
            else:
                invalid_rows.append({
                    'row_index': idx,
                    'row_data': row,
                    'error': error_msg
                })
        
        return valid_rows, invalid_rows


class ImportProcessor:
    """Process and import leads into the database."""
    
    @staticmethod
    def import_leads(leads_data: List[Dict], source: str) -> Tuple[int, int, List[Dict]]:
        """
        Import leads into database.
        
        Args:
            leads_data: List of dictionaries with 'name' and 'phone'
            source: Source of the import (google_sheets, excel_upload, csv_upload)
        
        Returns: (imported_count, duplicate_count, errors)
        """
        from leads.models import Lead
        
        # Validate data
        valid_rows, invalid_rows = LeadDataValidator.validate_batch(leads_data)
        
        if invalid_rows:
            return 0, 0, invalid_rows
        
        # Check for duplicates
        duplicate_checker = DuplicateChecker(check_field='phone')
        existing_phones = duplicate_checker.get_existing_values()
        
        imported_count = 0
        duplicate_count = 0
        
        leads_to_create = []
        
        for lead_data in valid_rows:
            normalized_phone = duplicate_checker._normalize_value(lead_data['phone'])
            
            if duplicate_checker.is_duplicate(normalized_phone, existing_phones):
                duplicate_count += 1
            else:
                leads_to_create.append(
                    Lead(
                        name=lead_data['name'],
                        phone=lead_data['phone'],
                        source=source,
                        status='new'
                    )
                )
                existing_phones.add(normalized_phone)
        
        # Bulk create leads
        if leads_to_create:
            created_leads = Lead.objects.bulk_create(leads_to_create, batch_size=settings.IMPORT_BATCH_SIZE)
            imported_count = len(created_leads)
        
        return imported_count, duplicate_count, []

"""Celery tasks for import service."""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from leads.models import ImportLog, Lead, LeadReminder
from .service import ImportProcessor
from .google_sheets import GoogleSheetsService


@shared_task
def import_from_google_sheets(sheet_id: str = None):
    """
    Scheduled task to import leads from Google Sheets.
    Runs every 5 minutes.
    """
    if not sheet_id:
        sheet_id = settings.GOOGLE_SHEETS_API_KEY
    
    # Create import log
    import_log = ImportLog.objects.create(
        import_type='google_sheets',
        status='processing',
        google_sheet_id=sheet_id
    )
    
    try:
        # Read from Google Sheets
        gs_service = GoogleSheetsService()
        sheet_data = gs_service.read_sheet(sheet_id)
        leads_data = gs_service.parse_sheet_data(sheet_data)
        
        import_log.total_records = len(leads_data)
        import_log.save()
        
        if not leads_data:
            import_log.status = 'completed'
            import_log.completed_at = timezone.now()
            import_log.save()
            return
        
        # Import leads
        imported_count, duplicate_count, errors = ImportProcessor.import_leads(
            leads_data,
            source='google_sheets'
        )
        
        # Update import log
        import_log.imported_count = imported_count
        import_log.duplicate_count = duplicate_count
        import_log.error_count = len(errors)
        import_log.error_details = {'errors': errors}
        import_log.status = 'completed'
        import_log.completed_at = timezone.now()
        import_log.save()
        
        # Create reminders for imported leads
        if imported_count > 0:
            create_reminders_for_new_leads.delay()
    
    except Exception as e:
        import_log.status = 'failed'
        import_log.error_details = {'error': str(e)}
        import_log.completed_at = timezone.now()
        import_log.save()


@shared_task
def manual_import_file(file_path: str, import_type: str = 'excel', user_id: int = None):
    """
    Manual import task for Excel/CSV files.
    
    Args:
        file_path: Path to uploaded file
        import_type: 'excel' or 'csv'
        user_id: ID of user who uploaded the file
    """
    from django.contrib.auth.models import User
    
    user = None
    if user_id:
        user = User.objects.get(id=user_id)
    
    # Create import log
    import_log = ImportLog.objects.create(
        import_type=import_type,
        status='processing',
        file_name=file_path.split('/')[-1],
        imported_by=user
    )
    
    try:
        # Parse file
        if import_type == 'excel':
            from .file_parsers import ExcelService
            with open(file_path, 'rb') as f:
                leads_data = ExcelService.parse_file(f)
        else:  # csv
            from .file_parsers import CSVService
            with open(file_path, 'r') as f:
                leads_data = CSVService.parse_file(f)
        
        import_log.total_records = len(leads_data)
        import_log.save()
        
        if not leads_data:
            import_log.status = 'completed'
            import_log.completed_at = timezone.now()
            import_log.save()
            return
        
        # Import leads
        source = f'{import_type}_upload'
        imported_count, duplicate_count, errors = ImportProcessor.import_leads(
            leads_data,
            source=source
        )
        
        # Update import log
        import_log.imported_count = imported_count
        import_log.duplicate_count = duplicate_count
        import_log.error_count = len(errors)
        import_log.error_details = {'errors': errors}
        import_log.status = 'completed'
        import_log.completed_at = timezone.now()
        import_log.save()
        
        # Create reminders for imported leads
        if imported_count > 0:
            create_reminders_for_new_leads.delay()
    
    except Exception as e:
        import_log.status = 'failed'
        import_log.error_details = {'error': str(e)}
        import_log.completed_at = timezone.now()
        import_log.save()


@shared_task
def create_reminders_for_new_leads():
    """
    Create reminders for all new leads without reminders.
    """
    new_leads = Lead.objects.filter(
        status='new',
        reminder__isnull=True
    )
    
    reminders = [
        LeadReminder(
            lead=lead,
            contact_deadline=timezone.now() + timezone.timedelta(minutes=5)
        )
        for lead in new_leads
    ]
    
    if reminders:
        LeadReminder.objects.bulk_create(reminders, batch_size=100)

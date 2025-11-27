# Education Center CRM System - Lead Import Functionality

A complete Django-based CRM system with automated lead import from Google Sheets and manual Excel/CSV uploads. Features include duplicate detection, automatic reminder scheduling, and a responsive Tailwind CSS frontend.

## Features

### 1. Google Sheets Auto Import
- **Automatic import every 5 minutes** via Celery Beat
- Connects to Google Sheets API to fetch new leads
- Fields imported: Name, Phone
- Prevents duplicate leads by checking phone numbers
- Creates automatic reminders for new leads

### 2. Excel/CSV Manual Upload
- Salespeople can upload Excel (.xlsx) or CSV files
- Parses Name and Phone columns
- Duplicate detection before import
- Bulk processing for performance
- Import history and status tracking

### 3. Lead Management
- Full CRUD operations on leads
- Lead fields:
  - **Name** (imported)
  - **Phone** (imported)
  - **Source** (google_sheets, excel_upload, csv_upload, manual)
  - **Status** (new, contacted, qualified, converted, lost)
  - **Assigned Salesperson** (manual assignment)

### 4. Reminder System
- Automatic reminders created for new leads
- Salespeople must contact within 5 minutes
- Follow-up reminders every 1 minute if overdue
- Snooze functionality
- Email notification support (configurable)

## Project Structure

```
leads_management/
├── crm_backend/
│   ├── crm_project/
│   │   ├── __init__.py
│   │   ├── settings.py         # Django settings
│   │   ├── urls.py             # Main URL configuration
│   │   ├── wsgi.py
│   │   ├── celery.py           # Celery configuration
│   │   └── manage.py
│   │
│   ├── leads/                  # Leads app
│   │   ├── models.py           # Lead, ImportLog, LeadReminder models
│   │   ├── views.py            # API views
│   │   ├── serializers.py      # DRF serializers
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   ├── import_service/         # Import service app
│   │   ├── service.py          # Core import logic
│   │   ├── google_sheets.py    # Google Sheets integration
│   │   ├── file_parsers.py     # Excel/CSV parsing
│   │   ├── views.py            # Import API views
│   │   ├── tasks.py            # Celery tasks
│   │   ├── urls.py
│   │   └── apps.py
│   │
│   ├── reminders/              # Reminders app
│   │   ├── tasks.py            # Reminder Celery tasks
│   │   ├── views.py            # Reminder API views
│   │   ├── urls.py
│   │   └── apps.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── templates/
│   │   ├── dashboard.html      # Main dashboard
│   │   ├── leads.html          # Lead management page
│   │   ├── import.html         # Import upload page
│   │   └── reminders.html      # Reminders page
│   └── static/
│
└── README.md
```

## Installation & Setup

### Backend Setup

1. **Clone and navigate to project:**
   ```bash
   cd crm_backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   DB_NAME=crm_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   
   GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
   GOOGLE_SHEETS_API_KEY=your-sheet-id
   ```

5. **Setup PostgreSQL database:**
   ```bash
   # Create database and user
   CREATE DATABASE crm_db;
   CREATE USER crm_user WITH PASSWORD 'password';
   ALTER ROLE crm_user SET client_encoding TO 'utf8';
   GRANT ALL PRIVILEGES ON DATABASE crm_db TO crm_user;
   ```

6. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

### Running the Application

1. **Start Redis:**
   ```bash
   redis-server
   ```

2. **Start Celery worker:**
   ```bash
   celery -A crm_project worker -l info -Q imports,reminders
   ```

3. **Start Celery Beat (scheduler):**
   ```bash
   celery -A crm_project beat -l info
   ```

4. **Start Django development server:**
   ```bash
   python manage.py runserver
   ```

5. **Access the application:**
   - Dashboard: http://localhost:8000/
   - Admin: http://localhost:8000/admin/
   - API: http://localhost:8000/api/

## API Endpoints

### Leads
- `GET /api/leads/` - List all leads
- `POST /api/leads/` - Create new lead
- `GET /api/leads/{id}/` - Get lead details
- `PUT /api/leads/{id}/` - Update lead
- `DELETE /api/leads/{id}/` - Delete lead
- `GET /api/leads/by_status/?status=new` - Filter by status
- `GET /api/leads/by_salesperson/?salesperson_id=1` - Filter by assigned person
- `POST /api/leads/{id}/mark_contacted/` - Mark as contacted
- `POST /api/leads/{id}/assign_to_salesperson/` - Assign lead

### Import
- `POST /api/imports/upload-excel/` - Upload Excel file
- `POST /api/imports/upload-csv/` - Upload CSV file
- `GET /api/imports/status/` - Get recent imports

### Reminders
- `GET /api/reminders/pending_reminders/` - Get pending reminders
- `GET /api/reminders/overdue_reminders/` - Get overdue reminders
- `POST /api/reminders/{id}/mark_contacted/` - Mark reminder as contacted
- `POST /api/reminders/{id}/snooze/` - Snooze reminder

## Google Sheets Setup

1. **Create service account credentials:**
   - Go to Google Cloud Console
   - Create new project
   - Enable Google Sheets API
   - Create service account
   - Generate and download JSON key file

2. **Place credentials file:**
   ```bash
   cp credentials.json crm_backend/
   ```

3. **Share Google Sheet:**
   - Create Google Sheet with columns: Name, Phone
   - Share sheet with service account email
   - Add sheet ID to `.env` file

## Frontend Features

### Dashboard
- Overview statistics (total leads, new, pending reminders, converted)
- Quick action buttons
- Recent leads list
- Import status

### Leads Management
- Browse all leads with filtering by status/source
- Add new leads manually
- Edit existing leads
- Delete leads
- Assign salespeople
- Mark as contacted

### Import Page
- Drag-and-drop file upload (Excel/CSV)
- Real-time upload progress
- Import history with statistics
- Duplicate detection feedback

### Reminders
- View pending reminders with deadlines
- View overdue reminders
- View contacted leads
- Mark reminders as contacted
- Snooze reminders
- Real-time updates

## Scheduled Tasks

### Celery Beat Schedule
- **Every 5 minutes:** Import from Google Sheets
  - Task: `import_service.tasks.import_from_google_sheets`
  - Fetches new leads from configured Google Sheet
  - Creates reminders for imported leads

- **Every 1 minute:** Check reminder deadlines
  - Task: `reminders.tasks.check_reminder_deadlines`
  - Identifies overdue reminders
  - Sends notifications to salespeople
  - Increments reminder count

## Database Models

### Lead
```python
- id: AutoField
- name: CharField
- phone: CharField (unique)
- source: CharField (google_sheets, excel_upload, csv_upload, manual)
- status: CharField (new, contacted, qualified, converted, lost)
- assigned_to: ForeignKey(User)
- created_at: DateTimeField
- updated_at: DateTimeField
```

### ImportLog
```python
- id: AutoField
- import_type: CharField
- status: CharField (pending, processing, completed, failed)
- total_records: IntegerField
- imported_count: IntegerField
- duplicate_count: IntegerField
- error_count: IntegerField
- error_details: JSONField
- imported_by: ForeignKey(User)
- file_name: CharField
- google_sheet_id: CharField
- started_at: DateTimeField
- completed_at: DateTimeField
```

### LeadReminder
```python
- id: AutoField
- lead: OneToOneField(Lead)
- status: CharField (pending, notified, contacted, snoozed)
- created_at: DateTimeField
- contact_deadline: DateTimeField
- last_reminder_at: DateTimeField
- contacted_at: DateTimeField
- reminder_count: IntegerField
```

## Configuration

### Import Settings
- `IMPORT_BATCH_SIZE=100` - Batch size for bulk imports
- `DUPLICATE_CHECK_FIELD='phone'` - Field to check for duplicates

### Reminder Settings
- `REMINDER_CHECK_INTERVAL=300` - Check interval in seconds (5 minutes)
- `REMINDER_CONTACT_DEADLINE=300` - Contact deadline in seconds (5 minutes)

## Error Handling

The system handles various error scenarios:
- Missing required fields in imports
- Duplicate detection
- Invalid file formats
- Database errors
- API errors
- Celery task failures

All errors are logged in `ImportLog.error_details` for tracking.

## Security Notes

1. **Keep credentials.json secure** - Never commit to version control
2. **Use environment variables** for sensitive data
3. **Enable CORS only for trusted origins**
4. **Use HTTPS in production**
5. **Set DEBUG=False in production**
6. **Use strong SECRET_KEY**

## Testing

To test the import functionality:

1. **Create test Excel file** with columns: Name, Phone
2. **Upload via import page**
3. **Check import status** in dashboard
4. **Verify leads** in leads management page
5. **Check reminders** created automatically

## Troubleshooting

### Celery tasks not running
- Ensure Redis is running
- Check Celery worker logs
- Verify Celery Beat schedule configuration

### Google Sheets import not working
- Verify credentials.json is correct
- Check sheet ID in .env
- Ensure sheet is shared with service account
- Verify Google Sheets API is enabled

### Reminders not sending
- Check email configuration
- Verify assigned salespersons have email addresses
- Check reminder task logs

## Production Deployment

1. **Use PostgreSQL** instead of SQLite
2. **Setup Redis** for Celery
3. **Use Gunicorn** as WSGI server
4. **Configure Nginx** as reverse proxy
5. **Enable HTTPS** with SSL certificate
6. **Setup logging** to persistent storage
7. **Configure backup** strategy
8. **Monitor** system performance

## Contributing

1. Create feature branch
2. Make changes following PEP 8
3. Write tests
4. Submit pull request

## License

MIT License - See LICENSE file

## Support

For issues and questions:
- Email: support@educationcrm.com
- GitHub Issues: [Link]
- Documentation: [Link]

# Quick Reference Guide

## Directory Navigation

```
leads_management/
├── crm_backend/               # Django backend (python manage.py runserver)
│   ├── crm_project/           # Project settings
│   ├── leads/                 # Lead CRUD, models, views
│   ├── import_service/        # Import logic, Google Sheets, Excel/CSV
│   ├── reminders/             # Reminder system, tasks
│   ├── manage.py              # Django management
│   ├── requirements.txt       # Python dependencies
│   ├── docker-compose.yml     # Docker setup
│   └── .env.example           # Environment template
│
├── frontend/                  # HTML/CSS frontend (open in browser)
│   └── templates/
│       ├── dashboard.html     # Main page
│       ├── leads.html         # Lead management
│       ├── import.html        # File upload
│       └── reminders.html     # Reminders
│
├── README.md                  # Main documentation
├── API_DOCUMENTATION.md       # API reference
├── DEPLOYMENT.md              # Production deployment
└── IMPLEMENTATION_SUMMARY.md  # This document
```

## Common Commands

### Backend Setup

```bash
# Navigate to backend
cd crm_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run database migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver

# Run test import command
python manage.py test_import --count=20
```

### Celery & Redis

```bash
# Start Redis (required for Celery)
redis-server

# Start Celery worker (in another terminal)
celery -A crm_project worker -l info

# Start Celery Beat scheduler (in another terminal)
celery -A crm_project beat -l info

# Run task immediately (for testing)
celery -A import_service.tasks import_from_google_sheets --apply-async
```

### Docker Commands

```bash
# Start all services with Docker
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f web

# Access database
docker-compose exec db psql -U crm_user -d crm_db
```

## API Quick Reference

### Authentication Token

```bash
# Obtain token (replace username/password)
curl -X POST http://localhost:8000/api-token-auth/ \
  -d "username=YOUR_USERNAME&password=YOUR_PASSWORD"

# Use token in requests
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/leads/
```

### Common API Calls

```bash
# Get all leads
curl -H "Authorization: Token TOKEN" \
  http://localhost:8000/api/leads/

# Get new leads only
curl -H "Authorization: Token TOKEN" \
  http://localhost:8000/api/leads/by_status/?status=new

# Get pending reminders
curl -H "Authorization: Token TOKEN" \
  http://localhost:8000/api/reminders/pending_reminders/

# Upload Excel file
curl -X POST \
  -H "Authorization: Token TOKEN" \
  -F "file=@leads.xlsx" \
  http://localhost:8000/api/imports/upload-excel/

# Create a lead
curl -X POST \
  -H "Authorization: Token TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"John","phone":"+1234567890","source":"manual","status":"new"}' \
  http://localhost:8000/api/leads/
```

## Configuration

### Important Settings (.env file)

```env
# Debug mode
DEBUG=True              # Set to False in production

# Database
DB_NAME=crm_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost

# Redis & Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Google Sheets
GOOGLE_SHEETS_API_KEY=your_sheet_id
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json

# Email (for reminders)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=app_password
```

## Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Redis connection refused

**Solution:**
```bash
# Start Redis server
redis-server

# On Windows with Redis installed:
redis-server.exe
```

### Issue: Database connection error

**Solution:**
```bash
# Check PostgreSQL is running
psql -U postgres

# Or use SQLite for development
# Modify settings.py DATABASES to use sqlite3
```

### Issue: Static files not loading

**Solution:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Clear browser cache (Ctrl+Shift+Delete)
```

### Issue: Celery tasks not running

**Solution:**
```bash
# Check if worker is running
celery -A crm_project inspect active

# Check if beat is running
ps aux | grep celery

# View task history
celery -A crm_project events
```

## File Formats

### Excel Import Format

Create file with two columns:

| Name | Phone |
|------|-------|
| John Doe | +1-234-567-8900 |
| Jane Smith | +1-987-654-3210 |

Save as `.xlsx` file

### CSV Import Format

Create text file with comma-separated values:

```
Name,Phone
John Doe,+1-234-567-8900
Jane Smith,+1-987-654-3210
```

Save as `.csv` file

## Default Credentials

**Django Admin:**
- URL: http://localhost:8000/admin/
- Username: (created during setup)
- Password: (created during setup)

**Database (PostgreSQL):**
- Host: localhost
- Port: 5432
- Username: postgres
- Password: (set during installation)

**Redis:**
- Host: localhost
- Port: 6379
- Password: (none by default)

## API Response Examples

### Lead Object
```json
{
  "id": 1,
  "name": "John Doe",
  "phone": "+1234567890",
  "source": "manual",
  "status": "new",
  "assigned_to": 2,
  "assigned_to_username": "salesperson1",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Reminder Object
```json
{
  "id": 1,
  "lead": 1,
  "lead_name": "John Doe",
  "lead_phone": "+1234567890",
  "status": "pending",
  "contact_deadline": "2024-01-15T10:35:00Z",
  "reminder_count": 0
}
```

### Import Status Object
```json
{
  "id": 1,
  "import_type": "Excel",
  "status": "completed",
  "total_records": 50,
  "imported_count": 48,
  "duplicate_count": 2,
  "error_count": 0,
  "file_name": "leads.xlsx",
  "started_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:02:30Z"
}
```

## Useful Links

- Django Docs: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Celery Docs: https://docs.celeryproject.org/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Redis Docs: https://redis.io/documentation
- Google Sheets API: https://developers.google.com/sheets/api
- Tailwind CSS: https://tailwindcss.com/

## Performance Tips

### For Large Imports (10,000+ leads)

```python
# Increase batch size in settings.py
IMPORT_BATCH_SIZE = 500

# Or in code:
leads = Lead.objects.bulk_create(leads_list, batch_size=500)
```

### For Better Celery Performance

```bash
# Use multiple workers
celery -A crm_project worker -l info --concurrency=8

# Use specific queue
celery -A crm_project worker -Q imports,reminders -l info
```

### For Database Performance

```sql
-- Monitor slow queries
SELECT * FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Analyze query plan
EXPLAIN ANALYZE 
SELECT * FROM leads_lead WHERE status='new';
```

## Monitoring

### Check Application Health

```bash
# Test API is running
curl http://localhost:8000/api/leads/

# Test database connection
python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()

# Test Redis connection
redis-cli ping
# Should return: PONG
```

### View Logs

```bash
# Django logs
tail -f django.log

# Celery worker logs
tail -f celery-worker.log

# Celery beat logs
tail -f celery-beat.log
```

## Backup & Recovery

### Backup Database

```bash
# PostgreSQL backup
pg_dump -U crm_user crm_db > backup.sql

# With compression
pg_dump -U crm_user crm_db | gzip > backup.sql.gz
```

### Restore Database

```bash
# PostgreSQL restore
psql -U crm_user crm_db < backup.sql

# From compressed backup
gunzip -c backup.sql.gz | psql -U crm_user crm_db
```

## Feature Test Checklist

- [ ] Import from Excel file
- [ ] Import from CSV file
- [ ] View pending reminders
- [ ] Mark lead as contacted
- [ ] Snooze reminder
- [ ] Assign lead to salesperson
- [ ] Change lead status
- [ ] Delete lead
- [ ] View import history
- [ ] Check dashboard statistics

## Common Customizations

### Change Reminder Deadline (from 5 to 10 minutes)

```python
# In settings.py
REMINDER_CONTACT_DEADLINE = 600  # 10 minutes in seconds

# In tasks.py
contact_deadline=timezone.now() + timezone.timedelta(minutes=10)
```

### Change Import Schedule (from every 5 to every 1 minute)

```python
# In celery.py
'import-from-google-sheets': {
    'schedule': 60.0,  # Every 1 minute
}
```

### Add Custom Lead Field

```python
# In leads/models.py
class Lead(models.Model):
    # ... existing fields ...
    email = models.EmailField(blank=True, null=True)
    
# Run migrations
python manage.py makemigrations
python manage.py migrate
```

## Documentation Files

- **README.md** - Main project documentation
- **API_DOCUMENTATION.md** - Complete API reference
- **DEPLOYMENT.md** - Production deployment guide
- **IMPLEMENTATION_SUMMARY.md** - Feature overview
- **QUICK_REFERENCE.md** - This file

## Support

For issues:
1. Check documentation files
2. Review error logs
3. Check API responses
4. Contact: support@educationcrm.com

---

**Last Updated:** November 27, 2025
**Version:** 1.0.0

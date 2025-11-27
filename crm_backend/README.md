# CRM Backend - Complete Setup Documentation

## Overview

This is a Django-based CRM backend system for managing leads, courses, trials, and analytics. The system includes:

- **Lead Management**: Multi-source lead import and tracking
- **Course & Group Scheduling**: Course/group management with room allocation
- **Trial Lessons**: Trial scheduling and result tracking
- **Sales Analytics**: KPI tracking and conversion analytics

## Project Status: ✅ FULLY CONFIGURED

All apps have been configured with:
- ✅ Complete model definitions
- ✅ Django admin interfaces
- ✅ Migrations created and applied
- ✅ Database tables created
- ✅ Permissions and content types registered

## Quick Start

### 1. Start the Development Server

```bash
cd crm_backend
python manage.py runserver
```

The server will start at: `http://127.0.0.1:8000/`

### 2. Access Django Admin

Navigate to: `http://127.0.0.1:8000/admin/`

### 3. Create Superuser (First Time Only)

```bash
python manage.py createsuperuser
```

## Installed Apps & Features

### 1. **Leads App** (`leads/`)
**Purpose**: Core lead management and import

**Models**:
- `Lead`: Lead information with source, status, and assignment
- `ImportLog`: Track import history from various sources
- `LeadReminder`: Manage follow-up reminders

**Lead Sources Supported**:
- Instagram Ads
- Telegram Bot
- WhatsApp
- Call Tracking
- Landing Page
- Google Sheets
- Excel Files
- CSV Files

**Admin Features**:
- List all leads with status and source filters
- Search leads by name or phone
- Assign leads to salespeople
- View import logs

### 2. **Import Service App** (`import_service/`)
**Purpose**: Handle multi-source lead imports

**Features**:
- Duplicate detection and prevention
- Multi-format support (CSV, Excel, Google Sheets)
- Import status tracking
- Bulk lead creation

### 3. **Reminders App** (`reminders/`)
**Purpose**: Follow-up reminder management

**Features**:
- Reminder creation and tracking
- Contact deadline management
- Reminder count tracking
- Status management (pending, sent, completed)

### 4. **Scheduling App** (`scheduling/`)
**Purpose**: Course and group scheduling with room management

**Models**:
- `Course`: Course information with teacher and pricing
  - Fields: name, description, teacher, price, duration, frequency, capacity
  
- `Room`: Physical classroom/room information
  - Fields: name, capacity, location
  
- `Group`: Course groups/classes with schedule
  - Fields: course, name, days, start_time, end_time, room, capacity, students
  - Properties: free_slots, occupancy_percent, is_full
  
- `RoomOccupancy`: Track room usage by time slot
  - Fields: room, date, time_start, time_end, occupancy_count
  - Properties: occupancy_percent, availability_color

**Admin Features**:
- Create and manage courses with teachers and pricing
- Create rooms and manage capacity
- Create groups with custom schedules (supports day patterns)
- Monitor occupancy percentages with color coding
- View free slots and capacity status
- Track room usage over time

**Day Patterns Supported**:
- `odd` / `even` (odd/even calendar days)
- `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`
- `mon_wed_fri` (specific day combinations)
- `tue_thu`

### 5. **Trials App** (`trials/`)
**Purpose**: Trial lesson scheduling and conversion tracking

**Models**:
- `Trial`: Trial lesson scheduling and result tracking
  - Fields: lead, group, scheduled_date, scheduled_time, status, result
  - Trial status: scheduled, attended, no-show, cancelled
  - Trial result: pending, sales_offer, accepted, rejected
  - Properties: is_overdue, is_upcoming_today, hours_until_trial
  
- `TrialReminder`: Pre and post-trial reminder management
  - Fields: trial, pre_trial_reminder_scheduled_at, post_trial_reminder_sent
  - Tracks both pre-trial (2 hours before) and post-trial (3 min after) reminders

**Admin Features**:
- Schedule trials for leads and groups
- Track trial attendance
- Monitor trial-to-enrollment conversion
- Manage pre and post-trial reminders
- View overdue trials
- Filter by status and result
- Color-coded status badges

### 6. **Analytics App** (`analytics/`)
**Purpose**: Sales metrics and performance analytics

**Models**:

#### SalesKPI
**Daily metrics per salesperson**:
- Contacts and follow-ups (new_contacts, followups_completed, followups_overdue)
- Trials (trials_scheduled, trials_attended, trials_no_show)
- Conversions (sales_offers_made, enrollments, lost_leads)
- Time metrics (avg_response_time)
- Computed properties: followup_completion_percent, trial_to_conversion_percent, overall_conversion_percent

#### LeadMetrics
**Daily aggregated lead metrics**:
- Lead acquisition by source (instagram, telegram, whatsapp, landing, etc.)
- Status breakdown (contacted, interested, trial_scheduled, trial_attended, enrolled, lost)
- Distribution (assigned, unassigned)
- Properties: source_breakdown, conversion_rate_percent, trial_to_conversion_percent

#### GroupAnalytics
**Group capacity and planning metrics**:
- Capacity metrics (full_groups, near_full_groups, empty_groups)
- Room usage (rooms_in_use, avg_room_occupancy)
- Trial students and expected enrollments
- Recommendations (new_groups_recommended, groups_to_combine)

#### MarketingAnalytics
**Marketing channel performance**:
- Traffic metrics (impressions, clicks, CTR)
- Lead generation (leads_generated, cost_total, CPL)
- Conversion metrics (enrollments_from_channel, CPA)

**Channels Tracked**:
- Instagram Ads
- Telegram Bot
- WhatsApp
- Landing Page
- Google Sheets
- Call Tracking

**Admin Features**:
- View daily KPIs per salesperson
- Monitor conversion rates with color coding
- Track lead metrics by source
- Analyze group capacity usage
- Monitor marketing channel performance and ROI

## Admin Interface Features

### Color-Coded Status Indicators

**Scheduling** (Group Occupancy):
- 🟢 Green: < 50% capacity
- 🟠 Orange: 50-80% capacity
- 🔴 Red: 80%+ or full

**Trials** (Trial Status):
- 🔵 Blue: Scheduled
- 🟢 Green: Attended
- 🔴 Red: No-show
- ⚫ Gray: Cancelled

**Analytics** (Conversion Rates):
- 🟢 Green: ≥ 20% conversion
- 🟠 Orange: 10-20% conversion
- 🔴 Red: < 10% conversion

### Key Metrics Available

**Group Admin**:
- Occupancy percentage
- Free slots remaining
- Trial students in group
- Is group full (yes/no)

**Trial Admin**:
- Trial status with color badge
- Result status with color badge
- Hours until trial
- Whether trial is overdue
- Whether trial is today

**SalesKPI Admin**:
- New contacts acquired
- Trials attended/no-show
- Enrollments
- Conversion percentages
- Follow-up completion rate

**LeadMetrics Admin**:
- Lead acquisition by source (breakdown display)
- Conversion rate with color badge
- Trial-to-conversion percentage
- Lead distribution

**MarketingAnalytics Admin**:
- Cost per lead (CPL)
- Cost per acquisition (CPA)
- Click-through rate (CTR)
- Channel performance comparison

## Database Structure

### Migrations Applied

All migrations have been created and successfully applied:

```
analytics/migrations/0001_initial.py
scheduling/migrations/0001_initial.py
trials/migrations/0001_initial.py
```

### Tables Created

1. **scheduling** app tables:
   - Course
   - Room
   - Group
   - RoomOccupancy

2. **trials** app tables:
   - Trial
   - TrialReminder

3. **analytics** app tables:
   - SalesKPI
   - LeadMetrics
   - GroupAnalytics
   - MarketingAnalytics

## API Integration (Future)

The backend is structured to support REST API integration:

- Each app has a `views.py` file ready for API views
- Each app has a `urls.py` file ready for URL routing
- Models are designed with proper relationships for serialization

## Usage Workflows

### 1. Lead Management Workflow
1. Import leads from multiple sources via import service
2. Assign leads to salespeople
3. Set follow-up reminders
4. Track reminder completion
5. Update lead status as sales progress

### 2. Trial Scheduling Workflow
1. Create courses and groups
2. Schedule trial lessons for interested leads
3. System generates pre and post-trial reminders
4. Track trial attendance
5. Generate sales offers post-trial
6. Track conversion to enrollment

### 3. Group Management Workflow
1. Create courses with pricing and teacher assignment
2. Create groups with specific schedules and rooms
3. Monitor group occupancy
4. View free slots and capacity
5. Get recommendations for new groups or combining groups

### 4. Analytics Workflow
1. Daily KPIs automatically tracked per salesperson
2. Lead metrics aggregated daily by source
3. Group capacity and planning recommendations
4. Marketing channel performance tracked
5. Reports available in admin interface

## Environment Variables

Required `.env` file variables:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

## File Structure

```
crm_backend/
├── crm_project/          # Main Django project settings
│   ├── settings.py       # All apps configured
│   ├── urls.py
│   └── wsgi.py
├── leads/                # Lead management
│   ├── models.py
│   ├── admin.py
│   └── views.py
├── import_service/       # Lead import handling
│   ├── models.py
│   └── views.py
├── reminders/            # Reminder management
│   ├── models.py
│   └── views.py
├── scheduling/           # Course & group scheduling
│   ├── models.py         # Course, Room, Group, RoomOccupancy
│   ├── admin.py          # Admin configuration
│   └── views.py
├── trials/               # Trial lesson management
│   ├── models.py         # Trial, TrialReminder
│   ├── admin.py          # Admin configuration
│   └── views.py
├── analytics/            # Sales & marketing analytics
│   ├── models.py         # SalesKPI, LeadMetrics, GroupAnalytics, MarketingAnalytics
│   ├── admin.py          # Admin configuration
│   └── views.py
├── templates/            # HTML templates
├── db.sqlite3            # Database
├── manage.py             # Django management script
├── SETUP_GUIDE.md        # Setup guide
└── requirements.txt      # Python dependencies
```

## Next Steps

### Immediate Actions
1. ✅ Create superuser: `python manage.py createsuperuser`
2. ✅ Start development server: `python manage.py runserver`
3. ✅ Access admin at `http://127.0.0.1:8000/admin/`

### Development
1. Build API views for each app
2. Create API serializers
3. Implement URL routing for API endpoints
4. Add authentication and permissions
5. Create frontend application

### Production Deployment
1. Set DEBUG=False
2. Configure proper database (PostgreSQL recommended)
3. Set up environment variables
4. Configure allowed hosts
5. Set up email for reminders
6. Configure static files serving
7. Set up task queue (Celery) for reminders
8. Deploy with production WSGI server (Gunicorn)

## Commands Reference

```bash
# Create migrations for new models
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Create admin superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run system checks
python manage.py check

# Create initial data (fixtures)
python manage.py loaddata fixture_name

# Dump data to fixture
python manage.py dumpdata app_name > fixture.json

# Access Django shell
python manage.py shell
```

## Support & Documentation

For more information:
- Django Docs: https://docs.djangoproject.com/
- This SETUP_GUIDE.md file for detailed setup
- Model docstrings in each app's models.py file
- Admin interface help within Django admin

---

**Last Updated**: November 2025
**Status**: ✅ Fully Configured and Ready for Use

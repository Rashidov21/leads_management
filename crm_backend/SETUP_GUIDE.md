# CRM Backend Setup Guide

## Project Structure

This Django project is a comprehensive CRM system with the following apps:

### Installed Apps

1. **leads** - Core lead management system
   - Lead tracking and assignment
   - Import from multiple sources (CSV, Excel, Google Sheets, Instagram, Telegram, WhatsApp, Call tracking)
   - Reminders for follow-ups

2. **import_service** - Handles lead imports
   - Manages the import process
   - Tracks import history and status
   - Handles duplicate detection

3. **reminders** - Follow-up reminder system
   - Tracks reminders for leads
   - Manages reminder status and completion

4. **scheduling** - Course and group scheduling
   - Course management
   - Group (class) management
   - Room allocation and occupancy tracking
   - Timetable generation

5. **trials** - Trial lesson management
   - Trial scheduling
   - Trial status tracking (scheduled, attended, no-show, cancelled)
   - Trial result tracking (pending, sales_offer, accepted, rejected)
   - Reminder tracking for pre and post-trial notifications

6. **analytics** - Sales and marketing analytics
   - Sales KPI tracking per salesperson
   - Lead metrics and conversion tracking
   - Group capacity analytics
   - Marketing channel performance analytics

## Database Models Overview

### Leads App
- **Lead**: Core lead information
- **ImportLog**: Import history and statistics
- **LeadReminder**: Reminder tracking

### Scheduling App
- **Course**: Course information with teacher and pricing
- **Room**: Physical classroom/room information
- **Group**: Course groups with schedule and capacity
- **RoomOccupancy**: Room usage tracking by time slot

### Trials App
- **Trial**: Trial lesson scheduling and result tracking
- **TrialReminder**: Trial-specific reminder tracking

### Analytics App
- **SalesKPI**: Daily KPI metrics per salesperson
- **LeadMetrics**: Aggregated lead metrics and conversion rates
- **GroupAnalytics**: Group capacity and room usage analytics
- **MarketingAnalytics**: Marketing channel performance data

## Setup Instructions

### 1. Create Migrations

First, you need to create migrations for all the apps:

```bash
python manage.py makemigrations
```

This will create migration files for:
- scheduling app (Course, Room, Group, RoomOccupancy models)
- trials app (Trial, TrialReminder models)
- analytics app (SalesKPI, LeadMetrics, GroupAnalytics, MarketingAnalytics models)
- leads app (if new fields were added)
- import_service app (if needed)
- reminders app (if needed)

### 2. Apply Migrations

Apply all migrations to the database:

```bash
python manage.py migrate
```

### 3. Create Superuser (if needed)

Create an admin user:

```bash
python manage.py createsuperuser
```

### 4. Access Django Admin

Start the development server:

```bash
python manage.py runserver
```

Then access the admin panel at: `http://127.0.0.1:8000/admin/`

## Admin Interface Features

### Leads Admin
- View and manage leads
- Filter by status and source
- Search by name or phone
- Assign leads to salespeople

### Scheduling Admin
- Create and manage courses
- Create and manage rooms
- Create and manage groups (classes)
- Monitor room occupancy
- View free slots and capacity percentages

### Trials Admin
- Schedule trial lessons
- Track trial status (scheduled, attended, no-show, cancelled)
- Track trial results (pending, sales_offer, accepted, rejected)
- Manage trial reminders
- View overdue trials

### Analytics Admin
- View daily KPIs per salesperson
- Monitor conversion rates
- Track lead metrics by source
- Analyze group capacity usage
- Monitor marketing channel performance

## Admin UI Enhancements

### Color-Coded Status Indicators
- **Scheduling**: Green (low occupancy), Orange (50%+), Red (full)
- **Trials**: Blue (scheduled), Green (attended), Red (no-show), Gray (cancelled)
- **Analytics**: Green (>20%), Orange (10-20%), Red (<10%)

### Key Metrics Displayed
- Occupancy percentages
- Free slots in groups
- Trial status breakdown
- Conversion rates
- CPL (Cost Per Lead)
- CPA (Cost Per Acquisition)

## Key Features

### Lead Management
- Multi-source import (Instagram, Telegram, WhatsApp, etc.)
- Lead status tracking
- Salesperson assignment
- Follow-up reminders
- Contact deadline management

### Course & Group Management
- Create courses with pricing and teacher assignment
- Create groups with specific schedules
- Manage room allocation
- Track group capacity and free slots
- Monitor occupancy percentages

### Trial Management
- Schedule trials with groups
- Track trial attendance
- Generate sales offers post-trial
- Manage pre and post-trial reminders
- Monitor conversion from trial to enrollment

### Analytics & KPIs
- Daily salesperson KPIs
- Lead source breakdown
- Conversion rate tracking
- Group capacity optimization
- Marketing channel ROI analysis

## Fields and Data Types

### Group Model Example
- **name**: CharField (255)
- **days**: Choice field (odd, even, mon-sun, mon_wed_fri, tue_thu)
- **start_time**: TimeField
- **end_time**: TimeField
- **capacity**: IntegerField
- **current_students**: IntegerField (read-only in admin)
- **free_slots**: Computed property
- **occupancy_percent**: Computed property

### Trial Model Example
- **scheduled_date**: DateField
- **scheduled_time**: TimeField
- **status**: Choice (scheduled, attended, no-show, cancelled)
- **result**: Choice (pending, sales_offer, accepted, rejected)
- **salesperson_notes**: TextField
- **is_overdue**: Computed property
- **hours_until_trial**: Computed property

### SalesKPI Model Example
- **date**: DateField
- **salesperson**: ForeignKey(User)
- **new_contacts**: IntegerField
- **trials_attended**: IntegerField
- **enrollments**: IntegerField
- **conversion_percent**: Computed property
- **trial_to_conversion_percent**: Computed property

## Next Steps

1. Run migrations: `python manage.py makemigrations && python manage.py migrate`
2. Create superuser: `python manage.py createsuperuser`
3. Start server: `python manage.py runserver`
4. Access admin panel to manage data
5. Set up API endpoints for integration with frontend (if needed)
6. Configure reminders scheduled task (if using Celery)
7. Set up email/SMS notifications for reminders

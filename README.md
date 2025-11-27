# Leads Management System

A comprehensive leads management system with Django backend, Telegram bot integration, KPI tracking with automatic bonus/penalty calculations, Google Sheets sync, and SMS campaign support.

## Features

- **Lead Management**: Track leads from multiple sources with status management
- **KPI System**: Automatic calculation of bonuses and penalties based on configurable rules
- **Telegram Bot**: Sellers can view and manage their leads via Telegram (Aiogram 3)
- **Google Sheets Sync**: Automatic bidirectional sync with Google Sheets
- **SMS Campaigns**: Stub API for future SMS campaign integration
- **Admin Dashboard**: Full-featured admin interface with TailwindCSS
- **Scheduled Tasks**: Celery-based background jobs for sync and calculations

## Tech Stack

- **Backend**: Django 4.2
- **Frontend**: Django Templates + TailwindCSS CDN
- **Database**: PostgreSQL
- **Bot**: Aiogram 3
- **Scheduler**: Celery + Redis
- **Google Sheets**: gspread
- **Auth**: Django Admin (admin-only system)

## Project Structure

```
leads_management/
├── leads/              # Lead management app
├── bot/               # Telegram bot app
├── kpi/               # KPI calculation app
├── campaigns/         # SMS campaigns app
├── templates/         # HTML templates
├── static/            # Static files
├── leads_management/  # Project settings
├── manage.py
├── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis
- Google Cloud Service Account (for Sheets sync)
- Telegram Bot Token

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd leads_management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

### Using Docker

1. **Build and start services**
   ```bash
   docker-compose up -d
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

3. **Access the application**
   - Web: http://localhost:8000
   - Admin: http://localhost:8000/admin

## Configuration

### Environment Variables

See `.env.example` for all required environment variables:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: PostgreSQL settings
- `CELERY_BROKER_URL`: Redis URL for Celery
- `GOOGLE_SHEETS_CREDENTIALS_FILE`: Path to Google service account JSON
- `GOOGLE_SHEETS_SPREADSHEET_ID`: Google Sheets spreadsheet ID
- `TELEGRAM_BOT_TOKEN`: Telegram bot token
- `START_TELEGRAM_BOT`: Set to 'true' to start bot automatically

### Google Sheets Setup

1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create a Service Account
4. Download credentials JSON file
5. Share your Google Sheet with the service account email
6. Set `GOOGLE_SHEETS_CREDENTIALS_FILE` in `.env`

### Telegram Bot Setup

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Set `TELEGRAM_BOT_TOKEN` in `.env`
4. Set `START_TELEGRAM_BOT=true` to enable auto-start
5. Register sellers in Django admin with their Telegram IDs

## Usage

### Admin Dashboard

1. Access `/admin/` and log in
2. Create sellers and link them to Django users
3. Set Telegram IDs for sellers
4. Configure KPI rules in the KPI section
5. View leads, KPIs, and campaigns

### Telegram Bot

Sellers can interact with the bot using commands:
- `/start` - Start the bot
- `/leads` - View all leads
- `/new_leads` - View new leads
- `/stats` - View statistics
- `/kpi` - View KPI summary
- `/help` - Show help

### KPI Rules

1. Go to `/kpi/rules/` or Admin → KPI Rules
2. Create rules with:
   - Rule type (conversion rate, leads contacted, etc.)
   - Comparison operator (>=, <=, =, between)
   - Threshold values
   - Bonus and penalty amounts
   - Evaluation period
3. Rules are automatically calculated by Celery
4. View calculations at `/kpi/calculations/`

### Google Sheets Sync

The system automatically syncs with Google Sheets every 30 minutes (configurable).

Expected sheet format:
- Row 1: Headers (Name, Email, Phone, Company, Notes, Status, Seller)
- Row 2+: Data rows

### SMS Campaigns

SMS campaigns are currently stubs. API endpoints available:
- `POST /campaigns/api/send/` - Send SMS
- `GET /campaigns/api/status/` - Check campaign status

## Celery Tasks

Scheduled tasks (via Celery Beat):
- **Google Sheets Sync**: Every 30 minutes
- **KPI Calculation**: Every 6 hours
- **Monthly Summaries**: Daily at midnight
- **Lead Reminders**: Every 4 hours

Run Celery worker:
```bash
celery -A leads_management worker -l info
```

Run Celery beat:
```bash
celery -A leads_management beat -l info
```

## API Endpoints

### SMS API (Stubs)

**Send SMS**
```bash
POST /campaigns/api/send/
Content-Type: application/json

{
  "phone": "+1234567890",
  "message": "Your message here",
  "campaign_id": 1
}
```

**Check Status**
```bash
GET /campaigns/api/status/?campaign_id=1
```

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

The project follows PEP 8. Consider using:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Configure proper `ALLOWED_HOSTS`
3. Use a production WSGI server (e.g., Gunicorn)
4. Set up proper database backups
5. Configure SSL/TLS
6. Use environment variables for secrets
7. Set up monitoring and logging

### Gunicorn Example

```bash
gunicorn leads_management.wsgi:application --bind 0.0.0.0:8000
```

## Troubleshooting

### Bot not starting
- Check `TELEGRAM_BOT_TOKEN` is set correctly
- Ensure `START_TELEGRAM_BOT=true` in `.env`
- Check bot logs for errors

### Google Sheets sync failing
- Verify credentials file path
- Check service account has access to the sheet
- Verify spreadsheet ID is correct

### Celery tasks not running
- Ensure Redis is running
- Check Celery worker is running
- Verify Celery beat is running for scheduled tasks

## License

[Your License Here]

## Support

For issues and questions, please open an issue in the repository.


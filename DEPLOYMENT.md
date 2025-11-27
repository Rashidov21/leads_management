# Deployment Guide

## Production Deployment Checklist

- [ ] Use PostgreSQL database
- [ ] Configure Redis for Celery
- [ ] Use Gunicorn as WSGI server
- [ ] Configure Nginx as reverse proxy
- [ ] Enable HTTPS/SSL
- [ ] Set DEBUG=False
- [ ] Generate strong SECRET_KEY
- [ ] Configure proper logging
- [ ] Setup backup strategy
- [ ] Monitor system performance

## Environment Setup

### 1. Server Requirements

**Minimum:**
- 2 CPUs
- 2GB RAM
- 10GB storage
- Ubuntu 20.04 LTS or similar

**Recommended:**
- 4+ CPUs
- 4GB+ RAM
- 50GB+ storage
- Ubuntu 22.04 LTS

### 2. Install Dependencies

```bash
sudo apt-get update
sudo apt-get install -y \
    python3.11 \
    python3-pip \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    curl \
    git
```

### 3. Create Application User

```bash
sudo useradd -m -s /bin/bash crm
sudo su - crm
```

### 4. Clone Repository

```bash
cd /home/crm
git clone https://github.com/yourname/leads_management.git
cd leads_management/crm_backend
```

### 5. Setup Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure PostgreSQL

```bash
sudo -u postgres psql

CREATE DATABASE crm_db;
CREATE USER crm_user WITH PASSWORD 'strong_password';
ALTER ROLE crm_user SET client_encoding TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE crm_db TO crm_user;
\q
```

### 7. Configure Environment

```bash
cp .env.example .env
nano .env
```

Set production values:
```
SECRET_KEY=generate-a-strong-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=your_postgresql_password
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 8. Run Migrations

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## Gunicorn Setup

### 1. Install Gunicorn

```bash
pip install gunicorn
```

### 2. Create Systemd Service

```bash
sudo nano /etc/systemd/system/crm-web.service
```

```ini
[Unit]
Description=CRM Web Service
After=network.target

[Service]
User=crm
WorkingDirectory=/home/crm/leads_management/crm_backend
Environment="PATH=/home/crm/leads_management/crm_backend/venv/bin"
ExecStart=/home/crm/leads_management/crm_backend/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/crm/gunicorn-access.log \
    --error-logfile /var/log/crm/gunicorn-error.log \
    crm_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 3. Enable Service

```bash
sudo mkdir -p /var/log/crm
sudo chown crm:crm /var/log/crm
sudo systemctl daemon-reload
sudo systemctl enable crm-web
sudo systemctl start crm-web
sudo systemctl status crm-web
```

## Celery Worker Setup

### 1. Create Worker Service

```bash
sudo nano /etc/systemd/system/crm-celery.service
```

```ini
[Unit]
Description=CRM Celery Worker
After=network.target

[Service]
User=crm
WorkingDirectory=/home/crm/leads_management/crm_backend
Environment="PATH=/home/crm/leads_management/crm_backend/venv/bin"
ExecStart=/home/crm/leads_management/crm_backend/venv/bin/celery -A crm_project worker \
    -l info \
    -Q imports,reminders \
    --logfile=/var/log/crm/celery-worker.log

[Install]
WantedBy=multi-user.target
```

### 2. Create Beat Service

```bash
sudo nano /etc/systemd/system/crm-celery-beat.service
```

```ini
[Unit]
Description=CRM Celery Beat Scheduler
After=network.target

[Service]
User=crm
WorkingDirectory=/home/crm/leads_management/crm_backend
Environment="PATH=/home/crm/leads_management/crm_backend/venv/bin"
ExecStart=/home/crm/leads_management/crm_backend/venv/bin/celery -A crm_project beat \
    -l info \
    --logfile=/var/log/crm/celery-beat.log \
    --pidfile=/var/run/crm/celerybeat.pid

[Install]
WantedBy=multi-user.target
```

### 3. Enable Services

```bash
sudo mkdir -p /var/run/crm
sudo chown crm:crm /var/run/crm
sudo systemctl daemon-reload
sudo systemctl enable crm-celery crm-celery-beat
sudo systemctl start crm-celery crm-celery-beat
```

## Nginx Configuration

### 1. Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/crm
```

```nginx
upstream crm_wsgi {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    client_max_body_size 10M;
    
    location /static/ {
        alias /home/crm/leads_management/crm_backend/staticfiles/;
    }
    
    location /media/ {
        alias /home/crm/leads_management/crm_backend/media/;
    }
    
    location / {
        proxy_pass http://crm_wsgi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### 2. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/crm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Certificate Setup (Let's Encrypt)

### 1. Install Certbot

```bash
sudo apt-get install certbot python3-certbot-nginx
```

### 2. Generate Certificate

```bash
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

### 3. Auto-Renewal

```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Monitoring & Logging

### 1. Configure Logging

```bash
sudo nano /home/crm/leads_management/crm_backend/crm_project/settings.py
```

Add logging configuration:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/crm/django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 2. Setup Log Rotation

```bash
sudo nano /etc/logrotate.d/crm
```

```
/var/log/crm/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 crm crm
    sharedscripts
    postrotate
        systemctl reload crm-web crm-celery > /dev/null 2>&1 || true
    endscript
}
```

### 3. Monitor Services

```bash
# Check service status
sudo systemctl status crm-web
sudo systemctl status crm-celery
sudo systemctl status crm-celery-beat

# View logs
tail -f /var/log/crm/django.log
tail -f /var/log/crm/celery-worker.log
tail -f /var/log/crm/gunicorn-access.log
```

## Database Backup

### 1. Automated Daily Backup

```bash
sudo nano /home/crm/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/crm/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/crm_db_$TIMESTAMP.sql.gz"

mkdir -p $BACKUP_DIR

pg_dump -U crm_user crm_db | gzip > $BACKUP_FILE

# Keep only last 30 days of backups
find $BACKUP_DIR -name "crm_db_*.sql.gz" -mtime +30 -delete

echo "Database backed up to $BACKUP_FILE"
```

### 2. Schedule with Cron

```bash
sudo crontab -e
```

Add:
```
0 2 * * * /home/crm/backup_db.sh >> /var/log/crm/backup.log 2>&1
```

## Performance Optimization

### 1. Database Connection Pooling

Install pgBouncer:
```bash
sudo apt-get install pgbouncer
```

### 2. Redis Configuration

```bash
sudo nano /etc/redis/redis.conf
```

Key settings:
```
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### 3. Celery Worker Optimization

Adjust worker count in service file:
```bash
# For 4 CPU server, use 4-8 workers
--concurrency=8
```

## Health Checks

### 1. Application Health Check Endpoint

Add to `urls.py`:
```python
from django.http import JsonResponse

def health(request):
    return JsonResponse({'status': 'healthy'})
```

### 2. Nginx Health Check

Add location to nginx config:
```nginx
location /health/ {
    access_log off;
    proxy_pass http://crm_wsgi;
}
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
sudo journalctl -u crm-web -n 50
sudo journalctl -u crm-celery -n 50
```

### Database Connection Issues
```bash
# Test database connection
psql -U crm_user -d crm_db -h localhost
```

### Celery Tasks Not Running
```bash
# Check Redis connection
redis-cli ping
# Should return: PONG
```

### High Memory Usage
```bash
# Check memory usage
free -h
ps aux | grep python
```

## Backup & Recovery

### Create Full Backup
```bash
pg_dump -U crm_user crm_db > backup.sql
tar -czf crm_backup.tar.gz /home/crm/leads_management/
```

### Restore Database
```bash
psql -U crm_user crm_db < backup.sql
```

## Monitoring Tools

Recommended monitoring stack:
- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **Sentry** - Error tracking
- **New Relic** - Performance monitoring

## Support

For deployment issues, contact: devops@educationcrm.com

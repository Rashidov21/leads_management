# 📋 Server Commands - Quick Reference

## Server'ga Ulanish

```bash
ssh username@server_ip
# yoki
ssh -i /path/to/key.pem username@server_ip
```

---

## Tezkor Deployment

```bash
# 1. Loyiha papkasiga o'tish
cd /path/to/leads_management

# 2. Deploy script ishga tushirish
bash deploy.sh
```

**Tayyor!** Script avtomatik ravishda:
- ✅ Backup oladi
- ✅ Git pull qiladi
- ✅ Dependencies yangilaydi
- ✅ Migration bajaradi
- ✅ Static files collect qiladi
- ✅ Gunicorn restart qiladi
- ✅ Celery restart qiladi
- ✅ Nginx reload qiladi

---

## Qo'lda Commands (Agar script ishlamasa)

### 1. Backup
```bash
python manage.py dumpdata crm_app.Lead crm_app.FollowUp > backup_$(date +%Y%m%d_%H%M%S).json
```

### 2. Git Pull
```bash
git pull origin main
```

### 3. Virtual Environment
```bash
source venv/bin/activate
```

### 4. Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### 5. Migration
```bash
python manage.py migrate
```

### 6. Static Files
```bash
python manage.py collectstatic --noinput
```

### 7. Restart Services
```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celerybeat
sudo systemctl reload nginx
```

---

## Service Management

### Status Tekshirish
```bash
sudo systemctl status gunicorn
sudo systemctl status celery
sudo systemctl status celerybeat
sudo systemctl status nginx
```

### Restart
```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celerybeat
```

### Start/Stop
```bash
sudo systemctl start gunicorn
sudo systemctl stop gunicorn
```

### Enable/Disable (Autostart)
```bash
sudo systemctl enable gunicorn
sudo systemctl disable gunicorn
```

---

## Log'larni Ko'rish

### Real-time Logs
```bash
sudo journalctl -u gunicorn -f
sudo journalctl -u celery -f
```

### Oxirgi N ta log
```bash
sudo journalctl -u gunicorn -n 50
sudo journalctl -u celery -n 50
sudo journalctl -u nginx -n 50
```

### Bugungi log'lar
```bash
sudo journalctl -u gunicorn --since today
```

### Error log'lar
```bash
sudo journalctl -u gunicorn -p err
```

---

## Django Management Commands

### Shell
```bash
python manage.py shell
```

### Database Backup/Restore
```bash
# Backup
python manage.py dumpdata > backup.json
python manage.py dumpdata crm_app > crm_backup.json

# Restore
python manage.py loaddata backup.json
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Migration Commands
```bash
python manage.py showmigrations
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --fake crm_app 0001  # Fake migration
```

---

## Celery Commands

### Manual Start (Agar service yo'q bo'lsa)
```bash
# Worker
celery -A crm_project worker -l info

# Beat
celery -A crm_project beat -l info

# Background'da
nohup celery -A crm_project worker -l info &
nohup celery -A crm_project beat -l info &
```

### Stop
```bash
pkill -f "celery worker"
pkill -f "celery beat"
```

### Celery Status
```bash
celery -A crm_project inspect active
celery -A crm_project inspect stats
```

---

## Testing Commands

### Django Shell Test
```bash
python manage.py shell
```

```python
from crm_app.models import Lead, FollowUp
from django.contrib.auth.models import User

# Follow-up'lar
FollowUp.objects.count()
FollowUp.objects.filter(status='pending')

# Eng oxirgi lidlar
Lead.objects.latest('created_at')
Lead.objects.filter(assigned_sales__isnull=False).count()

# Follow-up'siz lidlar
Lead.objects.filter(followups__isnull=True, assigned_sales__isnull=False).count()
```

### Run Tests
```bash
python manage.py test
python manage.py test crm_app
python manage.py test crm_app.tests.TestLeadModel
```

---

## Nginx Commands

### Test Config
```bash
sudo nginx -t
```

### Reload/Restart
```bash
sudo systemctl reload nginx
sudo systemctl restart nginx
```

### Logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## Git Commands

### Status
```bash
git status
git log --oneline -5
```

### Pull/Reset
```bash
git pull origin main
git fetch origin
git reset --hard origin/main  # Dikkat! Local o'zgarishlar yo'qoladi
```

### Rollback
```bash
git log --oneline
git reset --hard COMMIT_ID
```

---

## Permission Issues

### File Permissions
```bash
# Owner o'zgartirish
sudo chown -R username:username /path/to/leads_management

# Permissions o'zgartirish
chmod +x deploy.sh
chmod 755 manage.py
```

### Service Permissions
```bash
# Service file'ni tahrirlash
sudo nano /etc/systemd/system/gunicorn.service

# Reload daemon
sudo systemctl daemon-reload
```

---

## Disk Space

### Check Disk Space
```bash
df -h
du -sh /path/to/leads_management
```

### Clean Up
```bash
# Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Old backups
rm backup_*.json
```

---

## Quick Troubleshooting

### Service ishlamasa:
```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn celery
sudo journalctl -u gunicorn -n 100
```

### Database locked:
```bash
# SQLite uchun
lsof | grep db.sqlite3
kill -9 PID
```

### Port busy:
```bash
sudo lsof -i :8000
sudo kill -9 PID
```

---

## Environment Variables

### Ko'rish
```bash
printenv | grep DJANGO
echo $DJANGO_SETTINGS_MODULE
```

### O'rnatish
```bash
export DJANGO_SETTINGS_MODULE=crm_project.settings
export DEBUG=False
```

---

## Copy/Paste Ready Commands

### Full Deployment:
```bash
cd /path/to/leads_management && bash deploy.sh
```

### Quick Restart:
```bash
sudo systemctl restart gunicorn celery celerybeat && sudo systemctl reload nginx
```

### View All Logs:
```bash
sudo journalctl -u gunicorn -u celery -u nginx -n 50
```

### Test Everything:
```bash
python manage.py shell -c "from crm_app.models import Lead, FollowUp; print(f'Leads: {Lead.objects.count()}, Follow-ups: {FollowUp.objects.count()}')"
```

---

## Emergency Commands

### Server qayta ishga tushirish:
```bash
sudo reboot
```

### Hamma service'larni to'xtatish:
```bash
sudo systemctl stop gunicorn celery celerybeat nginx
```

### Hamma service'larni ishga tushirish:
```bash
sudo systemctl start gunicorn celery celerybeat nginx
```

---

**Eslatma:** Service nomlari serveringizda boshqacha bo'lishi mumkin. `systemctl list-units --type=service` bilan tekshiring.


# 🚀 Deployment Guide

## Tezkor Deployment (VPS Server)

### 1. Local'dan Push Qilish

```bash
# Local computer'da
git add .
git commit -m "Your commit message"
git push origin main
```

✅ **BAJARILDI!** (2024-12-17)

---

### 2. Server'da Deploy Qilish

#### Variant A: Avtomatik Script (Tavsiya)

```bash
# SSH orqali serverga ulanish
ssh username@server_ip

# Loyiha papkasiga o'tish
cd /path/to/leads_management

# Deploy scriptni ishga tushirish
bash deploy.sh
```

#### Variant B: Qo'lda Deploy

```bash
# 1. Serverga ulanish
ssh username@server_ip

# 2. Loyiha papkasiga o'tish
cd /path/to/leads_management

# 3. Backup olish
python manage.py dumpdata crm_app.Lead crm_app.FollowUp > backup_$(date +%Y%m%d_%H%M%S).json

# 4. Kod pull qilish
git pull origin main

# 5. Virtual environment
source venv/bin/activate

# 6. Dependencies
pip install -r requirements.txt --upgrade

# 7. Migration
python manage.py migrate

# 8. Static files
python manage.py collectstatic --noinput

# 9. Service'larni restart qilish
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celerybeat
sudo systemctl reload nginx
```

---

## 3. Test Qilish

### Browser'da Test:

1. Loyihaga kiring: `https://your-domain.com`
2. Login qiling
3. Google Sheets import tugmasini bosing
4. Yangi lid import qiling
5. Follow-up'lar avtomatik yaratilganini tekshiring:
   - Lidlar sahifasiga o'ting
   - Yangi lidni oching
   - "Qayta aloqalar" bo'limini tekshiring

### Server'da Test:

```bash
python manage.py shell
```

```python
from crm_app.models import Lead, FollowUp

# Eng oxirgi lidni tekshirish
latest_lead = Lead.objects.latest('created_at')
print(f"Lid: {latest_lead.name}")
print(f"Assigned sales: {latest_lead.assigned_sales}")
print(f"Follow-up'lar: {latest_lead.followups.count()}")

# Follow-up tafsilotlari
for f in latest_lead.followups.all():
    print(f"- {f.notes} | {f.due_date}")
```

---

## 4. Log'larni Tekshirish

```bash
# Gunicorn logs
sudo journalctl -u gunicorn -n 50

# Celery logs
sudo journalctl -u celery -n 50

# Real-time logs
sudo journalctl -u gunicorn -f  # Gunicorn
sudo journalctl -u celery -f    # Celery
```

---

## 5. Service Status

```bash
# Status tekshirish
sudo systemctl status gunicorn
sudo systemctl status celery
sudo systemctl status celerybeat
sudo systemctl status nginx

# Service'larni restart qilish
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celerybeat
sudo systemctl reload nginx
```

---

## Muammo Bo'lsa (Troubleshooting)

### Follow-up'lar yaratilmasa:

```bash
# Django shell'da
python manage.py shell
```

```python
from crm_app.models import Lead, FollowUp
from django.utils import timezone

# Follow-up'siz lidlar
leads_without_followups = Lead.objects.filter(
    followups__isnull=True,
    assigned_sales__isnull=False
)

print(f"Follow-up'siz lidlar: {leads_without_followups.count()}")

# Qo'lda follow-up yaratish (agar kerak bo'lsa)
from datetime import timedelta
for lead in leads_without_followups[:5]:  # Birinchi 5 tasi
    FollowUp.objects.create(
        lead=lead,
        sales=lead.assigned_sales,
        due_date=timezone.now() + timedelta(minutes=5),
        notes="Qo'lda yaratilgan - deploy'dan keyin"
    )
    print(f"✅ Follow-up yaratildi: {lead.name}")
```

### Service ishlamasa:

```bash
# Service'ni qayta boshlash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl restart celery

# Error log'larni ko'rish
sudo journalctl -u gunicorn -n 100
sudo journalctl -u celery -n 100
```

### Eski versiyaga qaytish (Rollback):

```bash
git log --oneline  # Commit ID'larni ko'rish
git reset --hard COMMIT_ID
sudo systemctl restart gunicorn celery
```

---

## Deployment Checklist

Har bir deployment'da tekshiring:

- [ ] Local'da commit va push qilindi
- [ ] Serverga SSH ulanish
- [ ] Backup olindi
- [ ] Git pull bajarildi
- [ ] Virtual environment activate
- [ ] Dependencies yangilandi
- [ ] Migration bajarildi
- [ ] Static files collect qilindi
- [ ] Gunicorn restart qilindi
- [ ] Celery restart qilindi
- [ ] Nginx reload qilindi
- [ ] Browser'da test qilindi
- [ ] Follow-up'lar yaratilishi test qilindi
- [ ] Log'lar xatosiz

---

## Muhim Eslatmalar

1. ⚠️ **Celery muhim!** Follow-up notification'lar Celery orqali yuboriladi
2. 💾 **Backup:** Har doim deploy'dan oldin backup oling
3. 🔒 **Permissions:** Agar permission xatolari bo'lsa, `sudo` ishlating
4. 📝 **Service nomlari:** Service nomlari serveringizda boshqacha bo'lishi mumkin
5. ⏱️ **Taxminiy vaqt:** To'liq deployment 5-10 daqiqa davom etadi

---

## Bu Deployment'da O'zgartirish

**Sana:** 2024-12-17

**O'zgarishlar:**
- ✅ Google Sheets import'da follow-up avtomatik yaratish
- ✅ Excel import'da follow-up avtomatik yaratish  
- ✅ Signal muammosi hal qilindi (ikki marta save)
- ✅ Frontend: Follow-up nomlarini o'zbekcha qilindi
- ✅ Takliflar sahifasi accordion formatida
- ✅ Google Sheets manual import tugmasi

**Texnik:**
- `crm_app/services.py` - import_new_leads metodida ikki marta save muammosi
- `crm_app/views.py` - excel_import metodida ikki marta save muammosi
- Lead faqat assigned_sales bilan birga save bo'ladi
- Signal to'g'ri ishlaydi va follow-up yaratadi

**Migration:** Kerak emas (faqat kod o'zgarishlari)

**Testing:** Import qilish va follow-up'lar yaratilishini tekshirish

---

## Keyingi Deployment Uchun

```bash
# Local'da
git add .
git commit -m "Your changes"
git push origin main

# Server'da
ssh your-server
cd /path/to/leads_management
bash deploy.sh
```

Hammasi shu! 🎉


# 🚀 SERVER'GA DEPLOY QILISH - HAR ENDI QILISH KERAK

## ✅ TAYYOR BO'LGAN ISHLAR (Local)

1. ✅ Barcha o'zgarishlar commit qilindi
2. ✅ GitHub'ga push qilindi (3 ta commit)
3. ✅ Deployment scriptlar yaratildi

---

## 📋 ENDI SIZNING QILISHINGIZ KERAK

### 1️⃣ Server'ga Ulanish

```bash
ssh username@server_ip
```

**Yoki kalit bilan:**
```bash
ssh -i /path/to/key.pem username@server_ip
```

---

### 2️⃣ Loyiha Papkasiga O'tish

```bash
cd /path/to/leads_management
```

**Masalan:**
- `cd /var/www/leads_management`
- `cd /home/username/leads_management`
- `cd ~/leads_management`

---

### 3️⃣ Deploy Qilish (2 ta variant)

#### ⭐ VARIANT A: Avtomatik (Tavsiya)

```bash
bash deploy.sh
```

Bu script avtomatik ravishda:
- Backup oladi
- Kodlarni pull qiladi  
- Dependencies yangilaydi
- Migration bajaradi
- Static files'ni collect qiladi
- Barcha service'larni restart qiladi

#### VARIANT B: Qo'lda

```bash
# 1. Backup
python manage.py dumpdata crm_app.Lead crm_app.FollowUp > backup_$(date +%Y%m%d_%H%M%S).json

# 2. Pull
git pull origin main

# 3. Virtual environment
source venv/bin/activate

# 4. Dependencies
pip install -r requirements.txt --upgrade

# 5. Migration
python manage.py migrate

# 6. Static
python manage.py collectstatic --noinput

# 7. Restart
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celerybeat
sudo systemctl reload nginx
```

---

### 4️⃣ Test Qilish

#### Browser'da:

1. Saytni oching: `https://your-domain.com`
2. Login qiling
3. "Lidlar" sahifasiga o'ting
4. "Google Sheets Import" tugmasini bosing
5. Yangi lidni oching
6. "Qayta aloqalar" bo'limida follow-up borligini tekshiring

#### Server'da:

```bash
python manage.py shell
```

```python
from crm_app.models import Lead, FollowUp

# Oxirgi lidni tekshirish
lead = Lead.objects.latest('created_at')
print(f"Lid: {lead.name}")
print(f"Sales: {lead.assigned_sales}")
print(f"Follow-ups: {lead.followups.count()}")
```

---

## 📊 SERVICE STATUS TEKSHIRISH

```bash
sudo systemctl status gunicorn
sudo systemctl status celery
sudo systemctl status celerybeat
```

**Agar qizil (failed) bo'lsa:**

```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celerybeat
```

---

## 📝 LOG'LARNI KO'RISH

```bash
# Gunicorn
sudo journalctl -u gunicorn -n 50

# Celery
sudo journalctl -u celery -n 50

# Real-time
sudo journalctl -u gunicorn -f
```

---

## ❓ MUAMMO BO'LSA

### Celerybeat pid file xatosi:

```bash
rm celerybeat.pid
sudo systemctl restart celerybeat
```

### Service topilmasa:

Service nomlari boshqacha bo'lishi mumkin:

```bash
# Service'larni ko'rish
systemctl list-units --type=service | grep -E "gunicorn|celery"

# Keyin to'g'ri nom bilan restart qilish
sudo systemctl restart your-service-name
```

### Follow-up'lar ko'rinmasa:

```bash
python manage.py shell
```

```python
from crm_app.models import FollowUp
from django.utils import timezone

# Pending follow-up'lar
followups = FollowUp.objects.filter(status='pending', due_date__lte=timezone.now())
print(f"Ko'rinishi kerak bo'lgan: {followups.count()}")

# Barcha follow-up'lar
print(f"Jami: {FollowUp.objects.count()}")
```

---

## 📚 QO'SHIMCHA HUJJATLAR

Loyihada endi 3 ta qo'llanma bor:

1. **`DEPLOYMENT.md`** - To'liq deployment guide
2. **`SERVER_COMMANDS.md`** - Barcha server commandlar
3. **`deploy.sh`** - Avtomatik deployment script

---

## ⚡ TEZKOR QADAMLAR

```bash
# 1. Server'ga ulanish
ssh username@server_ip

# 2. Loyihaga o'tish  
cd /path/to/leads_management

# 3. Deploy qilish
bash deploy.sh

# 4. Test qilish (browser'da)
```

**Taxminiy vaqt:** 5-10 daqiqa

---

## ✅ DEPLOYMENT CHECKLIST

Deploy qilayotganda tekshiring:

- [ ] Server'ga ulandingizmi?
- [ ] To'g'ri papkaga o'tdingizmi?
- [ ] `bash deploy.sh` ishga tushdimi?
- [ ] Barcha service'lar restart bo'ldimi?
- [ ] Browser'da sayt ochilmoqdami?
- [ ] Login qila olasizmi?
- [ ] Google Sheets import ishlayaptimi?
- [ ] Yangi lidda follow-up yaratilmoqdami?

---

## 🎯 MAQSAD

Deploy'dan keyin:

✅ Google Sheets'dan import qilingan lidlar uchun avtomatik follow-up yaratiladi
✅ Excel'dan import qilingan lidlar uchun avtomatik follow-up yaratiladi  
✅ Frontend o'zbek tilida (Qayta aloqalar, Muddati o'tgan)
✅ Takliflar accordion shaklida
✅ Manual Google Sheets import tugmasi

---

## 🆘 YORDAM KERAK BO'LSA

1. Log'larni ko'ring: `sudo journalctl -u gunicorn -n 100`
2. Service status: `sudo systemctl status gunicorn celery`
3. Menga log'lar yoki error messageni yuboring

---

## 🎉 TAYYOR!

Deploy qilish uchun faqat 3 ta command:

```bash
ssh username@server_ip
cd /path/to/leads_management
bash deploy.sh
```

**Omad!** 🚀


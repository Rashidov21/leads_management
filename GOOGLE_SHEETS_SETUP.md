# Google Sheets Avtomatik Import - O'rnatish Qo'llanmasi

## 📋 Umumiy Ma'lumot

Bu qo'llanma Instagram Ads va boshqa manbalardan kelgan lidlarni Google Sheets orqali avtomatik import qilish uchun tizimni sozlashda yordam beradi.

Tizim har **5 daqiqada** Google Sheets'ni tekshiradi va yangi qo'shilgan lidlarni avtomatik ravishda CRM tizimiga import qiladi.

---

## 🚀 Tezkor Boshlash

### 1. Google Cloud Setup

#### 1.1. Google Cloud Console'ga kirish
- [Google Cloud Console](https://console.cloud.google.com/) ga kiring
- Yangi project yarating yoki mavjudini tanlang

#### 1.2. Google Sheets API'ni yoqish
1. **APIs & Services** → **Library**
2. "Google Sheets API" ni qidiring
3. **ENABLE** tugmasini bosing

#### 1.3. Service Account yaratish
1. **APIs & Services** → **Credentials**
2. **Create Credentials** → **Service Account**
3. Service Account nomi kiriting: `crm-sheets-importer`
4. **CREATE AND CONTINUE**
5. Role tanlang: **Editor** yoki **Viewer** (faqat o'qish uchun)
6. **DONE**

#### 1.4. JSON Key yaratish
1. Yaratilgan Service Account'ga kiring
2. **Keys** tabiga o'ting
3. **Add Key** → **Create New Key**
4. Format: **JSON**
5. **CREATE** - JSON fayl avtomatik yuklab olinadi

#### 1.5. JSON faylni saqlash
JSON faylni loyiha papkasiga qo'ying:
```
leads_management/
├── google_credentials.json  ← Bu yerga qo'ying
└── ...
```

**DIQQAT:** `.gitignore` faylida `google_credentials.json` bo'lishini tekshiring!

---

### 2. Google Sheets Tayyorlash

#### 2.1. Google Sheets yaratish yoki mavjudini ochish
- Instagram Ads'dan kelgan ma'lumotlar uchun Google Sheets yarating
- Yoki mavjud sheet'ni ishlating

#### 2.2. Sheet formatini sozlash

**Talab qilinadigan ustunlar:**

| A (name) | B (phone) | C (source) | D (course) | E (secondary_phone) |
|----------|-----------|------------|------------|---------------------|
| Ali Valiyev | 998901234567 | instagram | Python | 998907654321 |
| Aziza Karimova | 998931234567 | instagram | English | |
| Bobur Aliyev | 998941234567 | telegram | Frontend | |

**Ustun nomlari (birinchi qator - header):**
- `name` yoki `Name` - Ism (majburiy)
- `phone` yoki `Phone` - Telefon (majburiy)
- `source` yoki `Source` - Manba (instagram, telegram, youtube, etc.)
- `course` yoki `Course` - Qiziqayotgan kurs (ixtiyoriy)
- `secondary_phone` yoki `Secondary Phone` - Qo'shimcha telefon (ixtiyoriy)

**Eslatma:** Ustun nomlari katta-kichik harfga sezgir emas.

#### 2.3. Service Account'ga ruxsat berish

1. Google Sheets'ni oching
2. **Share** tugmasini bosing
3. Service Account email'ini qo'shing:
   - JSON fayldagi `client_email` qiymatini ko'chiring
   - Masalan: `crm-sheets-importer@project-id.iam.gserviceaccount.com`
4. Ruxsat: **Viewer** (faqat o'qish) yoki **Editor**
5. **Share** tugmasini bosing

#### 2.4. Spreadsheet ID'ni olish

Google Sheets URL'dan ID'ni ko'chiring:
```
https://docs.google.com/spreadsheets/d/1ABC123def456GHI789jkl/edit
                                        ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                                        Bu Spreadsheet ID
```

---

### 3. Loyiha Konfiguratsiyasi

#### 3.1. .env faylni yaratish (agar yo'q bo'lsa)
```bash
cp env.sample .env
```

#### 3.2. .env faylni tahrirlash

**Variant 1: JSON fayl yo'lini ko'rsatish (Tavsiya etiladi)**
```bash
# .env
GOOGLE_SHEETS_CREDENTIALS=google_credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=1ABC123def456GHI789jkl
GOOGLE_SHEETS_WORKSHEET_NAME=Sheet1
```

**Variant 2: JSON content'ni to'g'ridan-to'g'ri**
```bash
# .env
GOOGLE_SHEETS_CREDENTIALS='{"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}'
GOOGLE_SHEETS_SPREADSHEET_ID=1ABC123def456GHI789jkl
GOOGLE_SHEETS_WORKSHEET_NAME=Sheet1
```

---

### 4. Test Qilish

#### 4.1. Django shell orqali test
```bash
python manage.py shell
```

```python
# Test connection
from crm_app.services import GoogleSheetsService

result = GoogleSheetsService.test_connection(
    'YOUR_SPREADSHEET_ID',  # .env'dagi ID
    'Sheet1'
)
print(result)
# Output: {'success': True, 'message': 'Ulanish muvaffaqiyatli! ...'}

# Test import
result = GoogleSheetsService.import_new_leads(
    'YOUR_SPREADSHEET_ID',
    'Sheet1'
)
print(result)
# Output: {'imported': 2, 'skipped': 0, 'errors': [], 'leads': [123, 124]}
```

#### 4.2. Celery task orqali test
```bash
# Django shell
python manage.py shell
```

```python
from crm_app.tasks import import_leads_from_google_sheets

# Task'ni qo'lda ishga tushirish
result = import_leads_from_google_sheets.delay()
print(result.get())  # Natijani kutish
```

---

### 5. Ishga Tushirish

#### 5.1. Celery Worker va Beat'ni ishga tushirish

**Windows:**
```bash
# Terminal 1: Celery Worker
run_celery_worker.bat

# Terminal 2: Celery Beat
run_celery_beat.bat
```

**Linux/Mac:**
```bash
# Terminal 1: Celery Worker
celery -A crm_project worker --loglevel=info

# Terminal 2: Celery Beat
celery -A crm_project beat --loglevel=info
```

#### 5.2. Log'larni kuzatish

**Celery Beat log'da quyidagilarni ko'rasiz:**
```
[2025-12-17 10:00:00] Google Sheets import task ishga tushdi
[2025-12-17 10:00:02] Google Sheets: 3 ta yangi lid import qilindi
```

**Telegram'da notification:**
```
📊 Google Sheets Auto-Import
==============================

✅ Import qilindi: 3 ta lid
⏭ O'tkazib yuborildi: 1 ta
```

---

## 🔧 Sozlamalar va Moslashtirish

### Ustun Nomlarini O'zgartirish

Agar sizning Google Sheets'da ustun nomlari boshqacha bo'lsa, `services.py` dagi `import_new_leads()` funksiyasini moslashtiring:

```python
# Masalan, agar ustunlar:
# Ism | Telefon | Manba | Kurs

result = GoogleSheetsService.import_new_leads(
    spreadsheet_id='...',
    worksheet_name='Sheet1',
    name_column='Ism',           # Default: 'name'
    phone_column='Telefon',      # Default: 'phone'
    source_column='Manba',       # Default: 'source'
    interested_course_column='Kurs'  # Default: 'course'
)
```

### Import Chastotasini O'zgartirish

`crm_project/settings.py` faylida:

```python
CELERY_BEAT_SCHEDULE = {
    # ...
    'import-leads-from-google-sheets': {
        'task': 'crm_app.tasks.import_leads_from_google_sheets',
        'schedule': crontab(minute='*/10'),  # Har 10 daqiqada
        # yoki
        # 'schedule': crontab(minute='*/3'),   # Har 3 daqiqada
        # yoki
        # 'schedule': crontab(minute='*/15'),  # Har 15 daqiqada
    },
}
```

### Cache'ni Tozalash

Agar barcha lidlarni qayta import qilish kerak bo'lsa, cache'ni tozalang:

```bash
python manage.py shell
```

```python
from django.core.cache import cache

# Bitta sheet uchun
cache_key = 'google_sheets_last_row_YOUR_SPREADSHEET_ID_Sheet1'
cache.delete(cache_key)

# Barcha cache
cache.clear()
```

---

## 🐛 Muammolarni Hal Qilish

### Xatolik: "GOOGLE_SHEETS_CREDENTIALS sozlanmagan!"

**Yechim:**
- `.env` faylda `GOOGLE_SHEETS_CREDENTIALS` to'g'ri sozlanganligini tekshiring
- JSON fayl yo'li to'g'ri ekanligini tekshiring
- JSON content to'g'ri format ekanligini tekshiring

### Xatolik: "Permission denied"

**Yechim:**
- Service Account email'i Google Sheets'ga share qilinganligini tekshiring
- Ruxsat darajasi Viewer yoki Editor ekanligini tekshiring

### Xatolik: "Spreadsheet not found"

**Yechim:**
- Spreadsheet ID to'g'ri ekanligini tekshiring
- Worksheet nomi to'g'ri ekanligini tekshiring (default: 'Sheet1')

### Lidlar import qilinmayapti

**Tekshirish:**
1. **Celery Beat ishlayaptimi?**
   ```bash
   # Log'larda "Google Sheets import task ishga tushdi" ni qidiring
   ```

2. **Google Sheets'da yangi qatorlar bormi?**
   - Birinchi import'dan keyin faqat yangi qatorlar import qilinadi

3. **Telefon raqam duplicate emasmi?**
   - Mavjud telefon raqamlar o'tkazib yuboriladi

4. **Ma'lumotlar to'g'rimi?**
   - `name` va `phone` majburiy fieldlar
   - Telefon raqam formati: 998XXXXXXXXX

### Cache muammolari

**Yechim:**
```python
# Django shell
from django.core.cache import cache
cache.clear()
```

---

## 📊 Monitoring va Statistika

### Telegram Notifications

Har safar yangi lidlar import qilinganda:
- Admin chat'ga to'liq hisobot yuboriladi
- Manager/Admin telegram group'lariga qisqa xabar yuboriladi

### Log Fayllar

Celery log'larida quyidagi ma'lumotlar mavjud:
```
[2025-12-17 10:00:00] Google Sheets import task ishga tushdi
[2025-12-17 10:00:02] Google Sheets: 3 ta yangi lid import qilindi
```

### Django Admin

Admin panel'dan:
- `/admin/crm_app/lead/` - Barcha lidlar
- Filter: Source = "Google Sheets"
- Notes maydonida: "Google Sheets'dan avtomatik import (row X)"

---

## 🔒 Xavfsizlik

### JSON Credentials Himoyasi

1. **.gitignore'ga qo'shing:**
   ```
   google_credentials.json
   .env
   ```

2. **Serverda faqat o'qish ruxsati:**
   ```bash
   chmod 600 google_credentials.json
   chmod 600 .env
   ```

3. **Production'da environment variable'dan foydalaning:**
   - Heroku: Config Vars
   - AWS: Secrets Manager
   - Docker: Environment variables

### Service Account Ruxsatlari

- Minimal ruxsat: **Viewer** (faqat o'qish)
- Faqat kerakli sheet'larga share qiling
- Bir nechta project uchun alohida Service Account'lar

---

## 📝 Instagram Ads Integration

### Instagram Lead Ads Setup

1. **Facebook Business Manager'da:**
   - Lead Ads forma yarating
   - CRM Integration → Google Sheets

2. **Google Sheets'ga ulanish:**
   - Facebook → Settings → Lead Access
   - Google Sheets'ni tanlang
   - Mapping'ni sozlang

3. **Mapping:**
   ```
   Facebook Field → Google Sheets Column
   full_name     → name
   phone_number  → phone
   ```

4. **Avtomatik sync:**
   - Facebook har lead kelganda Google Sheets'ga yozadi
   - CRM har 5 daqiqada Google Sheets'dan import qiladi

---

## 🎉 Tayyor!

Endi tizim to'liq avtomatik ishlaydi:

```
Instagram Ads → Google Sheets → CRM → Sotuvchilarga → Telegram
    ↓              ↓              ↓         ↓              ↓
  Lead      5 daqiqada    Import   Avtomatik   Notification
  keladi     tekshirish            taqsimlash
```

**Yangilash:** 17 Dekabr 2025  
**Versiya:** 1.0

---

## 📞 Yordam

Muammo yuzaga kelsa:
1. Log'larni tekshiring (Celery Worker va Beat)
2. Django admin'da Lead'larni tekshiring
3. Test qilish uchun Django shell'dan foydalaning
4. Cache'ni tozalang va qayta urinib ko'ring

**Qo'shimcha ma'lumot:** [README.md](README.md)


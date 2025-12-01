# O'quv Markazi CRM Tizimi

O'quv markazi sotuv bo'limi uchun to'liq avtomatlashtirilgan CRM tizimi.

## Texnologiyalar

- Backend: Django 4.2
- Database: SQLite3
- Background Tasks: Celery + Redis
- Frontend: HTML + TailwindCSS
- Telegram Bot: python-telegram-bot

## O'rnatish

1. Virtual environment yarating:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Kerakli paketlarni o'rnating:
```bash
pip install -r requirements.txt
```

3. Redis o'rnating va ishga tushiring (Celery uchun):
   - Windows: https://github.com/microsoftarchive/redis/releases
   - Linux: `sudo apt-get install redis-server`

4. .env fayl yarating (.env.example dan nusxa oling):
```
SECRET_KEY=your-secret-key
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-chat-id
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

5. Migratsiyalarni bajaring:
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Ishga tushirish:**

   **Windows:**
   - Terminal 1: `run_server.bat` (yoki `python manage.py runserver`)
   - Terminal 2: `run_celery_worker.bat` (yoki `celery -A crm_project worker --loglevel=info`)
   - Terminal 3: `run_celery_beat.bat` (yoki `celery -A crm_project beat --loglevel=info`)
   - Terminal 4: `run_telegram_bot.bat` (yoki `python manage.py run_telegram_bot`)

   **Linux/Mac:**
   ```bash
   # Terminal 1
   python manage.py runserver
   
   # Terminal 2
   celery -A crm_project worker --loglevel=info
   
   # Terminal 3
   celery -A crm_project beat --loglevel=info
   
   # Terminal 4
   python manage.py run_telegram_bot
   ```

## Foydalanish

1. Admin panel: http://localhost:8000/admin/
2. Dashboard: http://localhost:8000/dashboard/
3. Login: http://localhost:8000/login/

## Rollar

- **Admin**: To'liq boshqaruv
  - Sotuv managerlarini qo'shish/tahrirlash/o'chirish
  - Sotuvchilarni qo'shish/tahrirlash/o'chirish
  - Kurslar, guruhlar, xonalar boshqaruvi
  - Hisobotlar va analitika

- **Sales Manager**: Sotuvchilarni boshqarish
  - Sotuvchilarni qo'shish/tahrirlash/o'chirish
  - Lid taqsimlash strategiyasini sozlash
  - KPI va konversiya kuzatish
  - Sinov darslari va guruhlarni nazorat qilish

- **Sales**: Lidlar bilan ishlash
  - Lidlarni ko'rish (faqat o'ziga biriktirilgan)
  - Statuslarni o'zgartirish
  - Follow-up bajarish
  - Sinovga yozish
  - Guruhlarga joylashtirish

## Asosiy Funksiyalar

### 1. Lid Boshqaruvi
- Oddiy forma orqali lid qo'shish
- Excel import (duplicate checker bilan)
- Avtomatik lid taqsimlash (faol sotuvchilar orasida teng)
- Status pipeline (Yangi → Aloqa qilindi → ... → Kursga yozildi)

### 2. Follow-up Avtomatizatsiya
- Status o'zgarishi bilan avtomatik follow-up yaratish
- Overdue tracking (5+ overdue → yangi lidlar bloklanadi)
- Bugungi follow-ups paneli

### 3. Sinov Darslari
- Sinovga yozish (overbooking blokirovkasi bilan)
- Sinov natijalarini kiritish
- Avtomatik konversiya hisoblash

### 4. Guruh va Xona Boshqaruvi
- Xona bandlik jadvali (rangli ko'rsatish)
- Guruh sig'imi va bo'sh joylar
- Overbooking blokirovkasi

### 5. KPI Avtomatizatsiya
- Kunlik aloqa soni
- Follow-up bajarilganligi
- Sinovga yozilganlar
- Konversiya darajasi
- Response time
- Overdue statistikasi

### 6. Reaktivatsiya
- 7 kun → qayta taklif
- 14 kun → boshqa kurs tavsiyasi
- 30 kun → yangi guruhlar haqida xabar

### 7. Telegram Bot
- Yangi lid haqida xabar
- Follow-up eslatmalari
- Sinov oldi eslatma
- Overdue ogohlantirish
- Statistikalar va reyting

## Telegram Bot Buyruqlari

- `/start` - Botni ishga tushirish
- `/help` - Yordam
- `/stats` - Bugungi statistikalar
- `/followups` - Bugungi follow-ups
- `/overdue` - Overdue follow-ups
- `/rating` - Sotuvchilar reytingi

## Tizim Xususiyatlari

### Avtomatik Jarayonlar

1. **Lid kelganda:**
   - 5 daqiqada follow-up yaratiladi
   - Telegram xabar yuboriladi
   - Sotuvchiga avtomatik biriktiriladi

2. **Status o'zgarganda:**
   - Har bir status uchun mos follow-up yaratiladi
   - Vaqtlar: 24 soat, 48 soat, 2 soat, 3 daqiqa

3. **Sinov oldidan:**
   - 2 soat oldin eslatma yuboriladi

4. **Sinovdan keyin:**
   - 3 daqiqada sotuv taklifi follow-up yaratiladi

5. **Overdue:**
   - Har 15 daqiqada tekshiriladi
   - 5+ overdue → yangi lidlar bloklanadi
   - Manager/Admin ga xabar yuboriladi

6. **KPI:**
   - Har kuni kechasi avtomatik hisoblanadi

7. **Reaktivatsiya:**
   - Har kuni ertalab tekshiriladi
   - 7/14/30 kun reaktivatsiya takliflari

## Database Strukturasi

- **User**: Foydalanuvchilar (Admin, Sales Manager, Sales)
- **Lead**: Lidlar
- **Course**: Kurslar
- **Group**: Guruhlar
- **Room**: Xonalar
- **FollowUp**: Follow-up vazifalar
- **TrialLesson**: Sinov darslari
- **KPI**: KPI ma'lumotlari
- **Reactivation**: Reaktivatsiya tarixi

## Qo'shimcha Ma'lumot

Tizim to'liq avtomatlashtirilgan bo'lib, barcha jarayonlar lead kelganidan boshlab uni guruhga joylashtirib o'quvchiga aylantirishgacha bo'lgan bosqichlarni qamrab oladi.

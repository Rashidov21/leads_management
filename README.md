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

3. .env fayl yarating:
```
SECRET_KEY=your-secret-key
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-chat-id
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

4. Migratsiyalarni bajaring:
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Celery worker ishga tushiring:
```bash
celery -A crm_project worker --loglevel=info
```

6. Development server ishga tushiring:
```bash
python manage.py runserver
```

## Foydalanish

1. Admin panel: http://localhost:8000/admin/
2. Dashboard: http://localhost:8000/dashboard/
3. Login: http://localhost:8000/login/

## Rollar

- **Admin**: To'liq boshqaruv
- **Sales Manager**: Sotuvchilarni boshqarish, KPI kuzatish
- **Sales**: Lidlar bilan ishlash, follow-up bajarish


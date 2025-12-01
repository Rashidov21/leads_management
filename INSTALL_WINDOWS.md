# Windows uchun O'rnatish Yo'riqnomasi

## Pandas o'rnatish muammosi

Agar pandas o'rnatishda muammo bo'lsa, quyidagi yechimlardan birini tanlang:

### Variant 1: Pandas o'rnatmasdan (Tavsiya etiladi)

Tizim openpyxl bilan ham ishlaydi. Pandas o'rnatmasdan foydalanish mumkin:

```bash
pip install -r requirements.txt
```

Excel import funksiyasi openpyxl orqali ishlaydi.

### Variant 2: Pandas o'rnatish

Agar pandas kerak bo'lsa:

1. **Visual C++ Build Tools o'rnating:**
   - https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - "Desktop development with C++" ni tanlang

2. **Yoki pre-built wheel dan foydalaning:**
   ```bash
   pip install pandas --only-binary :all:
   ```

3. **Yoki conda orqali:**
   ```bash
   conda install pandas
   ```

### Variant 3: Python versiyasini tekshiring

Pandas Python 3.8+ ni talab qiladi. Python versiyangizni tekshiring:

```bash
python --version
```

Agar Python 3.7 yoki eskiroq bo'lsa, yangi versiyani o'rnating.

## Qolgan paketlarni o'rnatish

Agar pandas o'rnatishda muammo bo'lsa, uni o'tkazib yuborish mumkin:

```bash
pip install Django==4.2.7 celery==5.3.4 redis==5.0.1 python-telegram-bot==20.7 openpyxl gspread google-auth python-dotenv django-cors-headers Pillow
```

Tizim pandas o'rnatmasdan ham ishlaydi (openpyxl kifoya qiladi).

## Redis o'rnatish (Celery uchun)

Celery ishlashi uchun Redis server kerak. Windows'da Redis o'rnatish uchun quyidagi variantlardan birini tanlang:

### Variant 1: Memurai (Tavsiya etiladi - Windows uchun eng oson)

1. **Memurai'ni yuklab oling va o'rnating:**
   - https://www.memurai.com/get-memurai
   - Windows uchun bepul versiya mavjud

2. **O'rnatgandan keyin Memurai avtomatik ishga tushadi**

3. **Tekshirish:**
   ```powershell
   redis-cli ping
   ```
   Javob: `PONG` bo'lishi kerak

### Variant 2: WSL (Windows Subsystem for Linux)

1. **WSL o'rnating:**
   ```powershell
   wsl --install
   ```

2. **WSL ichida Redis o'rnating:**
   ```bash
   sudo apt-get update
   sudo apt-get install redis-server
   sudo service redis-server start
   ```

3. **Tekshirish:**
   ```bash
   redis-cli ping
   ```

### Variant 3: Docker (Agar Docker o'rnatilgan bo'lsa)

1. **Redis container'ni ishga tushiring:**
   ```powershell
   docker run -d -p 6379:6379 --name redis redis:latest
   ```

2. **Tekshirish:**
   ```powershell
   docker ps
   ```

### Variant 4: Redis Windows Port (Eski versiya)

1. **Redis Windows port'ni yuklab oling:**
   - https://github.com/microsoftarchive/redis/releases
   - `Redis-x64-3.0.504.zip` ni yuklab oling

2. **Zip faylni ochib, `redis-server.exe` ni ishga tushiring**

3. **Yoki Windows Service sifatida o'rnating**

## Redis ishga tushirishni tekshirish

Redis ishga tushirilgandan keyin, quyidagi buyruqni bajarib tekshiring:

```powershell
redis-cli ping
```

Agar `PONG` javobini olsangiz, Redis to'g'ri ishlayapti.

## Muammo hal qilish

### Xatolik: "Error 10061 connecting to localhost:6379"

Bu xatolik Redis server ishlamayotganini ko'rsatadi. Quyidagilarni tekshiring:

1. **Redis server ishga tushirilganmi?**
   - Memurai: Services panelida tekshiring
   - WSL: `sudo service redis-server status`
   - Docker: `docker ps` orqali tekshiring

2. **Port 6379 band emasmi?**
   ```powershell
   netstat -an | findstr 6379
   ```

3. **Firewall Redis'ga to'sqinlik qilmayaptimi?**

### Celery ishlamayapti

Agar Celery Redis'ga ulanayotganda xatolik bo'lsa:

1. Redis server ishga tushirilganligini tekshiring
2. `.env` faylda `CELERY_BROKER_URL` to'g'ri ekanligini tekshiring
3. Redis'ni qayta ishga tushiring

## Redis'siz ishlatish (Development uchun)

Agar faqat development uchun ishlatmoqchi bo'lsangiz va Celery'siz ishlatmoqchi bo'lsangiz, Celery worker va beat'ni ishga tushirmaslik mumkin. Lekin bu holda background task'lar ishlamaydi (follow-up avtomatizatsiya, KPI hisoblash va boshqalar).


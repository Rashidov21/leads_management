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


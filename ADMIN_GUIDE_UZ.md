# 👑 Admin Qisqa Qo'llanma

**Foydalanuvchi turi:** Admin  
**Huquqlar:** To'liq tizim nazorati

---

## 🚀 Tezkor Boshlash

### Asosiy Vazifalar

1. **Foydalanuvchilarni boshqarish** - Manager va sotuvchilar yaratish
2. **Tizim sozlamalari** - Kurslar, xonalar, guruhlar
3. **Monitoring** - Statistika va hisobotlar
4. **Takliflar yaratish** - Chegirma va bonuslar
5. **Ruxsatlarni boshqarish** - So'rovlarni tasdiqlash

---

## 👥 Foydalanuvchilar

### Manager Yaratish

```
Foydalanuvchilar → Managerlar → Yangi Manager
```

**Kerakli ma'lumotlar:**
- Username, parol
- Ism, familiya, email, telefon
- Telegram username

### Sotuvchi Yaratish

```
Foydalanuvchilar → Sotuvchilar → Yangi Sotuvchi
```

**Majburiy:**
- Username, parol
- Ish vaqtlari (boshlanish, tugash)
- Ish kunlari (checkbox)
- "Is active sales" ✅

**💡 Maslahat:** Ish vaqtlari to'g'ri bo'lishi muhim - follow-up'lar shu asosda hisoblanadi!

### Sotuvchini Ishda Emasligi Belgilash

```
Sotuvchilar → Absent tugmasi
```

- Boshlanish/tugash sanasi
- Sabab
- ✅ Yangi lidlar biriktirilmaydi
- ✅ Follow-up'lar keyinga o'tadi

---

## 📚 Kurslar

### Yangi Kurs

```
Tizim → Kurslar → Yangi Kurs
```

**Majburiy maydonlar:**
- Kurs nomi
- Narxi
- **Sotuv scripti** (sotuvchilar uchun)
- Dars davomiyligi
- Haftasiga darslar soni

**💡 Sotuv scripti namunasi:**
```
Assalomu alaykum! Men [Ism], [Kompaniya] dan.
- Kurs: IELTS Preparation
- Davomiyligi: 3 oy
- Dars soni: Haftada 3 marta (Dush/Chor/Juma)
- Har bir dars: 90 daqiqa
- Narxi: 1,200,000 so'm/oy
- BONUS: 
  ✅ Bepul Cambridge kitoblari
  ✅ Online platformaga kirish
  ✅ Mock test (2 marta)
```

---

## 🏢 Xonalar va Guruhlar

### Xona Qo'shish

```
Tizim → Xonalar → Yangi Xona
```

- Xona nomi (masalan: Xona 101)
- Sig'im (maksimal o'quvchilar)

### Guruh Yaratish

```
Tizim → Guruhlar → Yangi Guruh
```

**Kerakli:**
- Guruh nomi
- Kurs, xona
- Dars kunlari va vaqti
- Sig'im
- Faol ✅

---

## 🏷️ Takliflar

### Yangi Taklif Yaratish

```
Tizim → Takliflar → Yangi Taklif
```

**Majburiy:**
- Sarlavha (masalan: "Yangi Yil 20% Chegirma")
- Tavsif (batafsil)
- Taklif turi (chegirma/bonus/paket)
- Prioritet (urgent/high/normal/low)
- Kanal (follow-up/reactivation/trial/general)
- Auditoriya (new/lost/reactivation/trial/all)
- Amal qilish muddati
- Faol ✅

**Ko'rinadigan joylar:**
- Lead detail (accordion)
- Follow-up'lar sahifasida
- Overdue'lar sahifasida

---

## 📊 Lidlar Boshqaruvi

### Lidni Ko'rish

```
Lidlar → Filtrlar
```

**Filterlar:**
- Manba
- Status
- Sotuvchi
- Kurs
- Sana

### Lidni Biriktirish

```
Lid sahifasi → Biriktirish
```

- Sotuvchini tanlang
- ✅ Yangi follow-up yaratiladi
- ✅ Notification yuboriladi

---

## 💬 Xabarlar

### Xabar Yuborish

```
Xabarlar → Yangi Xabar
```

**Kerakli:**
- Mavzu
- Xabar matni
- Prioritet
- Qabul qiluvchilar (checkbox)

**Xabar boradi:**
- ✅ Tizim ichida (Inbox)
- ✅ Telegram bot orqali

### Xabar O'chirish

```
Xabarlar → O'chirish tugmasi
```

**Admin huquqi:** Istalgan xabarni o'chira olasiz

---

## ⚠️ Overdue Boshqaruvi

### Overdue'larni Ko'rish

```
Follow-up'lar → Overdue
```

**Filterlar:**
- Sotuvchi
- Kechikish vaqti (<1h, 1-6h, 6-24h, >24h)

### Bulk Actions

**1. Qayta Rejalashtirish**
- Checkbox bilan belgilang
- Necha soatdan keyin: 2
- "Qayta rejalashtirish"

**2. O'tkazish**
- Belgilang
- Yangi sotuvchini tanlang
- "O'tkazish"

**3. Bajarilgan deb belgilash**
- Belgilang
- "Bajarilgan deb belgilash"

**4. O'chirish (Faqat Admin!)** 🔥
- Belgilang
- "O'chirish"
- Tasdiqlang

---

## ✅ Ruxsat So'rovlari

### So'rovlarni Ko'rish

```
Ruxsatlar → Kutilmoqda
```

### Tasdiqlash/Rad Etish

**Tasdiqlash:**
- So'rovni oching
- "Tasdiqlash"
- ✅ Sotuvchiga xabar boradi
- ✅ Yangi lidlar biriktirilmaydi

**Rad Etish:**
- Sabab yozing
- "Rad etish"
- ✅ Sotuvchiga sabab bilan xabar boradi

---

## 📥 Import

### Excel Import

```
Lidlar → Excel Import
```

**Talab:**
- Header: name, phone, source, course
- Telefon noyob
- Format: .xlsx yoki .xls

**Natija:**
- ✅ Avtomatik taqsimlanadi
- ✅ Follow-up'lar yaratiladi

### Google Sheets Import

```
Lidlar → Google Sheets Import
```

**Sozlash:** `.env` faylida:
- GOOGLE_SHEETS_CREDENTIALS
- GOOGLE_SHEETS_SPREADSHEET_ID
- GOOGLE_SHEETS_WORKSHEET_NAME

---

## 📈 Statistika va Hisobotlar

### Analytics

```
Statistika → Analytics
```

**Ko'rinadigan:**
- Lidlar statistikasi
- Konversiya
- Sotuvchilar reytingi
- Grafik va diagrammalar

### Sotuvchi KPI

```
Statistika → Sotuvchi KPI
```

**Metrikalar:**
- Kunlik aloqalar
- Follow-up bajarilishi
- Sinovga yozilganlar
- Konversiya
- Overdue soni

---

## 🤖 Telegram Bot

### Sozlash

**`.env` faylida:**
```
TELEGRAM_BOT_TOKEN=your_bot_token
```

**Ishga tushirish:**
```bash
python manage.py run_telegram_bot
```

**Bot buyruqlari:**
- `/start` - Boshlash
- `/stats` - Statistika
- `/today` - Bugungi follow-up'lar
- `/overdue` - Overdue'lar

---

## ⚙️ Tizim Sozlamalari

### Asosiy Sozlamalar

**`settings.py`:**
- SECRET_KEY
- DATABASE sozlamalari
- TELEGRAM_BOT_TOKEN
- GOOGLE_SHEETS kredensiallar

### Celery (Background Tasks)

**Ishga tushirish:**
```bash
# Worker
celery -A crm_project worker -l info

# Beat (scheduler)
celery -A crm_project beat -l info
```

**Vazifalar:**
- Overdue tekshirish
- Reactivation
- KPI hisoblash
- Google Sheets avtomatik import

---

## 🛠️ Troubleshooting

### Muammo: Sotuvchi follow-up bajaray olmayapti
**Yechim:** Ish vaqtini tekshiring - faqat ish vaqtida bajarish mumkin

### Muammo: Google Sheets import ishlamayapti
**Yechim:** 
- `.env` fayl sozlamalarini tekshiring
- Kredensiallar to'g'riligini tekshiring
- Google Sheets'ga kirish huquqini tekshiring

### Muammo: Telegram bot xabar yubormayapti
**Yechim:**
- Bot token to'g'riligini tekshiring
- Bot ishlayotganligini tekshiring
- User'ning telegram_chat_id mavjudligini tekshiring

### Muammo: Lidlar avtomatik taqsimlanmayapti
**Yechim:**
- Faol sotuvchilar borligini tekshiring (is_active_sales=True)
- Sotuvchilar ish vaqtida ekanligini tekshiring
- Celery worker ishlayotganligini tekshiring

---

## 📋 Kunlik Vazifalar Checklist

- [ ] Yangi ruxsat so'rovlarini ko'rish va tasdiqlash
- [ ] Overdue statistikasini tekshirish
- [ ] Sotuvchilar KPI'sini kuzatish
- [ ] Tizim xatolarini tekshirish
- [ ] Backup olish (agar avtomatik bo'lmasa)

## 📋 Haftalik Vazifalar

- [ ] Sotuvchilar bilan 1-on-1 uchrashuvlar
- [ ] Yangi takliflar yaratish (kerak bo'lsa)
- [ ] Statistika tahlili
- [ ] Tizim sozlamalarini optimallash

---

## 🔐 Xavfsizlik

### Parollar
- Murakkab parollar
- 3 oyda bir marta o'zgartirish
- Hech kimga bermaslik

### Backup
- Kunlik avtomatik backup
- Mahalliy va cloud backup
- Tastiqlash (restore test)

### Kirish Huquqlari
- Faqat kerakli huquqlarni berish
- Ketgan xodimlarning huquqini o'chirish
- Kirish loglarini kuzatish

---

## 📞 Yordam

**Texnik Yordam:**
- Email: admin@yourcompany.com
- Telefon: +998 90 123 45 67

**Qo'llanmalar:**
- To'liq qo'llanma: USER_MANUAL_UZ.md
- Tezkor boshlash: QUICK_START_UZ.md

---

**Muvaffaqiyatli boshqaruv tilaymiz!** 🎉


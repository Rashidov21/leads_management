# 💼 Sotuvchi Qisqa Qo'llanma

**Foydalanuvchi turi:** Sotuvchi (Sales)  
**Huquqlar:** O'z lidlari bilan ishlash

---

## 🚀 Kunlik Ish Jarayoni

### 1. Tizimga Kirish

```
Login → Username va parol
```

### 2. Dashboard'ni Tekshirish

**Ko'riladigan:**
- 📋 Mening lidlarim (jami)
- 📞 Bugungi aloqalar (son)
- ⚠️ Muddati o'tgan (son)

**💡 Maslahat:** Har kuni ishni Dashboard'dan boshlang!

### 3. Bugungi Follow-up'larni Bajarish

```
Dashboard → "Qayta Aloqalar"
```

**Qadamlar:**
1. Follow-up ro'yxatini oching
2. Birinchi lidni oching
3. Mijozga qo'ng'iroq qiling
4. Gaplashganingizdan keyin "Bajarildi" tugmasini bosing
5. Keyingi lidga o'ting

**⚠️ Muhim:** Follow-up'ni faqat haqiqatan bajargandan keyin "Bajarildi" deb belgilang!

### 4. Overdue'larni Hal Qilish

```
Follow-up'lar → Overdue
```

**Prioritet:** Overdue'larni birinchi bo'lib bajaring!

**⚠️ Ogohlantirish:** 5+ overdue bo'lsa, yangi lidlar sizga biriktirilmaydi!

---

## 👤 Lid Bilan Ishlash

### Yangi Lid Qo'shish

```
Lidlar → Yangi Lid
```

**Majburiy:**
- Ism ✅
- Telefon ✅ (noyob)

**Ixtiyoriy:**
- Qo'shimcha telefon
- Manba
- Qiziqayotgan kurs
- Eslatmalar

**Natija:**
- ✅ Lid sizga avtomatik biriktiriladi
- ✅ 5 daqiqadan keyin follow-up yaratiladi
- ✅ Telegram'ga xabar keladi

### Lid Ma'lumotlarini Ko'rish

```
Lidlar → Lid nomiga bosing
```

**Ko'riladigan:**
- Ism, telefon, manba, status
- Qiziqayotgan kurs
- Follow-up'lar ro'yxati
- Sinov darslari
- **🏷️ Takliflar** (Accordion) ← Yangi!
- **📄 Sotuv Scripti** (Accordion) ← Yangi!

### Takliflar Accordion

**Qanday foydalanish:**
1. Lid sahifasida "Takliflar va Chegirmalar" ga bosing
2. Barcha faol takliflarni ko'ring
3. Mijoz bilan gaplashayotganda bu takliflarni taklif qiling

**💡 Maslahat:** Takliflar konversiyani oshiradi - albatta foydalaning!

### Sotuv Scripti Accordion

**Qanday foydalanish:**
1. Lid sahifasida "Sotuv Scripti" ga bosing
2. Kurs uchun sotuv scriptini ko'ring
3. Scriptdan foydalanib mijozga gaplashing

**💡 Maslahat:** Scriptni aynan o'qimang - mijozning ehtiyojiga moslang!

### Status O'zgartirish

```
Lid sahifasi → Status o'zgartirish
```

**Statuslar:**
- **Yangi** → Lid yangi kelgan
- **Aloqa qilindi** → Birinchi qo'ng'iroq
  - ✅ Avtomatik follow-up: 24 soat, 3 kun, 7 kun
- **Qiziqmoqda** → Mijoz qiziqmoqda
  - ✅ Avtomatik follow-up: 30 daqiqa, 2 kun, 5 kun
- **Sinovga yozildi** → Sinovga yozib qo'yildi
  - ✅ 1 kun oldin eslatma
- **Sinovga keldi** → Sinovda qatnashdi
  - ✅ 24 soat ichida sotuv taklifi
- **Sinovga kelmadi** → Sinovga kelmadi
  - ✅ 30 daqiqa, 24 soat, 3 kun follow-up'lar
- **Kursga yozildi** → Sotildi! 🎉
- **Yo'qotilgan lid** → Rad etdi

**⚠️ Muhim:** Har safar eslatma yozing - status nima uchun o'zgarganini!

---

## 📞 Follow-up'lar

### Bugungi Follow-up'lar

```
Follow-up'lar → Bugungi Aloqalar
```

**Ko'rinadigan:**
- Lid nomi va telefoni
- Follow-up vaqti
- Eslatmalar
- Lead status

**Bajarish:**
1. Mijozga qo'ng'iroq qiling
2. Kerakli ma'lumotlarni bering
3. Keyingi qadam to'g'risida kelishing
4. Sahifaga qayting va "Bajarildi" tugmasini bosing

### Overdue Follow-up'lar

```
Follow-up'lar → Muddati O'tgan
```

**⚠️ Jiddiy:** Overdue'larni darhol bajaring!

**5+ overdue natijasi:**
- ❌ Yangi lidlar biriktirilmaydi
- ❌ KPI pasayadi
- ❌ Manager bilan suhbat

---

## 🎓 Sinov Darslari

### Lidni Sinovga Yozish

```
Lid sahifasi → "Sinovga Yozish"
```

**Kerakli:**
- Guruh (ro'yxatdan tanlang)
- Sinov sanasi
- Sinov vaqti
- Eslatmalar

**Natija:**
- ✅ Lead status "Sinovga yozildi"
- ✅ 1 kun oldin eslatma follow-up
- ✅ Telegram'ga xabar

**💡 Maslahat:** Mijozga sinov sanasi va vaqtini SMS bilan ham yuboring!

### Sinov Natijasini Kiritish

```
Lid sahifasi → Sinov darslari → "Natija"
```

**Natijalar:**
- **Keldi** - Qatnashdi
- **Kelmadi** - Kelmadi
- **Qabul qilindi** - Kursga yozildi
- **Rad etdi** - Kursdan voz kechdi

---

## 📥 Import (Yangi!)

Endi siz ham lidlarni import qilishingiz mumkin!

### Excel Import

```
Lidlar → Excel Import
```

**Talab:**
- Header: name, phone, source, course
- Format: .xlsx yoki .xls

**Natija:**
- ✅ Lidlar sizga avtomatik biriktiriladi
- ✅ Follow-up'lar yaratiladi

### Google Sheets Import

```
Lidlar → Google Sheets Import → "Import"
```

**💡 Maslahat:** Import qilingan lidlaringizni darhol ko'rib chiqing!

---

## 📝 Ruxsat So'rash

### Ruxsat So'rovini Yuborish

```
Ruxsatlar → Ruxsat So'rash
```

**Kerakli:**
- Ruxsat turi (butun kun / soatlik)
- Sana (dan - gacha)
- Sabab
- Qo'shimcha sabab (matn)

**Natija:**
- ✅ So'rov manager'ga yuboriladi
- ✅ Javobni kutasiz
- ✅ Telegram'ga xabar keladi

---

## 💬 Kelgan Xabarlar

### Xabarlarni Ko'rish

```
Xabarlar → Kelgan Xabarlar
```

**Yangi xabarlar:**
- Ko'k border bilan
- "Yangi" belgisi

**💡 Maslahat:** Xabarlarni har kuni tekshiring - muhim ma'lumotlar bo'lishi mumkin!

---

## 📊 Mening KPI'm

### KPI Ko'rish

```
Statistika → Mening KPI'm
```

**Metrikalar:**
- **Kunlik aloqalar** - Har kuni qancha lid bilan aloqa
- **Follow-up bajarilishi** - Necha foiz bajarilgan (85%+ yaxshi)
- **Sinovga yozilganlar** - Qancha lid sinovga yozdingiz
- **Konversiya** - Necha foiz sotildi (15-25% yaxshi)
- **Overdue soni** - Qancha overdue'ingiz bor (0-3 yaxshi)

**💡 Maslahat:** Haftada bir marta KPI'ingizni tahlil qiling!

---

## 🤖 Telegram Bot

### Bot'ga Ulanish

1. Telegram'da `@your_crm_bot` ni qidiring
2. `/start` ni yuboring
3. Profilda Telegram username'ingizni to'g'ri kiriting

**Bot'dan Xabarlar:**
- 🆕 Yangi lid sizga biriktirildi
- 📞 Follow-up vaqti keldi
- ⚠️ Follow-up overdue bo'ldi
- 📨 Manager'dan yangi xabar
- ✅ Ruxsat tasdiqlandi

**Bot Buyruqlari:**
- `/stats` - Tezkor statistika
- `/today` - Bugungi follow-up'lar
- `/overdue` - Overdue'lar

---

## 💡 Sotish Bo'yicha Maslahatlar

### Birinchi Qo'ng'iroq

**Qilish kerak:**
- ✅ Ismini ayting va tanishing
- ✅ Qiziqishini so'rang
- ✅ Qisqa ma'lumot bering
- ✅ Sinov darsiga taklif qiling
- ✅ Keyingi qo'ng'iroq vaqtini kelishing

**Qilmaslik kerak:**
- ❌ Darhol narxni aytish
- ❌ Juda ko'p gapirish
- ❌ Bosim o'tkazish

### Takliflarni Taqdim Etish

**Qadamlar:**
1. Mijozning ehtiyojini tushunish
2. Kurs foydasini tushuntirish
3. Taklifni taqdim etish
4. E'tirozlarga javob berish
5. Yopish (closing)

**💡 Maslahat:** "Takliflar" accordion'dan foydalaning - bu sizga yordam beradi!

### E'tirozlarga Javob

**"Qimmat"**
→ "Men tushunaman. Lekin sifatli ta'lim - bu investitsiya. Bizda chegirmalar va to'lov planlari bor."

**"O'ylab ko'raman"**
→ "Albatta! Qaysi jihatlar to'g'risida ko'proq ma'lumot kerak?"

**"Vaqt yo'q"**
→ "Tushunaman. Bizda moslashuvchan jadvallar bor. Siz uchun qulay vaqtni topamiz."

### Yopish (Closing)

**Signallar:**
- Batafsil savol beradi
- Narx so'raydi
- Jadval so'raydi

**Qanday yopish:**
- "Keling, sizni bepul sinov darsiga yozib qo'yamiz?"
- "Qaysi guruh sizga qulay bo'ladi?"
- "To'lov bo'yicha qachon kelishsak bo'ladi?"

---

## ⚠️ Tez-tez Uchraydigan Xatolar

### Xato 1: Follow-up'ni vaqtida bajarmaslik

**Natija:** Overdue, KPI pasayadi, yangi lidlar biriktirilmaydi

**Yechim:** Follow-up'larni rejalashtiring, kalendarga qo'ying

### Xato 2: Eslatma yozmaslik

**Natija:** Keyingi gaplashuvda mijoz haqida hech narsa bilmaysiz

**Yechim:** Har bir aloqadan keyin eslatma yozing

### Xato 3: Status'ni o'zgartirmaslik

**Natija:** Follow-up'lar yaratilmaydi, statistika noto'g'ri

**Yechim:** Har safar gaplashganingizdan keyin status'ni yangilang

### Xato 4: Takliflar va scriptdan foydalanmaslik

**Natija:** Konversiya past

**Yechim:** Accordion'larni har safar oching va foydalaning

### Xato 5: Mijozga bosim o'tkazish

**Natija:** Mijoz qochadi

**Yechim:** Tabiiy va do'stona munosabat o'rnating

---

## 📋 Kunlik Checklist

**Ertalab (9:00-10:00):**
- [ ] Tizimga kirish
- [ ] Dashboard'ni tekshirish
- [ ] Bugungi follow-up'larni ko'rish
- [ ] Overdue'larni aniqlash

**Kun davomida:**
- [ ] Barcha follow-up'larni bajarish
- [ ] Lidlar bilan gaplashish
- [ ] Status'larni yangilash
- [ ] Eslatma yozish

**Kechqurun (17:00-18:00):**
- [ ] Bajarilmagan follow-up'larni tekshirish
- [ ] Ertangi reja tuzish
- [ ] Xabarlarni tekshirish

---

## 💪 Motivatsiya

### Maqsadlaringiz

**Kunlik:**
- 20-30 ta follow-up bajarish
- 5-10 ta yangi lid bilan aloqa
- 0 overdue

**Haftalik:**
- 3-5 ta sinovga yozish
- 1-2 ta sotish

**Oylik:**
- 15-20 ta sinovga yozish
- 8-12 ta sotish
- 20%+ konversiya

### Esda Tuting

- ✅ Har bir "yo'q" sizni "ha" ga yaqinlashtiradi
- ✅ Mijoz sizdan sotib olmaydi - muammoga yechim sotib oladi
- ✅ Eng yaxshi sotuvchi - eng ko'p e'tirozlarga javob bergan
- ✅ Muvaffaqiyat - bu kunlik kichik yutuqlar yig'indisi

**Omad tilaymiz!** 🎉

---

## 📞 Yordam

**Texnik Muammo:**
- Manager'ga murojaat qiling

**Qo'llanmalar:**
- To'liq qo'llanma: USER_MANUAL_UZ.md
- Tezkor boshlash: QUICK_START_UZ.md

**Telegram:**
- @support_bot

---

**Eng yaxshi sotuvchi bo'ling!** 🏆


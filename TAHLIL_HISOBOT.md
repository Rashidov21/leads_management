# Loyiha tahlili – Google Sheets import va yangilanishlar

**Sana:** 2026-02-06  
**Maqsad:** Bugun qo‘shilgan yangilanishlar va Google Sheets import zanjirining to‘g‘ri ishlashini tekshirish.

---

## 1. Google Sheets import – to‘liq zanjir

### 1.1 Trigger (qanday ishga tushadi)

| Trigger | Joy | Sozlash |
|--------|-----|--------|
| **Avtomatik (Celery Beat)** | `tasks.import_leads_from_google_sheets` | `settings.CELERY_BEAT_SCHEDULE`: har 5 daqiqada |
| **Qo‘lda (tugma)** | `views.google_sheets_manual_import` | Lidlar sahifasida "Google Sheets Import" |

Ikkalasi ham `GOOGLE_SHEETS_SPREADSHEET_ID` va `GOOGLE_SHEETS_WORKSHEETS` dan foydalanadi; bir xil `GoogleSheetsService.import_new_leads()` chaqiriladi. **To‘g‘ri.**

### 1.2 Worksheet’lar ro‘yxati

- **Settings:** `GOOGLE_SHEETS_WORKSHEETS` — `GOOGLE_SHEETS_WORKSHEETS` env (vergul bilan) yoki default `GOOGLE_SHEETS_WORKSHEET_NAME` (`Sheet1`).
- **Task** va **manual view** ikkalasi `worksheets` ni shu yerden oladi va har bir `worksheet_name` uchun `import_new_leads(spreadsheet_id, worksheet_name)` chaqiradi. **To‘g‘ri.**

### 1.3 Duplicate/bo‘sh sarlavha (Mobilografiya xatosi fix)

- **Muammo:** `get_all_records()` bo‘sh yoki takroriy ustunlar bo‘lsa xato berardi.
- **Yechim:** Ma’lumot `get_all_values()` orqali olinadi, birinchi qator sarlavha, bo‘sh/takroriy nomlar `_col0`, `name_2` kabi unikal qilinadi, record’lar `dict(zip(unique_headers, row_padded))` bilan yig‘iladi.
- **Kod:** `services.py` 1610–1635 atrofida. **To‘g‘ri**, barcha sheet’lar (jumladan Mobilografiya) uchun ishlashi kerak.

### 1.4 Ustunlar (name, phone, source, course)

- **Default:** `name`, `phone`, `source`, `course`, `secondary_phone`.
- **Phone:** `record.get(name_column, record.get(name_column.title(), ''))` — faqat `name` va `phone` (yoki ularning title varianti) qidiriladi. Agar sheet’da ustun boshqa nomda bo‘lsa (masalan `telefon_raqamingizni_yozib_qoldiring!`), u holda **per-sheet mapping** hozir yo‘q; bunday sheet uchun ustun nomi yoki mapping qo‘shish kerak.
- **Source:** `source_mapping.get(source_value, 'instagram')` — ustun bo‘sh/yo‘q bo‘lsa default **instagram**. **To‘g‘ri** (talab bo‘yicha).
- **Course:** Avval sheet nomidan (`GOOGLE_SHEETS_SHEET_COURSE_MAPPING`), keyin record’dagi `course`/`kurs` va h.k. ustunlardan. **To‘g‘ri.**

### 1.5 Sheet → kurs mapping

- **Settings:** `GOOGLE_SHEETS_SHEET_COURSE_MAPPING = {'Sheet1': 'Computer Science', 'Sheet2': 'Mobilografiya'}`.
- **Import:** `sheet_course_name = sheet_to_course_mapping.get(worksheet_name)`, keyin `Course.objects.filter(name__icontains=sheet_course_name).first()`. DB’da **Computer Science** va **Mobilografiya** nomli (yoki shu so‘zni o‘z ichiga oladigan) kurslar bo‘lishi kerak.
- **Eslatma:** Agar Sheet3 yoki boshqa worksheet ishlatilsa, mapping’ga qo‘shish kerak (masalan `'Sheet3': 'Boshqa kurs'`).

### 1.6 Notes va taqsimlash

- **Notes:** Har bir lid uchun `notes` ga quyidagilar yoziladi:
  - `"Google Sheets'dan avtomatik import\n"`
  - `"Sheet: {worksheet_name}\n"`  ← **Taqsimlash uchun muhim**
  - `"Qator: ..."`, kurs, manba.
- **Taqsimlash:** `LeadDistributionService.distribute_leads(leads_to_import)`:
  - `_extract_sheet_name_from_notes(lead.notes)` — regex `Sheet:\s*([^\n]+)` bilan sheet nomi olinadi. **Format mos.**
  - `_get_course_from_sheet_name(sheet_name)` — settings’dagi mapping va `Course.objects.filter(name__icontains=...)`. **To‘g‘ri.**
  - Kurs topilsa: avvalo shu kursga `assigned_courses` da biriktirilgan sotuvchilar, ular orasida eng kam lidli; kursga hech kim biriktirilmagan bo‘lsa — barcha faol sotuvchilar orasida eng kam lidli.
  - Kurs topilmasa: faqat eng kam lidli sotuvchi.
- Lid saqlanadi: `lead.assigned_sales = assigned_sales`, agar sheet’dan kurs topilsa va `interested_course` bo‘sh bo‘lsa `lead.interested_course = course_from_sheet`, keyin `lead.save()`. **To‘g‘ri.**

### 1.7 Cache (yangi qatorlar)

- **Key:** `google_sheets_last_row_{spreadsheet_id}_{worksheet_name}`.
- **Qiymat:** Import qilingan data qatorlari soni (sarlavhasiz). Keyingi chaqiruvda `new_records = all_records[last_imported_row:]`. **To‘g‘ri.**

### 1.8 Xulosa – Google Sheets import

| Qism | Holat | Izoh |
|------|--------|------|
| Trigger (Celery + manual) | ✅ | Bir xil service, multi-sheet |
| Duplicate/bo‘sh header | ✅ | get_all_values + unikal sarlavha |
| Source = instagram (default) | ✅ | |
| Course = sheet nomi (mapping) | ✅ | Sheet1→CS, Sheet2→Mobilografiya |
| Notes’da "Sheet: …" | ✅ | Taqsimlash uchun ishlatiladi |
| Taqsimlash (assigned_courses) | ✅ | Kurs bo‘yicha, keyin eng kam lidli |
| Cache yangi qatorlar | ✅ | |

**Mumkin bo‘lgan kamchilik:** Agar worksheet’da `name` yoki `phone` ustuni boshqa nomda bo‘lsa (masalan faqat `telefon_raqamingizni_yozib_qoldiring!`), lid skip bo‘ladi. Bunday sheet uchun ustun nomini o‘zgartirish yoki kelajakda per-worksheet column mapping qo‘shish kerak.

---

## 2. Bugun qo‘shilgan boshqa yangilanishlar

### 2.1 Kunlik KPI hisobot (Telegram)

- **Servis:** `KPIService.get_daily_report_stats(sales, date)` va `KPIService.build_daily_report_message(date)`.
- **Task:** `send_daily_sales_summary_task` — xabar `build_daily_report_message(today)` orqali yig‘iladi, avval `TELEGRAM_ADMIN_CHAT_ID`, keyin admin/manager `telegram_group_id` larga yuboriladi.
- **Ko‘rsatkichlar:** Lid qabul, task belgilandi, FU bajarildi/reja, aloqa, trial, sotuv, overdue, yangi aloqa qilinmagan, overdue 24+, status bo‘yicha pipeline. **Mantiq to‘g‘ri.**

### 2.2 Analitika – Excel export va Telegramga yuborish

- **Excel:** `export_analytics_excel` — mavjud, analitika sahifasida tugma.
- **Telegram:** `send_kpi_report_telegram` — `KPIService.build_daily_report_message()` ni chaqib, `TELEGRAM_ADMIN_CHAT_ID` ga yuboradi. **To‘g‘ri.**

### 2.3 Sotuvchi KPI’sini admin/manager ko‘rishi

- **URL:** `analytics/my-kpi/` (o‘z KPI) va `analytics/my-kpi/<sales_id>/` (berilgan sotuvchi).
- **View:** `sales_kpi(request, sales_id=None)` — sales faqat o‘zi, admin/manager `sales_id` orqali istalgan sotuvchi. **To‘g‘ri.**
- **Analitika jadvali:** Admin/manager uchun "KPI" ustuni va har bir sotuvchi qatorida `sales_kpi_sales` havolasi. **To‘g‘ri.**

---

## 3. Tekshirish ro‘yxati (siz qilishingiz mumkin)

1. **.env**
   - `GOOGLE_SHEETS_CREDENTIALS` (JSON yoki fayl yo‘li)
   - `GOOGLE_SHEETS_SPREADSHEET_ID`
   - `GOOGLE_SHEETS_WORKSHEETS=Sheet1,Sheet2` (yoki boshqa sheet nomlari)
   - `TELEGRAM_ADMIN_CHAT_ID` (kunlik/Telegram hisobot uchun)

2. **DB**
   - `Course` jadvalida "Computer Science" va "Mobilografiya" (yoki `name__icontains` topadigan nomlar) mavjud.
   - Sotuvchilarga `assigned_courses` to‘g‘ri biriktirilgan (kurs bo‘yicha taqsimlash ishlashi uchun).

3. **Google Sheet**
   - Birinchi qatorda ustunlar: `name`, `phone` (yoki ularni map qiladigan ustunlar).
   - Sheet nomlari: `Sheet1`, `Sheet2` (yoki `GOOGLE_SHEETS_WORKSHEETS` dagi nomlar).
   - Service account email sheet’ga share qilingan.

4. **Celery (avtomatik import uchun)**
   - Worker va Beat ishlayapti.
   - `import_leads_from_google_sheets` har 5 daqiqada ishga tushadi.

5. **Qo‘lda test**
   - Lidlar sahifasida "Google Sheets Import" → xabar va yangi lidlar.
   - Analitika → "Telegramga yuborish" → admin Telegram’da hisobot.

---

## 4. Xulosa

- **Google Sheets import** zanjiri (multi-sheet, duplicate header fix, source=instagram, course=sheet mapping, taqsimlash) **loyiha kodi bo‘yicha to‘g‘ri** yozilgan.
- **Yangi KPI hisobot, analitika tugmalari, sotuvchi KPI’sini admin/manager ko‘rishi** ham **to‘g‘ri** ulangan.
- Amalda ishlashi **.env, DB kurslari, sotuvchi–kurs biriktirish, Google Sheet format va Celery** ga bog‘liq. Yuqoridagi tekshirish ro‘yxatini bajarsangiz, yangi Google Sheets import’lar to‘g‘ri ishlashi kerak.

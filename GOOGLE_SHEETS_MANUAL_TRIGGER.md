# Google Sheets Manual Import Trigger

**Sana:** 17 Dekabr 2025  
**Versiya:** 1.2.0  
**Xususiyat:** Qo'lda Google Sheets import qilish tugmasi

---

## 🎯 Xususiyat

Admin va Sales Manager'lar endi **bir tugma bosish** bilan Google Sheets'dan yangi lidlarni import qilishlari mumkin!

---

## 🚀 Qanday Ishlaydi?

### **1. Tugma Joylashuvi**

Lidlar sahifasida (`/leads/`) **"Google Sheets Import"** yashil tugmasi mavjud:

```
[Yangi Lid] [Excel Import] [Google Sheets Import] [Lidlar ro'yxati] [To'liq Ekran]
```

- 🟢 **Yashil gradient button** (Green 600-700)
- 🔄 **Sync icon** (`fa-sync-alt`)
- 👥 **Admin va Sales Manager** uchun

### **2. Import Jarayoni**

Tugma bosilganda:

1. ✅ Google Sheets'ga ulanadi
2. ✅ Oxirgi import qilingan qatordan keyingi **yangi qatorlarni** topadi
3. ✅ Duplicate'larni tekshiradi (telefon bo'yicha)
4. ✅ Yangi lidlarni import qiladi
5. ✅ Avtomatik **taqsimlaydi** (LeadDistributionService)
6. ✅ **Telegram notification** yuboradi
7. ✅ Cache'ni yangilaydi (keyingi import uchun)

### **3. Avtomatik Import bilan Bog'liqligi**

- ✅ **Bir xil logika** ishlatiladi (`GoogleSheetsService.import_new_leads()`)
- ✅ **Cache** ishlatiladi - qaysi qator import qilingani saqlanadi
- ✅ **Duplicate** import bo'lmaydi
- ✅ **Avtomatik import** (Celery, har 5 min) ham davom etadi

---

## 📋 Ishlatish

### **Web Interface:**

1. Lidlar sahifasiga o'ting: `/leads/`
2. **"Google Sheets Import"** yashil tugmasini bosing
3. Kutib turing (1-2 soniya)
4. Natijani ko'ring:
   - ✅ "3 ta yangi lid muvaffaqiyatli import qilindi!"
   - ℹ️ "Yangi lid topilmadi"
   - ⚠️ Xatolar (agar bo'lsa)

---

## 🎨 Dizayn

### **Button Stillar:**
```html
- Rang: Green gradient (600-700)
- Icon: fa-sync-alt (sync/refresh)
- Hover: Shadow + darker green
- Active: Scale animation (0.98)
- Title: Tooltip ko'rsatadi
```

### **Messages:**
```python
✅ Success: "N ta yangi lid muvaffaqiyatli import qilindi!"
ℹ️ Info: "Yangi lid topilmadi"
⚠️ Warning: Xatolar (birinchi 3 ta)
❌ Error: "Xatolik yuz berdi: ..."
```

---

## 🔄 Avtomatik vs Qo'lda Import

| Xususiyat | Avtomatik Import | Qo'lda Import |
|-----------|------------------|---------------|
| **Trigger** | Celery Beat (5 min) | Tugma bosish |
| **Logika** | `import_new_leads()` | `import_new_leads()` |
| **Cache** | Ishlatadi | Ishlatadi |
| **Duplicate** | Skip qiladi | Skip qiladi |
| **Taqsimlash** | Avtomatik | Avtomatik |
| **Notification** | Telegram | Telegram |
| **User** | - | Admin/Sales Manager |

**⚡ Ikkalasi ham bir xil kodni ishlatadi va bir-birini to'ldiradi!**

---

## 🔧 Texnik Tafsilotlar

### **1. Qo'shilgan Kod:**

#### ✅ `crm_app/views.py`
```python
@login_required
@role_required('admin', 'sales_manager')
def google_sheets_manual_import(request):
    """Qo'lda yangi lidlarni import qilish"""
    # GoogleSheetsService.import_new_leads() ni chaqiradi
    # Natijalarni messages orqali ko'rsatadi
    # leads_list ga redirect qiladi
```

#### ✅ `crm_app/urls.py`
```python
path('leads/import/google-sheets/', 
     views.google_sheets_manual_import, 
     name='google_sheets_manual_import'),
```

#### ✅ `templates/leads/list.html`
```html
<a href="{% url 'google_sheets_manual_import' %}" 
   class="... bg-gradient-to-r from-green-600 ...">
    <i class="fas fa-sync-alt"></i>Google Sheets Import
</a>
```

---

## 📊 Natija Ko'rinishi

### **Scenario 1: Yangi Lidlar Bor**
```
✅ 5 ta yangi lid muvaffaqiyatli import qilindi!
```
*Lidlar avtomatik taqsimlanadi va Telegram'ga xabar yuboriladi*

### **Scenario 2: Yangi Lid Yo'q**
```
ℹ️ Yangi lid topilmadi. 2 ta lid allaqachon mavjud.
```
*Hech narsa import qilinmaydi*

### **Scenario 3: Xatoliklar Bor**
```
✅ 3 ta yangi lid muvaffaqiyatli import qilindi!
⚠️ Qator 10: Telefon formati noto'g'ri
⚠️ Qator 12: Ism bo'sh
```
*Xatolar bilan birga muvaffaqiyatli import ham bo'ladi*

### **Scenario 4: Umumiy Xatolik**
```
❌ Xatolik yuz berdi: GOOGLE_SHEETS_SPREADSHEET_ID sozlanmagan
```
*Import qilinmaydi, sozlash kerak*

---

## ⚙️ Sozlash

### **1. .env fayl:**
```env
GOOGLE_SHEETS_CREDENTIALS={"type": "service_account", ...}
GOOGLE_SHEETS_SPREADSHEET_ID=1abc...xyz
GOOGLE_SHEETS_WORKSHEET_NAME=Sheet1
```

### **2. Google Sheets Format:**
| name | phone | source | course | secondary_phone |
|------|-------|--------|--------|-----------------|
| Ali Valiyev | 998901234567 | instagram | Python | - |
| Vali Aliyev | 998902222222 | telegram | Frontend | - |

---

## 🔐 Xavfsizlik

- ✅ `@login_required` - Login talab qilinadi
- ✅ `@role_required('admin', 'sales_manager')` - Faqat adminlar va menejerlar
- ✅ CSRF protection - Django avtomatik qo'shadi
- ✅ Error handling - Try-except bilan himoyalangan

---

## 🐛 Troubleshooting

### **"Google Sheets ID sozlanmagan!"**
**Sabab:** `.env` faylda `GOOGLE_SHEETS_SPREADSHEET_ID` yo'q  
**Yechim:** `.env` ga qo'shing va serverni restart qiling

### **"Yangi lid topilmadi"**
**Sabab:** Barcha lidlar allaqachon import qilingan  
**Normal:** Bu xato emas, cache ishlayapti

### **"Xatolik: Permission denied"**
**Sabab:** Service Account'da Sheet'ga kirish huquqi yo'q  
**Yechim:** Google Sheet'ni Service Account email'iga share qiling

---

## ✅ Test Qilish

1. Lidlar sahifasiga o'ting: `/leads/`
2. **"Google Sheets Import"** tugmasini bosing
3. Natijani kutib turing (1-2 soniya)
4. Success message'ni ko'ring
5. Lidlar ro'yxatida yangi lidlarni tekshiring

---

## 🎉 Foydalar

1. **⚡ Tez:** Bir tugma bosish bilan
2. **🔄 Sync:** Avtomatik import kutmasdan
3. **👥 User-Friendly:** Sodda interface
4. **✅ Xavfsiz:** Role-based access
5. **🤝 Uyg'unlashadi:** Avtomatik import bilan birga ishlaydi

---

## 📝 Qo'shimcha Ma'lumot

- Avtomatik import: `crm_app/tasks.py` → `import_leads_from_google_sheets()`
- Service: `crm_app/services.py` → `GoogleSheetsService`
- Setup: `GOOGLE_SHEETS_SETUP.md`
- Changelog: `CHANGELOG_GOOGLE_SHEETS.md`

---

**✨ Tayyor! Google Sheets'dan bir bosish bilan yangi lidlarni import qiling!**


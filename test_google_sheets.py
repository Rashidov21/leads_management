#!/usr/bin/env python
"""
Google Sheets Integration Test Script

Bu script Google Sheets integratsiyasini test qilish uchun ishlatiladi.

Ishlatish:
    python test_google_sheets.py
"""

import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
django.setup()

from django.conf import settings
from crm_app.services import GoogleSheetsService


def test_credentials():
    """Credentials mavjudligini tekshirish"""
    print("=" * 50)
    print("1. CREDENTIALS TEKSHIRISH")
    print("=" * 50)
    
    if not settings.GOOGLE_SHEETS_CREDENTIALS:
        print("❌ GOOGLE_SHEETS_CREDENTIALS sozlanmagan!")
        print("   .env faylga quyidagini qo'shing:")
        print("   GOOGLE_SHEETS_CREDENTIALS=google_credentials.json")
        return False
    
    print("✅ GOOGLE_SHEETS_CREDENTIALS topildi")
    return True


def test_spreadsheet_id():
    """Spreadsheet ID mavjudligini tekshirish"""
    print("\n" + "=" * 50)
    print("2. SPREADSHEET ID TEKSHIRISH")
    print("=" * 50)
    
    if not settings.GOOGLE_SHEETS_SPREADSHEET_ID:
        print("❌ GOOGLE_SHEETS_SPREADSHEET_ID sozlanmagan!")
        print("   .env faylga quyidagini qo'shing:")
        print("   GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id")
        return False
    
    print(f"✅ GOOGLE_SHEETS_SPREADSHEET_ID: {settings.GOOGLE_SHEETS_SPREADSHEET_ID}")
    return True


def test_connection():
    """Google Sheets'ga ulanishni test qilish"""
    print("\n" + "=" * 50)
    print("3. ULANISH TESTI")
    print("=" * 50)
    
    try:
        result = GoogleSheetsService.test_connection(
            settings.GOOGLE_SHEETS_SPREADSHEET_ID,
            settings.GOOGLE_SHEETS_WORKSHEET_NAME
        )
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"   Qatorlar: {result['row_count']}")
            print(f"   Ustunlar: {result['col_count']}")
            return True
        else:
            print(f"❌ {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False


def test_import():
    """Lid import'ni test qilish"""
    print("\n" + "=" * 50)
    print("4. IMPORT TESTI")
    print("=" * 50)
    
    try:
        print("Import boshlanmoqda...")
        result = GoogleSheetsService.import_new_leads(
            settings.GOOGLE_SHEETS_SPREADSHEET_ID,
            settings.GOOGLE_SHEETS_WORKSHEET_NAME
        )
        
        print(f"\n📊 NATIJALAR:")
        print(f"   ✅ Import qilindi: {result['imported']} ta")
        print(f"   ⏭  O'tkazib yuborildi: {result['skipped']} ta")
        
        if result['errors']:
            print(f"   ❌ Xatoliklar: {len(result['errors'])} ta")
            for error in result['errors']:
                print(f"      - {error}")
        
        if result['leads']:
            print(f"\n   Lead ID'lar: {result['leads']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Asosiy test funksiyasi"""
    print("\n" + "=" * 50)
    print("GOOGLE SHEETS INTEGRATION TEST")
    print("=" * 50)
    print()
    
    # Test 1: Credentials
    if not test_credentials():
        return
    
    # Test 2: Spreadsheet ID
    if not test_spreadsheet_id():
        return
    
    # Test 3: Connection
    if not test_connection():
        print("\n⚠️  Ulanish muvaffaqiyatsiz. Quyidagilarni tekshiring:")
        print("   1. Service Account JSON fayli to'g'rimi?")
        print("   2. Google Sheets'ga Service Account share qilinganmi?")
        print("   3. Spreadsheet ID to'g'rimi?")
        return
    
    # Test 4: Import
    print("\n⚠️  Import test qilishni xohlaysizmi? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice == 'y':
        test_import()
    else:
        print("Import test qilinmadi.")
    
    print("\n" + "=" * 50)
    print("TEST YAKUNLANDI")
    print("=" * 50)
    print()
    
    print("📋 Keyingi qadamlar:")
    print("   1. Celery Worker'ni ishga tushiring: run_celery_worker.bat")
    print("   2. Celery Beat'ni ishga tushiring: run_celery_beat.bat")
    print("   3. Google Sheets'ga yangi lid qo'shing")
    print("   4. 5 daqiqa kuting (yoki log'larni kuzating)")
    print()
    print("📖 To'liq qo'llanma: GOOGLE_SHEETS_SETUP.md")
    print()


if __name__ == '__main__':
    main()


"""
Telegram Bot Handler (Sync Version)
Bu fayl Telegram botni ishga tushirish uchun alohida script sifatida ishlatiladi
python-telegram-bot 13.x (sync) versiyasi ishlatiladi
"""
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
django.setup()

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from django.utils import timezone
from datetime import date
from .models import Lead, FollowUp, User, KPI
from .services import FollowUpService, KPIService


def start(update: Update, context: CallbackContext):
    """Botni ishga tushirish"""
    update.message.reply_text(
        "Assalomu alaykum! CRM tizimi botiga xush kelibsiz.\n\n"
        "Foydalanish uchun /help buyrug'ini bosing."
    )


def help_command(update: Update, context: CallbackContext):
    """Yordam"""
    update.message.reply_text(
        "Mavjud buyruqlar:\n"
        "/stats - Bugungi statistikalar\n"
        "/followups - Bugungi follow-uplar\n"
        "/overdue - Overdue follow-uplar\n"
        "/rating - Sotuvchilar reytingi"
    )


def stats(update: Update, context: CallbackContext):
    """Bugungi statistikalar"""
    today = timezone.now().date()
    
    stats_text = f"📊 Bugungi Statistikalar ({today})\n\n"
    stats_text += f"Yangi lidlar: {Lead.objects.filter(created_at__date=today).count()}\n"
    stats_text += f"Jami follow-ups: {FollowUpService.get_today_followups().count()}\n"
    stats_text += f"Overdue: {FollowUpService.get_overdue_followups().count()}\n"
    
    update.message.reply_text(stats_text)


def followups(update: Update, context: CallbackContext):
    """Bugungi follow-uplar"""
    followups = FollowUpService.get_today_followups()
    
    if not followups.exists():
        update.message.reply_text("Bugungi follow-up yo'q")
        return
    
    text = "📋 Bugungi Follow-ups:\n\n"
    for followup in followups[:10]:  # Faqat birinchi 10 tasi
        text += f"• {followup.lead.name} - {followup.due_date.strftime('%H:%M')}\n"
    
    if followups.count() > 10:
        text += f"\n... va yana {followups.count() - 10} ta"
    
    update.message.reply_text(text)


def overdue(update: Update, context: CallbackContext):
    """Overdue follow-uplar"""
    overdue_followups = FollowUpService.get_overdue_followups()
    
    if not overdue_followups.exists():
        update.message.reply_text("Overdue follow-up yo'q ✅")
        return
    
    text = "⚠️ Overdue Follow-ups:\n\n"
    for followup in overdue_followups[:10]:
        text += f"• {followup.lead.name} ({followup.sales.username})\n"
        text += f"  Vaqt: {followup.due_date.strftime('%d.%m.%Y %H:%M')}\n\n"
    
    update.message.reply_text(text)


def rating(update: Update, context: CallbackContext):
    """Sotuvchilar reytingi"""
    today = timezone.now().date()
    sales_users = User.objects.filter(role='sales', is_active_sales=True)
    
    ratings = []
    for sales in sales_users:
        try:
            kpi = KPIService.calculate_daily_kpi(sales, today)
            overdue_count = FollowUpService.get_overdue_followups(sales).count()
            ratings.append({
                'sales': sales,
                'kpi': kpi,
                'overdue': overdue_count,
            })
        except Exception as e:
            print(f"KPI hisoblashda xatolik ({sales.username}): {e}")
            continue
    
    # Konversiya bo'yicha tartiblash
    ratings.sort(key=lambda x: x['kpi'].conversion_rate, reverse=True)
    
    text = "🏆 Sotuvchilar Reytingi:\n\n"
    for i, rating in enumerate(ratings[:10], 1):
        text += f"{i}. {rating['sales'].username}\n"
        text += f"   Konversiya: {rating['kpi'].conversion_rate:.1f}%\n"
        text += f"   Sotuv: {rating['kpi'].trials_to_sales}\n"
        text += f"   Overdue: {rating['overdue']}\n\n"
    
    if not ratings:
        text = "Sotuvchilar topilmadi yoki ma'lumotlar yo'q"
    
    update.message.reply_text(text)


def error_handler(update: Update, context: CallbackContext):
    """Xatoliklarni qayta ishlash"""
    print(f"Update {update} caused error {context.error}")
    if update and update.message:
        update.message.reply_text(
            "Xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring."
        )


def run_bot():
    """Botni ishga tushirish (sync)"""
    if not settings.TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN sozlanmagan!")
        return
    
    try:
        # Updater yaratish (sync)
        updater = Updater(token=settings.TELEGRAM_BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # Command handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("stats", stats))
        dispatcher.add_handler(CommandHandler("followups", followups))
        dispatcher.add_handler(CommandHandler("overdue", overdue))
        dispatcher.add_handler(CommandHandler("rating", rating))
        
        # Error handler
        dispatcher.add_error_handler(error_handler)
        
        # Botni ishga tushirish
        print("Telegram bot ishga tushdi (sync mode)...")
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        print(f"Bot ishga tushirishda xatolik: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_bot()

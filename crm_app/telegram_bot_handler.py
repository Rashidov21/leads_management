"""
Telegram Bot Handler
Bu fayl Telegram botni ishga tushirish uchun alohida script sifatida ishlatiladi
"""
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
django.setup()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from django.utils import timezone
from datetime import date
from .models import Lead, FollowUp, User, KPI
from .services import FollowUpService, KPIService
from .telegram_bot import send_telegram_notification


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botni ishga tushirish"""
    await update.message.reply_text(
        "Assalomu alaykum! CRM tizimi botiga xush kelibsiz.\n\n"
        "Foydalanish uchun /help buyrug'ini bosing."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam"""
    await update.message.reply_text(
        "Mavjud buyruqlar:\n"
        "/stats - Bugungi statistikalar\n"
        "/followups - Bugungi follow-uplar\n"
        "/overdue - Overdue follow-uplar\n"
        "/rating - Sotuvchilar reytingi"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bugungi statistikalar"""
    today = timezone.now().date()
    
    stats_text = f"📊 Bugungi Statistikalar ({today})\n\n"
    stats_text += f"Yangi lidlar: {Lead.objects.filter(created_at__date=today).count()}\n"
    stats_text += f"Jami follow-ups: {FollowUpService.get_today_followups().count()}\n"
    stats_text += f"Overdue: {FollowUpService.get_overdue_followups().count()}\n"
    
    await update.message.reply_text(stats_text)


async def followups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bugungi follow-uplar"""
    followups = FollowUpService.get_today_followups()
    
    if not followups.exists():
        await update.message.reply_text("Bugungi follow-up yo'q")
        return
    
    text = "📋 Bugungi Follow-ups:\n\n"
    for followup in followups[:10]:  # Faqat birinchi 10 tasi
        text += f"• {followup.lead.name} - {followup.due_date.strftime('%H:%M')}\n"
    
    if followups.count() > 10:
        text += f"\n... va yana {followups.count() - 10} ta"
    
    await update.message.reply_text(text)


async def overdue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Overdue follow-uplar"""
    overdue_followups = FollowUpService.get_overdue_followups()
    
    if not overdue_followups.exists():
        await update.message.reply_text("Overdue follow-up yo'q ✅")
        return
    
    text = "⚠️ Overdue Follow-ups:\n\n"
    for followup in overdue_followups[:10]:
        text += f"• {followup.lead.name} ({followup.sales.username})\n"
        text += f"  Vaqt: {followup.due_date.strftime('%d.%m.%Y %H:%M')}\n\n"
    
    await update.message.reply_text(text)


async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sotuvchilar reytingi"""
    today = timezone.now().date()
    sales_users = User.objects.filter(role='sales', is_active_sales=True)
    
    ratings = []
    for sales in sales_users:
        kpi = KPIService.calculate_daily_kpi(sales, today)
        overdue_count = FollowUpService.get_overdue_followups(sales).count()
        ratings.append({
            'sales': sales,
            'kpi': kpi,
            'overdue': overdue_count,
        })
    
    # Konversiya bo'yicha tartiblash
    ratings.sort(key=lambda x: x['kpi'].conversion_rate, reverse=True)
    
    text = "🏆 Sotuvchilar Reytingi:\n\n"
    for i, rating in enumerate(ratings[:10], 1):
        text += f"{i}. {rating['sales'].username}\n"
        text += f"   Konversiya: {rating['kpi'].conversion_rate:.1f}%\n"
        text += f"   Sotuv: {rating['kpi'].trials_to_sales}\n"
        text += f"   Overdue: {rating['overdue']}\n\n"
    
    await update.message.reply_text(text)


def run_bot():
    """Botni ishga tushirish"""
    if not settings.TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN sozlanmagan!")
        return
    
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("followups", followups))
    application.add_handler(CommandHandler("overdue", overdue))
    application.add_handler(CommandHandler("rating", rating))
    
    print("Telegram bot ishga tushdi...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    run_bot()


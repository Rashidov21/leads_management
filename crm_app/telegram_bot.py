import os
from django.conf import settings
from telegram import Bot
from telegram.error import TelegramError


def send_telegram_notification(chat_id, message):
    """Telegram xabar yuborish (sync)"""
    if not settings.TELEGRAM_BOT_TOKEN:
        return False
    
    try:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=chat_id, text=message)
        return True
    except TelegramError as e:
        print(f"Telegram xabar yuborishda xatolik: {e}")
        return False
    except Exception as e:
        print(f"Telegram xabar yuborishda umumiy xatolik: {e}")
        return False


def send_to_admin(message):
    """Admin ga xabar yuborish"""
    if settings.TELEGRAM_ADMIN_CHAT_ID:
        return send_telegram_notification(settings.TELEGRAM_ADMIN_CHAT_ID, message)
    return False

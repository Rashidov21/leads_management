import os
from django.conf import settings

# Telegram import'ni lazy qilish - faqat kerak bo'lganda import qilish
def _get_telegram_bot():
    """Telegram bot'ni lazy import qilish"""
    try:
        from telegram import Bot
        from telegram.error import TelegramError
        return Bot, TelegramError
    except ImportError as e:
        print(f"Telegram bot import xatolik: {e}")
        return None, None


def send_telegram_notification(chat_id, message, parse_mode='HTML'):
    """Telegram xabar yuborish (sync) - retry bilan"""
    if not settings.TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN sozlanmagan!")
        return False
    
    if not chat_id:
        print(f"Chat ID bo'sh: {chat_id}")
        return False
    
    # Lazy import
    Bot, TelegramError = _get_telegram_bot()
    if Bot is None:
        print("Telegram bot import qilinmadi")
        return False
    
    import time
    import asyncio
    from urllib3.exceptions import HTTPError, NewConnectionError, MaxRetryError
    from requests.exceptions import ConnectionError, Timeout
    
    async def _send_async():
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode)
    
    def _send_sync():
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode)
    
    max_retries = 3
    retry_delay = 2  # soniya
    
    for attempt in range(max_retries):
        try:
            import inspect
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            if inspect.iscoroutinefunction(bot.send_message):
                asyncio.run(_send_async())
            else:
                _send_sync()
            return True
        except (HTTPError, ConnectionError, Timeout, NewConnectionError, MaxRetryError) as e:
            # Network xatolarini qayta urinish
            if attempt < max_retries - 1:
                print(f"Telegram xabar yuborishda network xatolik (qayta uriniladi {attempt + 1}/{max_retries}): {type(e).__name__}")
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            print(f"Telegram xabar yuborishda network xatolik (barcha urinishlar tugadi): {type(e).__name__}: {e}")
            return False
        except TelegramError as e:
            error_type = type(e).__name__
            # Telegram API xatolarini qayta urinish (faqat connection xatolari uchun)
            if error_type in ['NetworkError', 'TimedOut']:
                if attempt < max_retries - 1:
                    print(f"Telegram xabar yuborishda API xatolik (qayta uriniladi {attempt + 1}/{max_retries}): {e}")
                    time.sleep(retry_delay * (attempt + 1))
                    continue
            # Boshqa Telegram xatolarini log qilish, lekin qayta urinmaslik
            print(f"Telegram xabar yuborishda API xatolik: {e}")
            return False
        except Exception as e:
            error_type = type(e).__name__
            error_str = str(e)
            # Network xatolarini aniqlash
            if any(keyword in error_str.lower() for keyword in ['connection', 'network', 'timeout', 'getaddrinfo', 'failed to establish']):
                if attempt < max_retries - 1:
                    print(f"Telegram xabar yuborishda network xatolik (qayta uriniladi {attempt + 1}/{max_retries}): {error_type}: {e}")
                    time.sleep(retry_delay * (attempt + 1))
                    continue
            print(f"Telegram xabar yuborishda umumiy xatolik: {error_type}: {e}")
            return False
    
    return False


def send_to_admin(message):
    """Admin ga xabar yuborish"""
    if settings.TELEGRAM_ADMIN_CHAT_ID:
        return send_telegram_notification(settings.TELEGRAM_ADMIN_CHAT_ID, message)
    return False

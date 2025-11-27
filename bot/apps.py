from django.apps import AppConfig
import os


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'
    
    def ready(self):
        """Start bot when Django is ready (if enabled)."""
        # Only start if explicitly enabled via environment variable
        # For production, use the management command instead: python manage.py run_bot
        if os.environ.get('START_TELEGRAM_BOT', 'False').lower() == 'true':
            if not hasattr(self, '_bot_started'):
                try:
                    import threading
                    from .bot import start_bot
                    
                    # Run bot in a separate thread to avoid blocking
                    bot_thread = threading.Thread(target=start_bot, daemon=True)
                    bot_thread.start()
                    self._bot_started = True
                except Exception as e:
                    print(f"Warning: Could not start Telegram bot: {e}")


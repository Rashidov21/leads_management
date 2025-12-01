from django.core.management.base import BaseCommand
from crm_app.telegram_bot_handler import run_bot


class Command(BaseCommand):
    help = 'Telegram botni ishga tushiradi'

    def handle(self, *args, **options):
        run_bot()


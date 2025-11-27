"""
Management command to run the Telegram bot.
"""
from django.core.management.base import BaseCommand
from bot.bot import start_bot


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Telegram bot...'))
        try:
            start_bot()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Bot stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))


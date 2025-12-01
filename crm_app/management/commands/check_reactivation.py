from django.core.management.base import BaseCommand
from crm_app.services import ReactivationService


class Command(BaseCommand):
    help = 'Yo\'qotilgan lidlarni reaktivatsiya qiladi'

    def handle(self, *args, **options):
        ReactivationService.check_and_reactivate()
        self.stdout.write(self.style.SUCCESS('Reaktivatsiya tekshirildi'))


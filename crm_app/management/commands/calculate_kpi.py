from django.core.management.base import BaseCommand
from django.utils import timezone
from crm_app.models import User
from crm_app.services import KPIService


class Command(BaseCommand):
    help = 'Kunlik KPI hisoblaydi'

    def handle(self, *args, **options):
        today = timezone.now().date()
        sales_users = User.objects.filter(role='sales', is_active_sales=True)
        
        for sales in sales_users:
            kpi = KPIService.calculate_daily_kpi(sales, today)
            self.stdout.write(
                self.style.SUCCESS(f'{sales.username} KPI hisoblandi: {kpi.conversion_rate:.1f}%')
            )


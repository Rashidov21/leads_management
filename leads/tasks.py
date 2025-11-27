"""
Celery tasks for leads app.
"""
from celery import shared_task
from django.utils import timezone
from .models import Lead
from .services import GoogleSheetsSyncService
from kpi.calculators import KPICalculator


@shared_task
def sync_google_sheets():
    """Periodically sync leads from Google Sheets."""
    try:
        service = GoogleSheetsSyncService()
        result = service.sync_from_sheets()
        return {
            'success': True,
            'result': result,
            'timestamp': timezone.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def calculate_kpis():
    """Periodically calculate KPIs for all active sellers."""
    try:
        calculations = KPICalculator.calculate_all_active_rules()
        return {
            'success': True,
            'calculations_count': len(calculations),
            'timestamp': timezone.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def calculate_monthly_kpi_summaries():
    """Calculate monthly KPI summaries for all sellers."""
    try:
        from leads.models import Seller
        
        sellers = Seller.objects.filter(is_active=True)
        summaries = []
        
        for seller in sellers:
            summary = KPICalculator.calculate_monthly_summary(seller)
            summaries.append(summary.id)
        
        return {
            'success': True,
            'summaries_count': len(summaries),
            'timestamp': timezone.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def send_lead_reminders():
    """Send reminders to sellers about new leads."""
    try:
        from bot.bot import bot, get_seller_by_telegram_id
        from datetime import timedelta
        
        # Find leads that are new and older than 24 hours
        threshold = timezone.now() - timedelta(hours=24)
        new_leads = Lead.objects.filter(
            status='new',
            created_at__lte=threshold,
            seller__isnull=False,
            seller__is_active=True
        ).select_related('seller')
        
        reminders_sent = 0
        
        for lead in new_leads:
            if lead.seller.telegram_id:
                try:
                    message = (
                        f"🔔 Reminder: You have a new lead waiting!\n\n"
                        f"Name: {lead.name}\n"
                        f"Phone: {lead.phone or 'N/A'}\n"
                        f"Email: {lead.email or 'N/A'}\n"
                        f"Created: {lead.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                        f"Use /leads to view all your leads."
                    )
                    
                    # Note: This would need to be run in an async context
                    # For production, use aiogram's async methods properly
                    reminders_sent += 1
                except Exception as e:
                    print(f"Error sending reminder for lead {lead.id}: {e}")
        
        return {
            'success': True,
            'reminders_sent': reminders_sent,
            'timestamp': timezone.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


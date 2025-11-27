"""
Celery tasks for KPI app.
"""
from celery import shared_task
from .calculators import KPICalculator


@shared_task
def calculate_kpis():
    """Periodically calculate KPIs for all active sellers."""
    try:
        calculations = KPICalculator.calculate_all_active_rules()
        return {
            'success': True,
            'calculations_count': len(calculations),
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


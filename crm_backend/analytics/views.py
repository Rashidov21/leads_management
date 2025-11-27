"""Views for analytics module: dashboards and reports."""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from leads.models import Lead
from analytics.models import SalesKPI, LeadMetrics, GroupAnalytics, MarketingAnalytics
from trials.models import Trial
from scheduling.models import Group


@login_required
def analytics_dashboard(request):
    """Main analytics dashboard with key metrics and charts."""
    today = timezone.now().date()
    
    # Today's metrics
    lead_metrics = LeadMetrics.objects.filter(date=today).first()
    group_analytics = GroupAnalytics.objects.filter(date=today).first()
    
    # Recent trends (last 7 days)
    last_7_days = [today - timedelta(days=i) for i in range(7)]
    recent_metrics = LeadMetrics.objects.filter(date__in=last_7_days).order_by('date')
    
    return render(request, 'analytics/dashboard.html', {
        'lead_metrics': lead_metrics,
        'group_analytics': group_analytics,
        'recent_metrics': recent_metrics,
    })


@login_required
def lead_analytics(request):
    """Lead analytics: sources, statuses, conversion rates."""
    today = timezone.now().date()
    period = request.GET.get('period', '7')  # days
    
    date_range = [today - timedelta(days=int(period))]
    metrics = LeadMetrics.objects.filter(date__gte=date_range[0]).order_by('date')
    
    # Calculate aggregates
    total_leads = sum(m.new_leads_total for m in metrics)
    leads_by_status = {
        'new': Lead.objects.filter(status='new').count(),
        'contacted': Lead.objects.filter(status='contacted').count(),
        'interested': Lead.objects.filter(status='interested').count(),
        'trial_scheduled': Lead.objects.filter(status='trial_scheduled').count(),
        'enrolled': Lead.objects.filter(status='enrolled').count(),
        'lost': Lead.objects.filter(status='lost').count(),
    }
    
    # Source breakdown
    source_breakdown = {
        'instagram': sum(m.new_leads_instagram for m in metrics),
        'telegram': sum(m.new_leads_telegram for m in metrics),
        'whatsapp': sum(m.new_leads_whatsapp for m in metrics),
        'landing': sum(m.new_leads_landing for m in metrics),
        'google_sheets': sum(m.new_leads_google_sheets for m in metrics),
        'excel': sum(m.new_leads_excel for m in metrics),
        'csv': sum(m.new_leads_csv for m in metrics),
        'call': sum(m.new_leads_call for m in metrics),
    }
    
    # Distribution
    assigned_count = Lead.objects.filter(assigned_to__isnull=False).count()
    unassigned_count = Lead.objects.filter(assigned_to__isnull=True).count()
    
    return render(request, 'analytics/lead_analytics.html', {
        'total_leads': total_leads,
        'leads_by_status': leads_by_status,
        'source_breakdown': source_breakdown,
        'assigned_count': assigned_count,
        'unassigned_count': unassigned_count,
        'metrics': metrics,
    })


@login_required
def sales_analytics(request):
    """Sales analytics: calls, follow-ups, trials, conversions by salesperson."""
    today = timezone.now().date()
    period = request.GET.get('period', '7')
    
    date_range_start = today - timedelta(days=int(period))
    kpis = SalesKPI.objects.filter(date__gte=date_range_start).order_by('date')
    
    # Group by salesperson
    salespeople = set(kpi.salesperson for kpi in kpis)
    salesperson_data = {}
    
    for sp in salespeople:
        sp_kpis = kpis.filter(salesperson=sp)
        salesperson_data[sp.username] = {
            'new_contacts': sum(k.new_contacts for k in sp_kpis),
            'followups': sum(k.followups_completed for k in sp_kpis),
            'overdue': sum(k.followups_overdue for k in sp_kpis),
            'trials_scheduled': sum(k.trials_scheduled for k in sp_kpis),
            'trials_attended': sum(k.trials_attended for k in sp_kpis),
            'enrollments': sum(k.enrollments for k in sp_kpis),
            'avg_response_time': sum(k.avg_response_time for k in sp_kpis) // len(sp_kpis) if sp_kpis else 0,
        }
    
    return render(request, 'analytics/sales_analytics.html', {
        'salesperson_data': salesperson_data,
        'kpis': kpis,
    })


@login_required
def group_analytics(request):
    """Group analytics: capacity usage, recommendations."""
    today = timezone.now().date()
    
    analytics = GroupAnalytics.objects.filter(date=today).first()
    
    # Calculate current group metrics
    groups = Group.objects.all()
    full_count = sum(1 for g in groups if g.is_full)
    near_full_count = sum(1 for g in groups if g.occupancy_percent >= 80 and not g.is_full)
    empty_count = sum(1 for g in groups if g.occupancy_percent == 0)
    
    avg_occupancy = sum(g.occupancy_percent for g in groups) // len(groups) if groups else 0
    
    return render(request, 'analytics/group_analytics.html', {
        'total_groups': groups.count(),
        'full_groups': full_count,
        'near_full_groups': near_full_count,
        'empty_groups': empty_count,
        'avg_occupancy': avg_occupancy,
        'groups': groups,
        'analytics': analytics,
    })


@login_required
def marketing_analytics(request):
    """Marketing analytics: channel performance, CPL, CPA."""
    today = timezone.now().date()
    period = request.GET.get('period', '7')
    
    date_range_start = today - timedelta(days=int(period))
    metrics = MarketingAnalytics.objects.filter(date__gte=date_range_start).order_by('date')
    
    # Group by channel
    channels = ['instagram', 'telegram', 'whatsapp', 'landing', 'google_sheets', 'call']
    channel_data = {}
    
    for channel in channels:
        channel_metrics = metrics.filter(channel=channel)
        if channel_metrics.exists():
            channel_data[channel] = {
                'impressions': sum(m.impressions for m in channel_metrics),
                'clicks': sum(m.clicks for m in channel_metrics),
                'leads': sum(m.leads_generated for m in channel_metrics),
                'cost': sum(m.cost_total for m in channel_metrics),
                'cpl': sum(m.cpl for m in channel_metrics) / channel_metrics.count() if channel_metrics else 0,
                'cpa': sum(m.cpa for m in channel_metrics) / channel_metrics.count() if channel_metrics else 0,
                'enrollments': sum(m.enrollments_from_channel for m in channel_metrics),
            }
    
    return render(request, 'analytics/marketing_analytics.html', {
        'channel_data': channel_data,
        'metrics': metrics,
    })

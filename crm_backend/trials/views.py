"""Views for trials module: scheduling, tracking, and reminders."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Trial, TrialReminder
from leads.models import Lead
from scheduling.models import Group


@login_required
def trials_list(request):
    """Display trials with status filters: scheduled, attended, no_show."""
    status = request.GET.get('status', 'scheduled')
    
    trials = Trial.objects.select_related('lead', 'group').all()
    if status:
        trials = trials.filter(status=status)
    
    # Separate scheduled trials into upcoming and overdue
    now = timezone.now()
    upcoming = []
    overdue = []
    
    for trial in trials.filter(status='scheduled'):
        trial_dt = timezone.make_aware(
            timezone.datetime.combine(trial.scheduled_date, trial.scheduled_time)
        )
        if trial_dt > now:
            upcoming.append(trial)
        else:
            overdue.append(trial)
    
    return render(request, 'trials/trials.html', {
        'trials': trials,
        'upcoming': upcoming,
        'overdue': overdue,
        'status_filter': status,
    })


@login_required
def schedule_trial(request):
    """Schedule a trial for a lead."""
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        group_id = request.POST.get('group_id')
        date_str = request.POST.get('scheduled_date')
        time_str = request.POST.get('scheduled_time')
        
        lead = get_object_or_404(Lead, pk=lead_id)
        group = get_object_or_404(Group, pk=group_id)
        
        # Create trial
        trial = Trial.objects.create(
            lead=lead,
            group=group,
            scheduled_date=date_str,
            scheduled_time=time_str,
            status='scheduled'
        )
        
        # Create reminder: 2h before trial
        trial_dt = timezone.make_aware(
            timezone.datetime.combine(
                trial.scheduled_date,
                trial.scheduled_time
            )
        )
        pre_reminder_dt = trial_dt - timedelta(hours=2)
        post_reminder_dt = trial_dt + timedelta(minutes=3)
        
        TrialReminder.objects.create(
            trial=trial,
            pre_trial_reminder_scheduled_at=pre_reminder_dt,
            post_trial_reminder_scheduled_at=post_reminder_dt,
        )
        
        # Increment trial students in group
        group.trial_students += 1
        group.save()
        
        return redirect('trials:trials_list')
    
    leads = Lead.objects.filter(status__in=['interested', 'decision_pending']).all()
    groups = Group.objects.select_related('course').all()
    
    return render(request, 'trials/schedule_trial.html', {
        'leads': leads,
        'groups': groups,
    })


@login_required
def mark_attended(request, pk):
    """Mark trial as attended."""
    trial = get_object_or_404(Trial, pk=pk)
    trial.status = 'attended'
    trial.actual_attendance_time = timezone.now()
    trial.trial_completed_at = timezone.now()
    trial.save()
    
    # Decrement trial students, add to current
    if trial.group:
        trial.group.trial_students = max(0, trial.group.trial_students - 1)
        trial.group.save()
    
    return redirect('trials:trials_list')


@login_required
def mark_no_show(request, pk):
    """Mark trial as no-show."""
    trial = get_object_or_404(Trial, pk=pk)
    trial.status = 'no_show'
    trial.trial_completed_at = timezone.now()
    trial.save()
    
    # Decrement trial students
    if trial.group:
        trial.group.trial_students = max(0, trial.group.trial_students - 1)
        trial.group.save()
    
    return redirect('trials:trials_list')


@login_required
def make_sales_offer(request, pk):
    """Make sales offer after trial and update lead status."""
    trial = get_object_or_404(Trial, pk=pk)
    trial.result = 'sales_offer'
    trial.sales_offer_made_at = timezone.now()
    trial.save()
    
    # Update lead status
    trial.lead.status = 'sales_offer'
    trial.lead.save()
    
    return redirect('trials:trials_list')

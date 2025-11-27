"""Template views for reminders (non-API).

These views render the `reminders.html` template and provide simple
POST endpoints for actions such as marking a reminder as contacted or
snoozing a reminder. More advanced logic is handled by Celery tasks.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from leads.models import LeadReminder
from .tasks import mark_reminder_contacted


@login_required
def pending_reminders(request):
    if request.user.is_staff:
        reminders = LeadReminder.objects.filter(status='pending').order_by('contact_deadline')
    else:
        reminders = LeadReminder.objects.filter(status='pending', lead__assigned_to=request.user).order_by('contact_deadline')

    return render(request, 'reminders.html', {'reminders': reminders})


@login_required
def overdue_reminders(request):
    now = timezone.now()
    if request.user.is_staff:
        reminders = LeadReminder.objects.filter(status__in=['pending','notified'], contact_deadline__lt=now).order_by('contact_deadline')
    else:
        reminders = LeadReminder.objects.filter(status__in=['pending','notified'], contact_deadline__lt=now, lead__assigned_to=request.user).order_by('contact_deadline')

    return render(request, 'reminders.html', {'reminders': reminders, 'overdue': True})


@login_required
def mark_contacted(request, pk):
    reminder = get_object_or_404(LeadReminder, pk=pk)
    mark_reminder_contacted.delay(reminder.id)
    return redirect('pending_reminders')


@login_required
def snooze_reminder(request, pk):
    reminder = get_object_or_404(LeadReminder, pk=pk)
    minutes = int(request.POST.get('minutes', 5))
    reminder.contact_deadline = timezone.now() + timezone.timedelta(minutes=minutes)
    reminder.status = 'snoozed'
    reminder.save()
    return redirect('pending_reminders')

"""Celery tasks for reminders."""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from leads.models import LeadReminder


@shared_task
def check_reminder_deadlines():
    """
    Check for reminder deadlines and notify salespeople.
    Runs every 1 minute.
    """
    now = timezone.now()
    
    # Get pending reminders that have passed deadline
    overdue_reminders = LeadReminder.objects.filter(
        status='pending',
        contact_deadline__lte=now
    ).select_related('lead', 'lead__assigned_to')
    
    for reminder in overdue_reminders:
        # Send notification to assigned salesperson
        send_reminder_notification.delay(reminder.id)
        
        # Update reminder
        reminder.status = 'notified'
        reminder.last_reminder_at = now
        reminder.reminder_count += 1
        reminder.save()


@shared_task
def send_reminder_notification(reminder_id: int):
    """
    Send notification to salesperson about a lead.
    
    Can be extended to send email, SMS, or push notifications.
    """
    try:
        reminder = LeadReminder.objects.get(id=reminder_id)
        lead = reminder.lead
        salesperson = lead.assigned_to
        
        if not salesperson:
            return
        
        # You can extend this with actual notification methods:
        # - Email notification
        # - SMS notification
        # - Push notification
        # - In-app notification
        
        message = f"Reminder: You need to contact {lead.name} ({lead.phone}) within 5 minutes."
        
        # Example: Send email
        try:
            send_email_notification(
                recipient=salesperson.email,
                subject=f"Lead Follow-up Reminder: {lead.name}",
                message=message,
                lead=lead
            )
        except Exception as e:
            print(f"Error sending email: {e}")
    
    except LeadReminder.DoesNotExist:
        pass


def send_email_notification(recipient: str, subject: str, message: str, lead=None):
    """
    Send email notification to salesperson.
    
    This is a placeholder that can be extended with email service.
    """
    from django.core.mail import send_mail
    from django.conf import settings
    
    html_message = f"""
    <h2>{subject}</h2>
    <p>{message}</p>
    <hr>
    <h3>Lead Details:</h3>
    <p><strong>Name:</strong> {lead.name}</p>
    <p><strong>Phone:</strong> {lead.phone}</p>
    <p><strong>Source:</strong> {lead.get_source_display()}</p>
    <p><strong>Status:</strong> {lead.get_status_display()}</p>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email: {e}")


@shared_task
def mark_reminder_contacted(reminder_id: int):
    """Mark a reminder as contacted."""
    try:
        reminder = LeadReminder.objects.get(id=reminder_id)
        reminder.status = 'contacted'
        reminder.contacted_at = timezone.now()
        reminder.save()
    except LeadReminder.DoesNotExist:
        pass

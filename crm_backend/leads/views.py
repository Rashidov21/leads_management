"""Simple Django views for rendering front-end templates (non-API)."""
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Lead


def leads_list(request):
    """Render the leads listing page (uses `frontend/templates/leads.html`)."""
    leads = Lead.objects.all().order_by('-created_at')[:200]
    return render(request, 'leads.html', {'leads': leads})


def create_lead(request):
    """Create a lead via a simple HTML form POST (non-API).

    Expects form fields: name, phone, source, interested_course.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        source = request.POST.get('source', 'manual')
        interested_course = request.POST.get('interested_course')

        if name and phone:
            Lead.objects.get_or_create(
                phone=phone,
                defaults={
                    'name': name,
                    'source': source,
                    'interested_course': interested_course,
                }
            )
        return redirect('leads_list')

    return render(request, 'leads.html')


def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    return render(request, 'leads.html', {'lead': lead})

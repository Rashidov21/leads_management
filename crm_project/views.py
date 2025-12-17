"""
Custom error views for CRM project
"""
from django.shortcuts import render


def custom_404(request, exception=None):
    """Custom 404 error page"""
    return render(request, '404.html', {
        'exception': str(exception) if exception else None
    }, status=404)


def custom_500(request):
    """Custom 500 error page"""
    return render(request, '500.html', status=500)


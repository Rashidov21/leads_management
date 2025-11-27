"""
Views for campaigns app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import SMSCampaign, SMSCampaignLog
from leads.models import Lead, Seller


@staff_member_required
def campaign_list(request):
    """List all SMS campaigns."""
    campaigns = SMSCampaign.objects.prefetch_related('target_sellers').order_by('-created_at')
    context = {
        'campaigns': campaigns,
    }
    return render(request, 'campaigns/campaign_list.html', context)


@staff_member_required
def campaign_create(request):
    """Create a new SMS campaign."""
    if request.method == 'POST':
        # This is a stub - full implementation would create the campaign
        messages.info(request, 'SMS kampaniya yaratish kelajakdagi amalga oshirish uchun qoralama.')
        return redirect('campaigns:campaign_list')
    
    sellers = Seller.objects.filter(is_active=True)
    context = {
        'sellers': sellers,
    }
    return render(request, 'campaigns/campaign_create.html', context)


@staff_member_required
def campaign_detail(request, campaign_id):
    """Detail view for an SMS campaign."""
    campaign = get_object_or_404(SMSCampaign.objects.prefetch_related('target_sellers', 'logs__lead'), id=campaign_id)
    logs = campaign.logs.select_related('lead').order_by('-created_at')[:50]
    
    context = {
        'campaign': campaign,
        'logs': logs,
    }
    return render(request, 'campaigns/campaign_detail.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def api_send_sms(request):
    """
    API endpoint for sending SMS (stub for future implementation).
    
    Expected JSON payload:
    {
        "phone": "+1234567890",
        "message": "Your message here",
        "campaign_id": 1 (optional)
    }
    """
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        message = data.get('message')
        campaign_id = data.get('campaign_id')
        
        if not phone or not message:
            return JsonResponse({
                'success': False,
                'error': 'phone and message are required'
            }, status=400)
        
        # Stub implementation - would integrate with actual SMS provider
        response = {
            'success': True,
            'message_id': f'stub_{phone}_{hash(message)}',
            'status': 'queued',
            'note': 'This is a stub endpoint. Integrate with your SMS provider API.'
        }
        
        return JsonResponse(response)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_campaign_status(request):
    """
    API endpoint for checking campaign status (stub).
    
    Query params: campaign_id
    """
    campaign_id = request.GET.get('campaign_id')
    
    if not campaign_id:
        return JsonResponse({
            'success': False,
            'error': 'campaign_id is required'
        }, status=400)
    
    try:
        campaign = SMSCampaign.objects.get(id=campaign_id)
        return JsonResponse({
            'success': True,
            'campaign_id': campaign.id,
            'status': campaign.status,
            'total_recipients': campaign.total_recipients,
            'sent_count': campaign.sent_count,
            'failed_count': campaign.failed_count,
        })
    except SMSCampaign.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Campaign not found'
        }, status=404)


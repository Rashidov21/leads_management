"""
Views for leads app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
import csv
from .models import Lead, Seller


@staff_member_required
def dashboard(request):
    """Main dashboard view."""
    # Statistics
    total_leads = Lead.objects.count()
    new_leads = Lead.objects.filter(status='new').count()
    contacted_leads = Lead.objects.filter(status='contacted').count()
    converted_leads = Lead.objects.filter(status='converted').count()
    
    # Recent leads
    recent_leads = Lead.objects.select_related('seller').order_by('-created_at')[:10]
    
    # Leads by seller
    leads_by_seller = Seller.objects.annotate(
        total_leads=Count('leads'),
        new_leads=Count('leads', filter=Q(leads__status='new')),
        converted_leads=Count('leads', filter=Q(leads__status='converted'))
    ).filter(is_active=True)
    
    context = {
        'total_leads': total_leads,
        'new_leads': new_leads,
        'contacted_leads': contacted_leads,
        'converted_leads': converted_leads,
        'recent_leads': recent_leads,
        'leads_by_seller': leads_by_seller,
    }
    return render(request, 'leads/dashboard.html', context)


@staff_member_required
def lead_list(request):
    """List all leads with filtering."""
    leads = Lead.objects.select_related('seller').order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status')
    seller_filter = request.GET.get('seller')
    search_query = request.GET.get('search')
    
    if status_filter:
        leads = leads.filter(status=status_filter)
    if seller_filter:
        leads = leads.filter(seller_id=seller_filter)
    if search_query:
        leads = leads.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    sellers = Seller.objects.filter(is_active=True)
    
    context = {
        'leads': leads,
        'sellers': sellers,
        'status_filter': status_filter,
        'seller_filter': seller_filter,
        'search_query': search_query,
    }
    return render(request, 'leads/lead_list.html', context)


@staff_member_required
def lead_detail(request, lead_id):
    """Detail view for a single lead."""
    lead = get_object_or_404(Lead.objects.select_related('seller'), id=lead_id)
    context = {
        'lead': lead,
    }
    return render(request, 'leads/lead_detail.html', context)


@staff_member_required
def lead_create(request):
    """Create a new lead."""
    if request.method == 'POST':
        try:
            lead = Lead.objects.create(
                name=request.POST.get('name'),
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone', ''),
                company=request.POST.get('company', ''),
                seller_id=request.POST.get('seller') or None,
                status=request.POST.get('status', 'new'),
                source=request.POST.get('source', 'manual'),
                notes=request.POST.get('notes', ''),
            )
            messages.success(request, f'Lid "{lead.name}" muvaffaqiyatli yaratildi.')
            return redirect('lead_detail', lead_id=lead.id)
        except Exception as e:
            messages.error(request, f'Lid yaratishda xatolik: {str(e)}')
    
    sellers = Seller.objects.filter(is_active=True)
    context = {
        'sellers': sellers,
        'status_choices': Lead.STATUS_CHOICES,
    }
    return render(request, 'leads/lead_form.html', context)


@staff_member_required
def lead_edit(request, lead_id):
    """Edit an existing lead."""
    lead = get_object_or_404(Lead, id=lead_id)
    
    if request.method == 'POST':
        try:
            lead.name = request.POST.get('name')
            lead.email = request.POST.get('email', '')
            lead.phone = request.POST.get('phone', '')
            lead.company = request.POST.get('company', '')
            lead.seller_id = request.POST.get('seller') or None
            lead.status = request.POST.get('status', 'new')
            lead.source = request.POST.get('source', 'manual')
            lead.notes = request.POST.get('notes', '')
            lead.save()
            messages.success(request, f'Lid "{lead.name}" muvaffaqiyatli yangilandi.')
            return redirect('lead_detail', lead_id=lead.id)
        except Exception as e:
            messages.error(request, f'Lid yangilashda xatolik: {str(e)}')
    
    sellers = Seller.objects.filter(is_active=True)
    context = {
        'lead': lead,
        'sellers': sellers,
        'status_choices': Lead.STATUS_CHOICES,
    }
    return render(request, 'leads/lead_form.html', context)


@staff_member_required
def lead_delete(request, lead_id):
    """Delete a lead."""
    lead = get_object_or_404(Lead, id=lead_id)
    
    if request.method == 'POST':
        lead_name = lead.name
        lead.delete()
        messages.success(request, f'Lid "{lead_name}" muvaffaqiyatli o\'chirildi.')
        return redirect('lead_list')
    
    context = {'lead': lead}
    return render(request, 'leads/lead_confirm_delete.html', context)


@staff_member_required
def lead_export(request):
    """Export leads to CSV."""
    leads = Lead.objects.select_related('seller').order_by('-created_at')
    
    # Apply filters
    status_filter = request.GET.get('status')
    seller_filter = request.GET.get('seller')
    search_query = request.GET.get('search')
    
    if status_filter:
        leads = leads.filter(status=status_filter)
    if seller_filter:
        leads = leads.filter(seller_id=seller_filter)
    if search_query:
        leads = leads.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="leads_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Company', 'Seller', 'Status', 'Source', 'Created At', 'Updated At'])
    
    for lead in leads:
        writer.writerow([
            lead.id,
            lead.name,
            lead.email,
            lead.phone,
            lead.company,
            lead.seller.user.get_full_name() if lead.seller else '',
            lead.get_status_display(),
            lead.source,
            lead.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            lead.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    
    return response


# Salesperson (Seller) CRUD Views
@staff_member_required
def seller_list(request):
    """List all sellers."""
    sellers = Seller.objects.select_related('user').order_by('-created_at')
    
    # Filtering
    is_active_filter = request.GET.get('is_active')
    search_query = request.GET.get('search')
    
    if is_active_filter is not None:
        sellers = sellers.filter(is_active=is_active_filter == 'true')
    if search_query:
        sellers = sellers.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    context = {
        'sellers': sellers,
        'is_active_filter': is_active_filter,
        'search_query': search_query,
    }
    return render(request, 'leads/seller_list.html', context)


@staff_member_required
def seller_create(request):
    """Create a new seller."""
    if request.method == 'POST':
        try:
            # Create or get user
            username = request.POST.get('username')
            email = request.POST.get('email', '')
            password = request.POST.get('password')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Bu foydalanuvchi nomi allaqachon mavjud.')
                return redirect('seller_create')
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
            )
            
            # Create seller
            seller = Seller.objects.create(
                user=user,
                telegram_id=request.POST.get('telegram_id') or None,
                phone_number=request.POST.get('phone_number', ''),
                is_active=request.POST.get('is_active') == 'on',
            )
            messages.success(request, f'Sotuvchi "{user.get_full_name() or username}" muvaffaqiyatli yaratildi.')
            return redirect('seller_list')
        except Exception as e:
            messages.error(request, f'Sotuvchi yaratishda xatolik: {str(e)}')
    
    return render(request, 'leads/seller_form.html')


@staff_member_required
def seller_edit(request, seller_id):
    """Edit an existing seller."""
    seller = get_object_or_404(Seller.objects.select_related('user'), id=seller_id)
    
    if request.method == 'POST':
        try:
            user = seller.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            if request.POST.get('password'):
                user.set_password(request.POST.get('password'))
            user.save()
            
            seller.telegram_id = request.POST.get('telegram_id') or None
            seller.phone_number = request.POST.get('phone_number', '')
            seller.is_active = request.POST.get('is_active') == 'on'
            seller.save()
            
            messages.success(request, f'Sotuvchi "{user.get_full_name() or user.username}" muvaffaqiyatli yangilandi.')
            return redirect('seller_list')
        except Exception as e:
            messages.error(request, f'Sotuvchi yangilashda xatolik: {str(e)}')
    
    context = {'seller': seller}
    return render(request, 'leads/seller_form.html', context)


@staff_member_required
def seller_delete(request, seller_id):
    """Delete a seller."""
    seller = get_object_or_404(Seller.objects.select_related('user'), id=seller_id)
    
    if request.method == 'POST':
        seller_name = seller.user.get_full_name() or seller.user.username
        seller.user.delete()  # This will also delete the seller due to CASCADE
        messages.success(request, f'Sotuvchi "{seller_name}" muvaffaqiyatli o\'chirildi.')
        return redirect('seller_list')
    
    context = {'seller': seller}
    return render(request, 'leads/seller_confirm_delete.html', context)


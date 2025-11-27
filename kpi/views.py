"""
Views for KPI app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum
from .models import KPIRule, KPICalculation, SellerKPISummary
from .calculators import KPICalculator
from leads.models import Seller


@staff_member_required
def kpi_dashboard(request):
    """Main KPI dashboard."""
    active_rules = KPIRule.objects.filter(is_active=True).count()
    recent_calculations = KPICalculation.objects.select_related('seller', 'rule').order_by('-calculated_at')[:10]
    
    # Total bonuses/penalties
    total_stats = KPICalculation.objects.aggregate(
        total_bonus=Sum('bonus_amount'),
        total_penalty=Sum('penalty_amount')
    )
    
    # Monthly summaries
    recent_summaries = SellerKPISummary.objects.select_related('seller').order_by('-month', '-seller')[:20]
    
    context = {
        'active_rules': active_rules,
        'recent_calculations': recent_calculations,
        'total_stats': total_stats,
        'recent_summaries': recent_summaries,
    }
    return render(request, 'kpi/dashboard.html', context)


@staff_member_required
def rule_list(request):
    """List all KPI rules."""
    rules = KPIRule.objects.all().order_by('-created_at')
    context = {
        'rules': rules,
    }
    return render(request, 'kpi/rule_list.html', context)


@staff_member_required
def rule_detail(request, rule_id):
    """Detail view for a KPI rule."""
    rule = get_object_or_404(KPIRule, id=rule_id)
    recent_calculations = KPICalculation.objects.filter(rule=rule).select_related('seller').order_by('-calculated_at')[:20]
    
    context = {
        'rule': rule,
        'recent_calculations': recent_calculations,
    }
    return render(request, 'kpi/rule_detail.html', context)


@staff_member_required
def rule_edit(request, rule_id):
    """Edit a KPI rule."""
    rule = get_object_or_404(KPIRule, id=rule_id)
    
    if request.method == 'POST':
        # Update rule fields
        rule.name = request.POST.get('name', rule.name)
        rule.rule_type = request.POST.get('rule_type', rule.rule_type)
        rule.comparison = request.POST.get('comparison', rule.comparison)
        rule.threshold_value = request.POST.get('threshold_value') or None
        rule.threshold_min = request.POST.get('threshold_min') or None
        rule.threshold_max = request.POST.get('threshold_max') or None
        rule.bonus_amount = request.POST.get('bonus_amount', 0)
        rule.penalty_amount = request.POST.get('penalty_amount', 0)
        rule.evaluation_period_days = request.POST.get('evaluation_period_days', 30)
        rule.is_active = request.POST.get('is_active') == 'on'
        
        try:
            rule.full_clean()
            rule.save()
            messages.success(request, f'Qoida "{rule.name}" muvaffaqiyatli yangilandi.')
            return redirect('kpi:rule_detail', rule_id=rule.id)
        except Exception as e:
            messages.error(request, f'Qoidani yangilashda xatolik: {str(e)}')
    
    context = {
        'rule': rule,
        'rule_type_choices': KPIRule.RULE_TYPE_CHOICES,
        'comparison_choices': KPIRule.COMPARISON_CHOICES,
    }
    return render(request, 'kpi/rule_form.html', context)


@staff_member_required
def calculation_list(request):
    """List all KPI calculations."""
    calculations = KPICalculation.objects.select_related('seller', 'rule').order_by('-calculated_at')
    
    # Filtering
    seller_filter = request.GET.get('seller')
    rule_filter = request.GET.get('rule')
    
    if seller_filter:
        calculations = calculations.filter(seller_id=seller_filter)
    if rule_filter:
        calculations = calculations.filter(rule_id=rule_filter)
    
    sellers = Seller.objects.filter(is_active=True)
    rules = KPIRule.objects.filter(is_active=True)
    
    context = {
        'calculations': calculations,
        'sellers': sellers,
        'rules': rules,
        'seller_filter': seller_filter,
        'rule_filter': rule_filter,
    }
    return render(request, 'kpi/calculation_list.html', context)


@staff_member_required
def summary_list(request):
    """List all seller KPI summaries."""
    summaries = SellerKPISummary.objects.select_related('seller').order_by('-month', '-seller')
    
    seller_filter = request.GET.get('seller')
    if seller_filter:
        summaries = summaries.filter(seller_id=seller_filter)
    
    sellers = Seller.objects.filter(is_active=True)
    
    context = {
        'summaries': summaries,
        'sellers': sellers,
        'seller_filter': seller_filter,
    }
    return render(request, 'kpi/summary_list.html', context)


@staff_member_required
def trigger_calculation(request):
    """Manually trigger KPI calculation."""
    if request.method == 'POST':
        seller_id = request.POST.get('seller')
        seller = None
        if seller_id:
            seller = get_object_or_404(Seller, id=seller_id)
        
        try:
            calculations = KPICalculator.calculate_all_active_rules(seller=seller)
            messages.success(request, f'{len(calculations)} ta KPI qoidasi hisoblandi.')
        except Exception as e:
            messages.error(request, f'KPI larni hisoblashda xatolik: {str(e)}')
    
    return redirect('kpi:kpi_dashboard')


# KPI Rule CRUD Views
@staff_member_required
def rule_create(request):
    """Create a new KPI rule."""
    if request.method == 'POST':
        try:
            rule = KPIRule.objects.create(
                name=request.POST.get('name'),
                rule_type=request.POST.get('rule_type'),
                comparison=request.POST.get('comparison'),
                threshold_value=request.POST.get('threshold_value') or None,
                threshold_min=request.POST.get('threshold_min') or None,
                threshold_max=request.POST.get('threshold_max') or None,
                bonus_amount=request.POST.get('bonus_amount', 0),
                penalty_amount=request.POST.get('penalty_amount', 0),
                evaluation_period_days=request.POST.get('evaluation_period_days', 30),
                is_active=request.POST.get('is_active') == 'on',
            )
            rule.full_clean()  # Validate
            rule.save()
            messages.success(request, f'KPI qoidasi "{rule.name}" muvaffaqiyatli yaratildi.')
            return redirect('kpi:rule_detail', rule_id=rule.id)
        except Exception as e:
            messages.error(request, f'KPI qoidasi yaratishda xatolik: {str(e)}')
    
    context = {
        'rule_type_choices': KPIRule.RULE_TYPE_CHOICES,
        'comparison_choices': KPIRule.COMPARISON_CHOICES,
    }
    return render(request, 'kpi/rule_form.html', context)


@staff_member_required
def rule_edit(request, rule_id):
    """Edit an existing KPI rule."""
    rule = get_object_or_404(KPIRule, id=rule_id)
    
    if request.method == 'POST':
        try:
            rule.name = request.POST.get('name')
            rule.rule_type = request.POST.get('rule_type')
            rule.comparison = request.POST.get('comparison')
            rule.threshold_value = request.POST.get('threshold_value') or None
            rule.threshold_min = request.POST.get('threshold_min') or None
            rule.threshold_max = request.POST.get('threshold_max') or None
            rule.bonus_amount = request.POST.get('bonus_amount', 0)
            rule.penalty_amount = request.POST.get('penalty_amount', 0)
            rule.evaluation_period_days = request.POST.get('evaluation_period_days', 30)
            rule.is_active = request.POST.get('is_active') == 'on'
            rule.full_clean()  # Validate
            rule.save()
            messages.success(request, f'KPI qoidasi "{rule.name}" muvaffaqiyatli yangilandi.')
            return redirect('kpi:rule_detail', rule_id=rule.id)
        except Exception as e:
            messages.error(request, f'KPI qoidasi yangilashda xatolik: {str(e)}')
    
    context = {
        'rule': rule,
        'rule_type_choices': KPIRule.RULE_TYPE_CHOICES,
        'comparison_choices': KPIRule.COMPARISON_CHOICES,
    }
    return render(request, 'kpi/rule_form.html', context)


@staff_member_required
def rule_delete(request, rule_id):
    """Delete a KPI rule."""
    rule = get_object_or_404(KPIRule, id=rule_id)
    
    if request.method == 'POST':
        rule_name = rule.name
        rule.delete()
        messages.success(request, f'KPI qoidasi "{rule_name}" muvaffaqiyatli o\'chirildi.')
        return redirect('kpi:rule_list')
    
    context = {'rule': rule}
    return render(request, 'kpi/rule_confirm_delete.html', context)

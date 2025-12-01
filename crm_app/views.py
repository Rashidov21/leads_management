from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, F
from django.utils import timezone
from datetime import date, timedelta
from .models import (
    Lead, Course, Group, Room, FollowUp, TrialLesson, 
    KPI, User, Reactivation
)
from .forms import (
    LeadForm, LeadStatusForm, TrialLessonForm, TrialResultForm,
    FollowUpForm, ExcelImportForm
)
from .decorators import role_required, admin_required, manager_or_admin_required
from .services import (
    LeadDistributionService, FollowUpService, GroupService,
    KPIService, ReactivationService
)
import pandas as pd


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Login yoki parol noto\'g\'ri')
    
    return render(request, 'login.html')


@login_required
def dashboard(request):
    context = {}
    
    if request.user.is_admin or request.user.is_sales_manager:
        # Admin/Manager dashboard
        context.update({
            'total_leads': Lead.objects.count(),
            'new_leads_today': Lead.objects.filter(
                created_at__date=timezone.now().date(),
                status='new'
            ).count(),
            'total_sales': User.objects.filter(role='sales', is_active_sales=True).count(),
            'active_groups': Group.objects.filter(is_active=True).count(),
            'overdue_followups': FollowUpService.get_overdue_followups().count(),
        })
    else:
        # Sales dashboard
        sales = request.user
        context.update({
            'my_leads': Lead.objects.filter(assigned_sales=sales).count(),
            'today_followups': FollowUpService.get_today_followups(sales).count(),
            'overdue_followups': FollowUpService.get_overdue_followups(sales).count(),
            'is_blocked': FollowUpService.check_sales_blocked(sales),
        })
    
    return render(request, 'dashboard.html', context)


@login_required
@role_required('admin', 'sales_manager', 'sales')
def leads_list(request):
    queryset = Lead.objects.all()
    
    if request.user.is_sales:
        queryset = queryset.filter(assigned_sales=request.user)
    
    # Filtrlash
    status_filter = request.GET.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    source_filter = request.GET.get('source')
    if source_filter:
        queryset = queryset.filter(source=source_filter)
    
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) | Q(phone__icontains=search)
        )
    
    context = {
        'leads': queryset.order_by('-created_at'),
        'statuses': Lead.STATUS_CHOICES,
        'sources': Lead.SOURCE_CHOICES,
    }
    return render(request, 'leads/list.html', context)


@login_required
@role_required('admin', 'sales_manager', 'sales')
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    # Faqat o'z lidlari bilan ishlash
    if request.user.is_sales and lead.assigned_sales != request.user:
        messages.error(request, "Sizda bu lidni ko'rish huquqi yo'q")
        return redirect('leads_list')
    
    if request.method == 'POST':
        form = LeadStatusForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, 'Status yangilandi')
            return redirect('lead_detail', pk=pk)
    else:
        form = LeadStatusForm(instance=lead)
    
    context = {
        'lead': lead,
        'form': form,
        'followups': lead.followups.all().order_by('-due_date'),
        'trials': lead.trials.all().order_by('-date'),
    }
    return render(request, 'leads/detail.html', context)


@login_required
@role_required('admin', 'sales_manager', 'sales')
def lead_create(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            if not lead.assigned_sales:
                # Avtomatik taqsimlash
                LeadDistributionService.distribute_leads([lead])
            lead.save()
            messages.success(request, 'Lid qo\'shildi')
            return redirect('lead_detail', pk=lead.pk)
    else:
        form = LeadForm()
    
    return render(request, 'leads/create.html', {'form': form})


@login_required
@role_required('admin', 'sales_manager')
def lead_assign(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        sales_id = request.POST.get('sales_id')
        sales = get_object_or_404(User, pk=sales_id, role='sales')
        lead.assigned_sales = sales
        lead.save()
        messages.success(request, f'Lid {sales.username} ga biriktirildi')
        return redirect('lead_detail', pk=pk)
    
    sales_list = User.objects.filter(role='sales', is_active_sales=True)
    return render(request, 'leads/assign.html', {
        'lead': lead,
        'sales_list': sales_list
    })


@login_required
@role_required('admin', 'sales_manager', 'sales')
def followups_today(request):
    followups = FollowUpService.get_today_followups(
        sales=request.user if request.user.is_sales else None
    )
    
    if request.method == 'POST':
        followup_id = request.POST.get('followup_id')
        followup = get_object_or_404(FollowUp, pk=followup_id)
        if request.user.is_sales and followup.sales != request.user:
            messages.error(request, "Sizda bu follow-upni bajarish huquqi yo'q")
        else:
            followup.mark_completed()
            messages.success(request, 'Follow-up bajarildi')
        return redirect('followups_today')
    
    return render(request, 'followups/today.html', {'followups': followups})


@login_required
@role_required('admin', 'sales_manager', 'sales')
def trial_register(request, lead_pk):
    lead = get_object_or_404(Lead, pk=lead_pk)
    
    if request.user.is_sales and lead.assigned_sales != request.user:
        messages.error(request, "Sizda bu lidni sinovga yozish huquqi yo'q")
        return redirect('leads_list')
    
    if request.method == 'POST':
        form = TrialLessonForm(request.POST)
        if form.is_valid():
            trial = form.save(commit=False)
            trial.lead = lead
            
            # Overbooking tekshirish
            if not GroupService.can_enroll_to_group(trial.group):
                messages.error(request, 'Bu guruh to\'lgan!')
                return render(request, 'trials/register.html', {
                    'lead': lead,
                    'form': form
                })
            
            trial.save()
            lead.status = 'trial_registered'
            lead.save()
            messages.success(request, 'Sinovga yozildi')
            return redirect('lead_detail', pk=lead_pk)
    else:
        form = TrialLessonForm()
        # Faqat mavjud guruhlarni ko'rsatish
        if lead.interested_course:
            form.fields['group'].queryset = GroupService.get_available_groups(
                course=lead.interested_course
            )
    
    return render(request, 'trials/register.html', {
        'lead': lead,
        'form': form
    })


@login_required
@role_required('admin', 'sales_manager', 'sales')
def trial_result(request, trial_pk):
    trial = get_object_or_404(TrialLesson, pk=trial_pk)
    
    if request.user.is_sales and trial.lead.assigned_sales != request.user:
        messages.error(request, "Sizda bu sinov natijasini kiritish huquqi yo'q")
        return redirect('leads_list')
    
    if request.method == 'POST':
        form = TrialResultForm(request.POST, instance=trial)
        if form.is_valid():
            trial = form.save()
            lead = trial.lead
            
            if trial.result == 'attended':
                lead.status = 'trial_attended'
            elif trial.result == 'not_attended':
                lead.status = 'trial_not_attended'
            elif trial.result == 'accepted':
                lead.status = 'enrolled'
                lead.enrolled_group = trial.group
                trial.group.current_students += 1
                trial.group.save()
            elif trial.result == 'rejected':
                lead.status = 'lost'
            
            lead.save()
            messages.success(request, 'Sinov natijasi saqlandi')
            return redirect('lead_detail', pk=lead.pk)
    else:
        form = TrialResultForm(instance=trial)
    
    return render(request, 'trials/result.html', {
        'trial': trial,
        'form': form
    })


@login_required
@admin_required
def courses_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/list.html', {'courses': courses})


@login_required
@admin_required
def groups_list(request):
    groups = Group.objects.all().select_related('course', 'room')
    return render(request, 'groups/list.html', {'groups': groups})


@login_required
@manager_or_admin_required
def analytics(request):
    context = {}
    
    # Lid statistikasi
    context['leads_stats'] = {
        'total': Lead.objects.count(),
        'new_today': Lead.objects.filter(created_at__date=timezone.now().date()).count(),
        'by_status': dict(Lead.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')),
        'by_source': dict(Lead.objects.values('source').annotate(count=Count('id')).values_list('source', 'count')),
    }
    
    # Sotuvchi statistikasi
    if request.user.is_admin:
        sales_stats = []
        for sales in User.objects.filter(role='sales', is_active_sales=True):
            kpi = KPIService.calculate_daily_kpi(sales, timezone.now().date())
            sales_stats.append({
                'sales': sales,
                'kpi': kpi,
                'overdue': FollowUpService.get_overdue_followups(sales).count(),
            })
        context['sales_stats'] = sales_stats
    
    # Guruh statistikasi
    context['groups_stats'] = {
        'total': Group.objects.count(),
        'full': Group.objects.filter(current_students__gte=F('capacity')).count(),
        'available': Group.objects.filter(current_students__lt=F('capacity')).count(),
    }
    
    return render(request, 'analytics/index.html', context)


@login_required
@role_required('admin', 'sales_manager')
def excel_import(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                df = pd.read_excel(request.FILES['file'])
                leads = []
                
                for _, row in df.iterrows():
                    # Duplicate tekshirish
                    if Lead.objects.filter(phone=str(row.get('phone', ''))).exists():
                        continue
                    
                    lead = Lead(
                        name=str(row.get('name', '')),
                        phone=str(row.get('phone', '')),
                        source='excel',
                    )
                    leads.append(lead)
                
                # Taqsimlash
                if leads:
                    LeadDistributionService.distribute_leads(leads)
                    for lead in leads:
                        lead.save()
                    
                    messages.success(request, f'{len(leads)} ta lid import qilindi')
                else:
                    messages.warning(request, 'Yangi lid topilmadi')
                
                return redirect('leads_list')
            except Exception as e:
                messages.error(request, f'Xatolik: {str(e)}')
    else:
        form = ExcelImportForm()
    
    return render(request, 'leads/import.html', {'form': form})


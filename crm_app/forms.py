from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Lead, Course, Group, TrialLesson, User, FollowUp, Room, LeaveRequest, SalesMessage


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'phone', 'interested_course', 'source', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ismni kiriting'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+998901234567',
                'type': 'tel'
            }),
            'interested_course': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Qo\'shimcha eslatmalar...'
            }),
        }


class LeadStatusForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Status o\'zgarishi haqida eslatma...'
            }),
        }


class TrialLessonForm(forms.ModelForm):
    class Meta:
        model = TrialLesson
        fields = ['group', 'date', 'time', 'room']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time'
            }),
            'room': forms.Select(attrs={'class': 'form-select'}),
        }


class TrialResultForm(forms.ModelForm):
    class Meta:
        model = TrialLesson
        fields = ['result', 'notes']
        widgets = {
            'result': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Sinov natijasi haqida eslatma...'
            }),
        }


class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ['due_date', 'notes']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Follow-up haqida eslatma...'
            }),
        }


class ExcelImportForm(forms.Form):
    file = forms.FileField(
        label='Excel fayl',
        widget=forms.FileInput(attrs={
            'class': 'form-file',
            'type': 'file',
            'accept': '.xlsx,.xls'
        })
    )


# User Management Forms
class UserCreateForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+998901234567',
            'type': 'tel'
        })
    )
    telegram_chat_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Telegram chat ID'
        })
    )
    is_active_sales = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'phone', 'telegram_chat_id', 'is_active_sales', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'type': 'email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
        }


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'phone', 'telegram_chat_id', 'is_active_sales', 'is_active',
                  'work_start_time', 'work_end_time', 'work_monday', 'work_tuesday', 'work_wednesday', 
                  'work_thursday', 'work_friday', 'work_saturday', 'work_sunday']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'type': 'email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'type': 'tel'}),
            'telegram_chat_id': forms.TextInput(attrs={'class': 'form-input'}),
            'is_active_sales': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'work_start_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'work_end_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'work_monday': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'work_tuesday': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'work_wednesday': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'work_thursday': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'work_friday': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'work_saturday': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'work_sunday': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
        }


# Course Management Forms
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'price', 'sales_script', 'duration_minutes', 'lessons_per_week', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Kurs nomi'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Narx (so\'m)'}),
            'sales_script': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 6,
                'placeholder': 'Sotuv scripti va bonus eslatmalar...'
            }),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Dars davomiyligi (daqiqa)'}),
            'lessons_per_week': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Haftasiga darslar soni'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


# Room Management Forms
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'capacity', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Xona nomi'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Sig\'im'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


# Group Management Forms
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['course', 'name', 'days', 'time', 'room', 'capacity', 'is_active']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Guruh nomi'}),
            'days': forms.Select(attrs={'class': 'form-select'}),
            'time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'room': forms.Select(attrs={'class': 'form-select'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Sig\'im'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


# Leave Request Forms
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'start_time', 'end_time', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'placeholder': 'Boshlanish sanasi'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'placeholder': 'Tugash sanasi'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time',
                'placeholder': 'Boshlanish vaqti (ixtiyoriy)'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time',
                'placeholder': 'Tugash vaqti (ixtiyoriy)'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Ruxsat sababi...'
            }),
        }


class LeaveRequestApprovalForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['status', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'rejection_reason': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Rad etish sababi (agar rad etilsa)...'
            }),
        }


class SalesAbsenceForm(forms.ModelForm):
    """Manager tomonidan sotuvchini ishda emasligini belgilash"""
    class Meta:
        model = User
        fields = ['is_absent', 'absent_reason', 'absent_from', 'absent_until']
        widgets = {
            'is_absent': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'absent_reason': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Ishda emaslik sababi...'
            }),
            'absent_from': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local',
                'placeholder': 'Boshlanish vaqti'
            }),
            'absent_until': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local',
                'placeholder': 'Tugash vaqti'
            }),
        }


# Sales Message Forms
class SalesMessageForm(forms.ModelForm):
    class Meta:
        model = SalesMessage
        fields = ['recipients', 'subject', 'message', 'priority']
        widgets = {
            'recipients': forms.CheckboxSelectMultiple(attrs={
                'class': 'space-y-2'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Xabar mavzusi...'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 6,
                'placeholder': 'Xabar matni...'
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Faqat faol sotuvchilarni ko'rsatish
        self.fields['recipients'].queryset = User.objects.filter(
            role='sales',
            is_active_sales=True
        ).order_by('username')
        self.fields['recipients'].label = "Qabul qiluvchilar"

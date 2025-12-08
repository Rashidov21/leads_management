from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Lead, Course, Group, TrialLesson, User, FollowUp, Room, LeaveRequest, SalesMessage, Offer


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'phone', 'secondary_phone', 'interested_course', 'source', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'placeholder': 'Ismni kiriting'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'placeholder': '+998901234567',
                'type': 'tel'
            }),
            'secondary_phone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'placeholder': 'Qo\'shimcha raqam (ixtiyoriy)',
                'type': 'tel'
            }),
            'interested_course': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 appearance-none bg-no-repeat bg-right-2.5 bg-[length:1.5em_1.5em]'
            }),
            'source': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 appearance-none bg-no-repeat bg-right-2.5 bg-[length:1.5em_1.5em]'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 resize-y min-h-[100px] placeholder:text-gray-400',
                'rows': 4,
                'placeholder': 'Qo\'shimcha eslatmalar...'
            }),
        }


class LeadStatusForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 appearance-none bg-no-repeat bg-right-2.5 bg-[length:1.5em_1.5em]'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 resize-y min-h-[100px] placeholder:text-gray-400',
                'rows': 4,
                'placeholder': 'Status o\'zgarishi haqida eslatma...'
            }),
        }


class TrialLessonForm(forms.ModelForm):
    class Meta:
        model = TrialLesson
        fields = ['group', 'date', 'time', 'room']
        widgets = {
            'group': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 appearance-none bg-no-repeat bg-right-2.5 bg-[length:1.5em_1.5em]'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200',
                'type': 'date'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200',
                'type': 'time'
            }),
            'room': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 appearance-none bg-no-repeat bg-right-2.5 bg-[length:1.5em_1.5em]'
            }),
        }


class TrialResultForm(forms.ModelForm):
    class Meta:
        model = TrialLesson
        fields = ['result', 'notes']
        widgets = {
            'result': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 appearance-none bg-no-repeat bg-right-2.5 bg-[length:1.5em_1.5em]'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 resize-y min-h-[100px] placeholder:text-gray-400',
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
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200',
                'type': 'datetime-local'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 resize-y min-h-[100px] placeholder:text-gray-400',
                'rows': 4,
                'placeholder': 'Follow-up haqida eslatma...'
            }),
        }


class ExcelImportForm(forms.Form):
    file = forms.FileField(
        label='Excel fayl',
        widget=forms.FileInput(attrs={
            'class': 'form-file block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 file:mr-4 file:py-2 file:px-4 file:rounded-l-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-600 file:text-white hover:file:bg-indigo-700',
            'type': 'file',
            'accept': '.xlsx,.xls'
        })
    )


# User Management Forms
class UserCreateForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 appearance-none bg-no-repeat bg-right-2.5 bg-[length:1.5em_1.5em]'
        }),
        required=True
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
            'placeholder': '+998901234567',
            'type': 'tel'
        })
    )
    telegram_chat_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
            'placeholder': 'Telegram chat ID'
        })
    )
    telegram_group_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
            'placeholder': 'Telegram guruh ID (statistika uchun)'
        })
    )
    is_active_sales = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'phone', 'telegram_chat_id', 'telegram_group_id', 'is_active_sales', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'type': 'email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400'
            }),
        }


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'phone', 'telegram_chat_id', 'telegram_group_id', 'is_active_sales', 'is_active',
                  'work_start_time', 'work_end_time', 'work_monday', 'work_tuesday', 'work_wednesday', 
                  'work_thursday', 'work_friday', 'work_saturday', 'work_sunday']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'type': 'email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 appearance-none bg-no-repeat bg-right-2.5 bg-[length:1.5em_1.5em]'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'type': 'tel'
            }),
            'telegram_chat_id': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400'
            }),
            'telegram_group_id': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400'
            }),
            'is_active_sales': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
            }),
            'work_start_time': forms.TimeInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200',
                'type': 'time'
            }),
            'work_end_time': forms.TimeInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200',
                'type': 'time'
            }),
            'work_monday': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
            }),
            'work_tuesday': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
            }),
            'work_wednesday': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
            }),
            'work_thursday': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
            }),
            'work_friday': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
            }),
            'work_saturday': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
            }),
            'work_sunday': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
            }),
        }


# Course Management Forms
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'price', 'sales_script', 'duration_minutes', 'lessons_per_week', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'placeholder': 'Kurs nomi'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'placeholder': 'Narx (so\'m)'
            }),
            'sales_script': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 resize-y min-h-[150px] placeholder:text-gray-400',
                'rows': 6,
                'placeholder': 'Sotuv scripti va bonus eslatmalar...'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'placeholder': 'Dars davomiyligi (daqiqa)'
            }),
            'lessons_per_week': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'placeholder': 'Haftasiga darslar soni'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
            }),
        }


# Room Management Forms
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'capacity', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'placeholder': 'Xona nomi'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'placeholder': 'Sig\'im'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
            }),
        }


# Group Management Forms
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['course', 'name', 'days', 'time', 'room', 'capacity', 'is_active']
        widgets = {
            'course': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 appearance-none bg-no-repeat bg-right-2.5 bg-[length:1.5em_1.5em]'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'placeholder': 'Guruh nomi'
            }),
            'days': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 appearance-none bg-no-repeat bg-right-2.5 bg-[length:1.5em_1.5em]'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200',
                'type': 'time'
            }),
            'room': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 appearance-none bg-no-repeat bg-right-2.5 bg-[length:1.5em_1.5em]'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'placeholder': 'Sig\'im'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
            }),
        }


# Leave Request Forms
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'start_time', 'end_time', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200',
                'type': 'date',
                'placeholder': 'Boshlanish sanasi'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200',
                'type': 'date',
                'placeholder': 'Tugash sanasi'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200',
                'type': 'time',
                'placeholder': 'Boshlanish vaqti (ixtiyoriy)'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200',
                'type': 'time',
                'placeholder': 'Tugash vaqti (ixtiyoriy)'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 resize-y min-h-[100px] placeholder:text-gray-400',
                'rows': 4,
                'placeholder': 'Ruxsat sababi...'
            }),
        }


class LeaveRequestApprovalForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['status', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 appearance-none bg-no-repeat bg-right-2.5 bg-[length:1.5em_1.5em]'
            }),
            'rejection_reason': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 resize-y min-h-[80px] placeholder:text-gray-400',
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
            'is_absent': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded transition-all duration-200 cursor-pointer'
            }),
            'absent_reason': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 resize-y min-h-[80px] placeholder:text-gray-400',
                'rows': 3,
                'placeholder': 'Ishda emaslik sababi...'
            }),
            'absent_from': forms.DateTimeInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200',
                'type': 'datetime-local',
                'placeholder': 'Boshlanish vaqti'
            }),
            'absent_until': forms.DateTimeInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200',
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
                'class': 'space-y-2 max-h-60 overflow-y-auto p-3 border border-gray-200 rounded-lg bg-gray-50'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400',
                'placeholder': 'Xabar mavzusi...'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 resize-y min-h-[150px] placeholder:text-gray-400',
                'rows': 6,
                'placeholder': 'Xabar matni...'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2.5 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 appearance-none bg-no-repeat bg-right-2.5 bg-[length:1.5em_1.5em]'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Faqat faol sotuvchilarni ko'rsatish
        self.fields['recipients'].queryset = User.objects.filter(
            role='sales',
            is_active_sales=True
        ).order_by('username')
        self.fields['recipients'].label = "Qabul qiluvchilar"


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = [
            'title', 'description', 'offer_type', 'course',
            'valid_from', 'valid_until', 'is_active',
            'channel', 'audience', 'priority'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'offer_type': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'valid_from': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'audience': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'channel': forms.Select(attrs={'class': 'form-select'}),
        }

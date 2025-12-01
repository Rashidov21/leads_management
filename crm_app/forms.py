from django import forms
from .models import Lead, Course, Group, TrialLesson, User, FollowUp


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'phone', 'interested_course', 'source', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'interested_course': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class LeadStatusForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class TrialLessonForm(forms.ModelForm):
    class Meta:
        model = TrialLesson
        fields = ['group', 'date', 'time', 'room']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'room': forms.Select(attrs={'class': 'form-select'}),
        }


class TrialResultForm(forms.ModelForm):
    class Meta:
        model = TrialLesson
        fields = ['result', 'notes']
        widgets = {
            'result': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ['due_date', 'notes']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class ExcelImportForm(forms.Form):
    file = forms.FileField(label='Excel fayl', widget=forms.FileInput(attrs={'class': 'form-input', 'type': 'file', 'accept': '.xlsx,.xls'}))


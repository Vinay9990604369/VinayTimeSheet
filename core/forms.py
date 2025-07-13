from django import forms
from .models import TimesheetEntry

class TimesheetEntryForm(forms.ModelForm):
    class Meta:
        model = TimesheetEntry
        fields = [
            'client_name', 'client_id',
            'project_name', 'project_id',
            'service_provider', 'service_type',
            'phase', 'billing_consultant',
            'date_of_service', 'billing_time',
            'description', 'comments',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'comments': forms.Textarea(attrs={'rows': 2}),
            'date_of_service': forms.DateInput(attrs={'type': 'date'}),
            'billing_time': forms.TimeInput(attrs={'type': 'time'}),
        }

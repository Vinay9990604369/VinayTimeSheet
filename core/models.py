from django import forms
from .models import TimesheetEntry, CustomUser, Client, Project

class TimesheetEntryForm(forms.ModelForm):
    class Meta:
        model = TimesheetEntry
        fields = [
            # Show all fields but some will be readonly in the form
            'client',
            'project',
            'service_provider',
            'service_type',
            'phase',
            'billing_consultant',
            'date_of_service',
            'last_updated',
            'billing_time_duration',
            'work_description',
            'comments',
        ]
        widgets = {
            'client': forms.TextInput(attrs={'readonly': 'readonly'}),
            'project': forms.TextInput(attrs={'readonly': 'readonly'}),
            'service_provider': forms.TextInput(attrs={'readonly': 'readonly'}),
            'service_type': forms.TextInput(attrs={'readonly': 'readonly'}),
            'phase': forms.TextInput(attrs={'readonly': 'readonly'}),
            'billing_consultant': forms.TextInput(attrs={'readonly': 'readonly'}),
            'date_of_service': forms.DateInput(attrs={'readonly': 'readonly', 'type': 'date'}),
            'last_updated': forms.DateTimeInput(attrs={'readonly': 'readonly', 'type': 'datetime'}),
            'billing_time_duration': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'work_description': forms.Textarea(attrs={'rows': 3}),
            'comments': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable the readonly fields so user cannot change them
        readonly_fields = [
            'client', 'project', 'service_provider', 'service_type',
            'phase', 'billing_consultant', 'date_of_service', 'last_updated'
        ]
        for field_name in readonly_fields:
            if field_name in self.fields:
                self.fields[field_name].disabled = True

        # Limit billing_consultant queryset to users with role 'CONSULTANT' if editable (probably not editable here)
        if 'billing_consultant' in self.fields:
            self.fields['billing_consultant'].queryset = CustomUser.objects.filter(role='CONSULTANT')


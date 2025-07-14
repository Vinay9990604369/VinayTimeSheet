from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import TimesheetEntry, CustomUser, Client


class TimesheetEntryForm(forms.ModelForm):
    # Read-only fields derived from related models
    client_id = forms.CharField(label="Client ID", required=False, disabled=True)
    project_id = forms.CharField(label="Project ID", required=False, disabled=True)
    service_provider = forms.CharField(label="Service Provider", required=False, disabled=True)
    service_type = forms.CharField(label="Service Type", required=False, disabled=True)
    last_updated = forms.DateTimeField(label="Last Updated", required=False, disabled=True)

    class Meta:
        model = TimesheetEntry
        fields = [
            'client',
            'client_id',
            'project',
            'project_id',
            'service_provider',
            'service_type',
            'phase',
            'billing_consultant',
            'date_of_service',
            'billing_time_duration',
            'work_description',
            'comments',
            'last_updated',
        ]

        widgets = {
            'client': forms.TextInput(attrs={'readonly': 'readonly'}),
            'project': forms.TextInput(attrs={'readonly': 'readonly'}),
            'phase': forms.Select(attrs={'disabled': True}),
            'billing_consultant': forms.TextInput(attrs={'readonly': 'readonly'}),
            'date_of_service': forms.DateInput(attrs={'type': 'date', 'readonly': 'readonly'}),
            'billing_time_duration': forms.TimeInput(attrs={'type': 'time'}),
            'work_description': forms.Textarea(attrs={'rows': 3}),
            'comments': forms.Textarea(attrs={'rows': 2}),
            'last_updated': forms.DateTimeInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            # Populate read-only virtual fields from relationships
            self.fields['client_id'].initial = self.instance.client.client_id
            self.fields['project_id'].initial = self.instance.project.project_id
            self.fields['service_provider'].initial = self.instance.project.service_provider
            self.fields['service_type'].initial = self.instance.project.service_type
            self.fields['last_updated'].initial = self.instance.last_updated

        # Disable all read-only fields
        readonly_fields = [
            'client', 'client_id', 'project', 'project_id',
            'service_provider', 'service_type', 'phase',
            'billing_consultant', 'date_of_service', 'last_updated'
        ]
        for field in readonly_fields:
            self.fields[field].disabled = True

        # Filter consultants in billing_consultant dropdown (useful in admin panel)
        self.fields['billing_consultant'].queryset = CustomUser.objects.filter(role='CONSULTANT')


class CustomUserCreationForm(UserCreationForm):
    clients = forms.ModelMultipleChoiceField(
        queryset=Client.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select client(s) associated with this client user."
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'clients')

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        clients = cleaned_data.get('clients')
        if role == 'CLIENT' and not clients:
            raise forms.ValidationError("Client users must be associated with at least one client.")
        if role != 'CLIENT' and clients:
            raise forms.ValidationError("Only client users can be associated with clients.")
        return cleaned_data


class CustomUserChangeForm(UserChangeForm):
    clients = forms.ModelMultipleChoiceField(
        queryset=Client.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select client(s) associated with this client user."
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'clients')

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        clients = cleaned_data.get('clients')
        if role == 'CLIENT' and not clients:
            raise forms.ValidationError("Client users must be associated with at least one client.")
        if role != 'CLIENT' and clients:
            raise forms.ValidationError("Only client users can be associated with clients.")
        return cleaned_data

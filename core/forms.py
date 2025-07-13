from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import TimesheetEntry, CustomUser, Client

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

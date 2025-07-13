from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import TimesheetEntry, CustomUser, Client


class TimesheetEntryForm(forms.ModelForm):
    class Meta:
        model = TimesheetEntry
        fields = [
            'client',
            'project_name', 'project_id',
            'service_type', 'phase', 'task_id',
            'billing_consultant',
            'date_of_service', 'duration',
            'description', 'remarks',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
            'date_of_service': forms.DateInput(attrs={'type': 'date'}),
            'duration': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter consultants in billing_consultant dropdown
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

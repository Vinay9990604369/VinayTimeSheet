from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.core.exceptions import ValidationError

from .models import CustomUser, Client, Project, TimesheetEntry

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'clients', 'password')

    clients = forms.ModelMultipleChoiceField(
        queryset=Client.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple('Clients', is_stacked=False)
    )

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        clients = cleaned_data.get('clients')

        if role == 'CLIENT' and (not clients or clients.count() == 0):
            raise ValidationError("Client users must be associated with at least one client.")
        if role != 'CLIENT' and clients:
            raise ValidationError("Only client users can be associated with clients.")
        return cleaned_data


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'clients', 'is_active', 'is_staff')

    clients = forms.ModelMultipleChoiceField(
        queryset=Client.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple('Clients', is_stacked=False)
    )

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        clients = cleaned_data.get('clients')

        if role == 'CLIENT' and (not clients or clients.count() == 0):
            raise ValidationError("Client users must be associated with at least one client.")
        if role != 'CLIENT' and clients:
            raise ValidationError("Only client users can be associated with clients.")
        return cleaned_data


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            return fieldsets + (
                (None, {'fields': ('role', 'clients')}),
            )
        if obj.role == 'CLIENT':
            return fieldsets + (
                (None, {'fields': ('role', 'clients')}),
            )
        else:
            return fieldsets + (
                (None, {'fields': ('role',)}),
            )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is not None:
            if obj.role == 'CLIENT':
                form.base_fields['clients'].queryset = Client.objects.all()
                form.base_fields['clients'].required = True
            else:
                form.base_fields.pop('clients', None)
        return form


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'address']
    search_fields = ['company_name']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'client', 'project_id']
    list_filter = ['client']
    search_fields = ['name', 'project_id']


class TimesheetEntryAdminForm(forms.ModelForm):
    class Meta:
        model = TimesheetEntry
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        # Add any additional validation here if needed
        return cleaned_data


@admin.register(TimesheetEntry)
class TimesheetEntryAdmin(admin.ModelAdmin):
    form = TimesheetEntryAdminForm

    list_display = [
        'client', 'project', 'service_provider', 'service_type',
        'phase', 'billing_consultant', 'date_of_service',
        'billing_time_duration', 'last_updated'
    ]
    list_filter = ['client', 'project', 'billing_consultant', 'date_of_service']
    search_fields = ['client__company_name', 'project__name', 'service_provider']

    readonly_fields = [
        'client', 'project', 'service_provider', 'service_type',
        'phase', 'billing_consultant', 'date_of_service', 'last_updated'
    ]

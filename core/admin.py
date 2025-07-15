from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.core.exceptions import ValidationError

from .models import CustomUser, Client, Project, TimesheetEntry


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'clients')

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


class CustomUserChangeForm(UserChangeForm):
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
    search_fields = ['username', 'email']
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Role', {'fields': ('role', 'clients')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'clients', 'password1', 'password2'),
        }),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'client_id', 'address']
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

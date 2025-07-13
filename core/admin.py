from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.core.exceptions import ValidationError

from .models import CustomUser, Client

class CustomUserCreationForm(forms.ModelForm):
    """
    Custom form for creating users that require
    client association if role = CLIENT.
    """
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
        return cleaned_data


class CustomUserChangeForm(forms.ModelForm):
    """
    Custom form for changing users that require
    client association if role = CLIENT.
    """
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
        return cleaned_data


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']

    # Show 'clients' field only for users with role 'CLIENT'
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # If adding a new user
        if obj is None:
            return fieldsets + (
                (None, {'fields': ('role', 'clients')}),
            )
        # For existing user
        if obj.role == 'CLIENT':
            return fieldsets + (
                (None, {'fields': ('role', 'clients')}),
            )
        else:
            # Exclude clients for other roles
            return fieldsets + (
                (None, {'fields': ('role',)}),
            )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Limit clients field visibility based on role in form
        if obj is not None:
            if obj.role == 'CLIENT':
                form.base_fields['clients'].queryset = Client.objects.all()
                form.base_fields['clients'].required = True
            else:
                # Remove clients field for non-client users
                form.base_fields.pop('clients', None)
        else:
            # For new user, clients required only if role = CLIENT
            # This is handled in the clean() method of forms

            pass

        return form


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'address']
    search_fields = ['company_name']

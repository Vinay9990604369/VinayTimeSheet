# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    # Login and Logout URLs
    path('', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:login'), name='logout'),

    # Redirect after login to route users based on role
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),

    # Dashboard URLs for different user roles
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('consultant/dashboard/', views.consultant_dashboard, name='consultant_dashboard'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),

    # Timesheet Entry URLs
    path('timesheet-entry/', views.timesheet_entry, name='timesheet_entry'),
    # Removed timesheet_entry_edit as it’s not handled differently in your current view
    # path('timesheet-entry/<int:entry_id>/', views.timesheet_entry, name='timesheet_entry_edit'),
]

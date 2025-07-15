# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication URLs
    path('', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:login'), name='logout'),

    # Redirect users after login based on their role
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),

    # Dashboards for user roles
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('consultant/dashboard/', views.consultant_dashboard, name='consultant_dashboard'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),

    # Timesheet Entry
    path('timesheet-entry/', views.timesheet_entry, name='timesheet_entry'),

    # ✅ Add this line to support edit links in the consultant dashboard
    path('timesheet-entry/edit/<int:entry_id>/', views.timesheet_entry_edit, name='timesheet_entry_edit'),
]

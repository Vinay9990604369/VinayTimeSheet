from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:login'), name='logout'),

    # Dashboards
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('consultant/dashboard/', views.consultant_dashboard, name='consultant_dashboard'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),

    # Timesheet Entry
    path('timesheet-entry/', views.timesheet_entry, name='timesheet_entry'),
    path('timesheet-entry/<int:entry_id>/', views.timesheet_entry, name='timesheet_entry_edit'),
]

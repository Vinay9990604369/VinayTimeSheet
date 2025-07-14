from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.login_view, name='login'),  # Login page
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('consultant/dashboard/', views.consultant_dashboard, name='consultant_dashboard'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),

    # Timesheet Entry
    path('timesheet-entry/', views.timesheet_entry, name='timesheet_entry'),
    path('timesheet-entry/<int:entry_id>/', views.timesheet_entry, name='timesheet_entry_edit'),
]

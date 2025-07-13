from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),  # Default route
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('consultant-dashboard/', views.consultant_dashboard, name='consultant_dashboard'),
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),

    # Timesheet Entry
    path('timesheet-entry/', views.timesheet_entry, name='timesheet_entry'),
]

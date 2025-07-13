from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('consultant-dashboard/', views.consultant_dashboard, name='consultant_dashboard'),
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),  # 👈 This makes the home page go to login
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('consultant-dashboard/', views.consultant_dashboard, name='consultant_dashboard'),
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),
    path('timesheet-entry/', views.timesheet_entry, name='timesheet_entry'),
]

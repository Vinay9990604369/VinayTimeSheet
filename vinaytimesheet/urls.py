# vinaytimesheet/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include core app URLs with namespace
    path('', include('core.urls', namespace='core')),
]

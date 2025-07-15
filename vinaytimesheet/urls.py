# vinaytimesheet/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin Site
    path('admin/', admin.site.urls),

    # Include core app URLs under the root URL
    path('', include('core.urls', namespace='core')),
]

# vinaytimesheet/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin site
    path('admin/', admin.site.urls),

    # Include URLs from the core app with namespace 'core'
    path('', include('core.urls', namespace='core')),
]

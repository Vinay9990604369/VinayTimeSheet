from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include core app URLs at root
    path('', include('core.urls', namespace='core')),
]

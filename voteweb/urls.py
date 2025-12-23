from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls), # Using custom /root
    path('', include('core.urls')),
]

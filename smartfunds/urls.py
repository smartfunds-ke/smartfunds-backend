
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('console/', admin.site.urls),
    path('api/', include('api.urls')),
]

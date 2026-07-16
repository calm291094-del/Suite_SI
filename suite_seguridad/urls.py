"""
URLs raíz del proyecto.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # PRIMERO: URLs de la aplicación core
    # (Django evalúa en orden, la primera que haga match gana)
    path('', include('core.urls')),
    
    # SEGUNDO: Panel de administración de Django (solo root)
    # Solo llega aquí si core.urls no hizo match
    path('django-admin/', admin.site.urls),
]

# Servir archivos multimedia en modo desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
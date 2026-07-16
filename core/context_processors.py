"""
Procesadores de contexto: inyectan variables en todos los templates.
"""

from django.utils import timezone
from datetime import timedelta


def notificaciones_no_leidas(request):
    """Badge de notificaciones en la navbar."""
    if request.user.is_authenticated and hasattr(request.user, 'perfil'):
        from .models import Notificacion
        count = Notificacion.objects.filter(destinatario=request.user, leida=False).count()
        return {'notifs_count': count}
    return {'notifs_count': 0}


def dias_expiracion_password(request):
    """Calcula los días restantes para la expiración de contraseña
    y lo inyecta en el contexto como 'password_dias_restantes'.
    Se usa en base.html para mostrar el banner de aviso."""
    if request.user.is_authenticated and hasattr(request.user, 'perfil'):
        perfil = request.user.perfil
        if (perfil.fecha_ultimo_cambio_password 
            and perfil.dias_expiracion_password > 0
            and perfil.rol != 'root'):
            delta = (perfil.fecha_ultimo_cambio_password + 
                     timedelta(days=perfil.dias_expiracion_password) - timezone.now())
            return {'password_dias_restantes': delta.days}
    return {'password_dias_restantes': None}
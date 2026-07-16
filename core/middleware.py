"""
Middleware de expiración de contraseñas.
Se ejecuta en CADA request para verificar si la contraseña del usuario
ha expirado. Si expiró, redirige forzosamente a cambiar contraseña.
Solo se excluyen las URLs de cambio de contraseña, login y logout.
"""

from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages

# URLs que NO deben ser interceptadas por el middleware
RUTAS_EXCLUIDAS = [
    '/cambiar-password/',
    '/login/',
    '/logout/',
    '/verificar-2fa/',
    '/setup-2fa/',
]


class PasswordExpiryMiddleware:
    """Middleware que forza el cambio de contraseña cuando expira."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo verificar si el usuario está autenticado
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Root nunca expira
        if hasattr(request.user, 'perfil') and request.user.perfil.rol == 'root':
            return self.get_response(request)

        # No interceptar rutas excluidas (evita loop infinito)
        if request.path in RUTAS_EXCLUIDAS:
            return self.get_response(request)

        perfil = request.user.perfil

        # Verificar si tiene expiración configurada
        if not perfil.fecha_ultimo_cambio_password or perfil.dias_expiracion_password == 0:
            return self.get_response(request)

        # Calcular fecha de vencimiento
        from datetime import timedelta
        vencimiento = perfil.fecha_ultimo_cambio_password + timedelta(
            days=perfil.dias_expiracion_password
        )

        if timezone.now() > vencimiento:
            messages.warning(
                request,
                f'Su contraseña ha expirado (hace {perfil.dias_expiracion_password} días). '
                'Debe cambiarla para continuar usando el sistema.'
            )
            return redirect('cambiar_password')

        return self.get_response(request)
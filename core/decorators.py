"""
Decoradores personalizados para proteger vistas.
Reemplazan a @login_required y @permission_required con lógica
basada en los roles personalizados del sistema.
También protege las URLs contra acceso directo sin autenticación.
"""

from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib import messages


def login_requerido(view_func):
    """Decorador que exige que el usuario esté autenticado.
    Si no lo está, redirige al login con un mensaje de error.
    Úsalo en TODAS las vistas que requieran estar logueado."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debe iniciar sesión para acceder a esta página.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_requerido(view_func):
    """Decorador que exige rol de administrador.
    Los roles con permisos administrativos son: root, admin_red, seguridad.
    Los usuarios normales reciben un error 403 Forbidden."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debe iniciar sesión para acceder.')
            return redirect('login')
        # Verificar que el perfil tenga rol de admin
        if not hasattr(request.user, 'perfil'):
            messages.error(request, 'Su cuenta no tiene perfil configurado.')
            return redirect('login')
        if request.user.perfil.rol not in ['root', 'admin_red', 'seguridad']:
            return HttpResponseForbidden(
                'No tiene permisos de administrador para acceder a esta sección. '
                'Contacte al administrador del sistema si cree que esto es un error.'
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def root_requerido(view_func):
    """Decorador que exige rol root (super administrador).
    Solo el usuario root puede acceder a estas vistas.
    Útil para operaciones críticas del sistema."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'perfil') or request.user.perfil.rol != 'root':
            return HttpResponseForbidden(
                'Solo el super administrador (Root) tiene acceso a esta sección.'
            )
        return view_func(request, *args, **kwargs)
    return wrapper
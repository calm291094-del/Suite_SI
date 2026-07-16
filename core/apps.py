"""
Configuración de la aplicación 'core'.
Incluye la señal para crear automáticamente el perfil cuando se crea un usuario.
"""

from django.apps import AppConfig

class CoreConfig(AppConfig):
    """Configuración principal de la app core."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Se ejecuta cuando la aplicación está lista.
        Importamos las señales para que se registren automáticamente."""
        import core.signals
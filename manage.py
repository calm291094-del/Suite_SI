#!/usr/bin/env python
"""Punto de entrada para ejecutar comandos de Django.
Ejecutar: python manage.py runserver
"""

# =============================================================================
# Importar las librerias necesarias para el proyecto
# =============================================================================
import os
import sys
import mimetypes

# =============================================================================
# Configuración MIME para utilizar las fuentes e iconos locales sin depender de internet
# =============================================================================
mimetypes.add_type('font/woff2', '.woff2')
mimetypes.add_type('font/woff', '.woff')
mimetypes.add_type('font/ttf', '.ttf')

# =============================================================================
# FUNCIONES
# =============================================================================
def main():
    """Configura y ejecuta el servidor de desarrollo de Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suite_seguridad.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Está instalado?"
        ) from exc
    execute_from_command_line(sys.argv)

# =============================================================================
# Main
# =============================================================================
if __name__ == '__main__':
    main()
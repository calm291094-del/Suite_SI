"""
Configuración WSGI para servir la aplicación en producción.
Usado por servidores como Gunicorn u Apache mod_wsgi.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suite_seguridad.settings')
application = get_wsgi_application()
"""
═══════════════════════════════════════════════════════════════════════════
  Configuración principal del proyecto Suite de Seguridad Informática.
═══════════════════════════════════════════════════════════════════════════
  Define todas las settings necesarias para que Django funcione:
  
  1. Conexión a base de datos
  2. Aplicaciones instaladas (apps)
  3. Middleware (filtros que procesan cada petición HTTP)
  4. Plantillas (templates HTML)
  5. Archivos estáticos (CSS, JS, imágenes)
  6. Autenticación personalizada
  7. Seguridad (CSRF, cookies, cabeceras HTTP)
  
  FLUJO DE UNA PETICIÓN EN DJANGO:
  Navegador → Middleware → URLconf → Vista → Template → Respuesta HTTP
  
═══════════════════════════════════════════════════════════════════════════
"""

import os
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════
# RUTAS DEL PROYECTO
# ══════════════════════════════════════════════════════════════════════════
# BASE_DIR: Ruta absoluta de la carpeta que contiene a settings.py
# Ejemplo: d:\Karlos\Python\Suite_SI
# Path(__file__) = ".../suite_seguridad/settings.py"
# .resolve()    = convierte a ruta absoluta sin symlinks
# .parent       = sube a ".../suite_seguridad/"
# .parent       = sube a ".../Suite_SI/"  ← esta es BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# ══════════════════════════════════════════════════════════════════════════
# SEGURIDAD BÁSICA
# ══════════════════════════════════════════════════════════════════════════
# SECRET_KEY: Clave criptográfica que Django usa para:
#   - Firmar las cookies de sesión (para que no puedan ser falsificadas)
#   - Generar tokens CSRF (para evitar ataques de sitios cruzados)
#   - Cifrar datos sensibles internamente
# ⚠️ NUNCA subir esta clave a GitHub. En producción se lee desde
#    una variable de entorno (ej: os.environ.get('SECRET_KEY'))
SECRET_KEY = 'django-insecure-cambiar-esta-clave-en-produccion-4815162342-x'

# DEBUG: Modo de depuración
#   True  = Muestra trazas de errores detalladas en el navegador.
#           Muestra archivos estáticos automáticamente.
#           ¡¡¡NUNCA usar True en producción!!!
#   False = Muestra página 404/500 genérica. Requiere collectstatic.
#
# NOTA: Si DEBUG=False y no agregas tu dominio a ALLOWED_HOSTS,
#       Django devolverá error 400 (Bad Request) en todas las páginas.
DEBUG = True

# ALLOWED_HOSTS: Lista de dominios/IPs desde los cuales Django acepta peticiones.
#
#   - En desarrollo (DEBUG=True): ['*'] acepta todo (pero es inseguro).
#   - En producción (DEBUG=False): DEBE contener los dominios reales.
#
# Para tu red local con cyseg.kalm, cuando pases a producción sería:
#   ALLOWED_HOSTS = ['cyseg.kalm', '192.168.1.100']
#
# Por ahora con DEBUG=True, ['*'] funciona pero no es recomendable para red.
ALLOWED_HOSTS = ['*']

# ══════════════════════════════════════════════════════════════════════════
# APLICACIONES INSTALADAS
# ══════════════════════════════════════════════════════════════════════════

# INSTALLED_APPS: Registro de todas las apps que Django debe cargar al arrancar.
#
# Las de "django.contrib" son apps oficiales que proveen:
#   - admin      → Panel de administración automático
#   - auth       → Sistema de usuarios, contraseñas, grupos, permisos
#   - contenttypes → Sistema de tipos de contenido (ForeignKey genéricas)
#   - sessions   → Manejo de sesiones (datos del usuario entre páginas)
#   - messages   → Mensajes temporales (ej: "Contraseña cambiada con éxito")
#   - staticfiles → Comando collectstatic para juntar todos los CSS/JS
#
# Las de terceros y propias:
#   - widget_tweaks → Permite agregar clases CSS a los campos de formularios
#                      desde los templates con |add_class:"mi-clase"
#   - core          → Tu aplicación principal con toda la lógica del sistema
INSTALLED_APPS = [
    # --- Apps oficiales de Django ---
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # --- Apps de terceros ---
    'widget_tweaks',       # Permite personalizar widgets en templates
    # --- Apps propias del proyecto ---
    'core',                # Nuestra aplicación principal
]

# ══════════════════════════════════════════════════════════════════════════
# MIDDLEWARE (Capa intermedia de procesamiento)
# ══════════════════════════════════════════════════════════════════════════

# MIDDLEWARE: Lista de clases que se ejecutan EN ORDEN para cada petición HTTP
# y EN ORDEN INVERSO para cada respuesta. Funcionan como una "cadena":
#
#   REQUEST:  Browser → SecurityMiddleware → SessionMiddleware → ... → Vista
#   RESPONSE: Vista → ... → SessionMiddleware → SecurityMiddleware → Browser
#
# ¿Qué hace cada uno?
#
#   SecurityMiddleware       → Agrega cabeceras de seguridad HTTP
#                              (HSTS, X-Content-Type-Options, etc.)
#
#   SessionMiddleware        → Lee/guarda la sesión del usuario usando cookies.
#                              Es lo que permite que request.session funcione.
#
#   CommonMiddleware         → Normaliza URLs (agrega/barra final) y
#                              rechaza USER_AGENT desconocidos si se configura.
#
#   CsrfViewMiddleware       → Verifica el token CSRF en formularios POST.
#                              Impide que ataques externos envíen formularios
#                              a tu sitio desde otra página maliciosa.
#
#   AuthenticationMiddleware → Adjunta el usuario a request.user.
#                              Si no ha iniciado sesión → request.user = AnonymousUser.
#                              Si inició sesión → request.user = objeto User.
#
#   MessageMiddleware        → Maneja los mensajes flash entre redirecciones.
#                              Usa las cookies de mensajes para pasar datos
#                              de una vista a otra (ej: después de un POST).
#
#   XFrameOptionsMiddleware  → Agrega cabecera X-Frame-Options: DENY.
#                              Impide que tu sitio se cargue dentro de un <iframe>
#                              en otra página. Previene ataques de clickjacking.
#
#   PasswordExpiryMiddleware → (TU CUSTOM) Verifica si la contraseña del usuario
#                              ha expirado y redirige a cambiarla si es necesario.
#                              Se ejecuta DESPUÉS de AuthenticationMiddleware
#                              porque necesita acceder a request.user.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # --- Middleware personalizado del proyecto ---
    'core.middleware.PasswordExpiryMiddleware'
]

# ══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE URLs
# ══════════════════════════════════════════════════════════════════════════
# ROOT_URLCONF: Apunta al archivo donde Django debe buscar las URLs principales.
# Este archivo contiene el urlpatterns raíz que incluye las URLs de cada app.
ROOT_URLCONF = 'suite_seguridad.urls'

# ══════════════════════════════════════════════════════════════════════════
# PLANTILLAS (TEMPLATES HTML)
# ══════════════════════════════════════════════════════════════════════════
# TEMPLATES: Configuración del motor de plantillas de Django.
#
#   DIRS: Carpetas额外 (fuera de las apps) donde buscar archivos .html
#         Aquí apuntamos a la carpeta global "templates/" del proyecto.
#
#   APP_DIRS: Si es True, Django también busca templates dentro de
#             cada app en la subcarpeta "templates/" (ej: core/templates/).
#             Orden de búsqueda: DIRS primero, luego APP_DIRS.
#
#   context_processors: Funciones que inyectan variables automáticas
#                       en TODOS los templates sin que la vista las pase.
#
#     - debug          → Inyecta {{ debug }} (solo si DEBUG=True)
#     - request        → Inyecta {{ request }} (el objeto HTTP completo)
#     - auth           → Inyecta {{ user }} y {{ perms }} en todos los HTML
#     - messages       → Inyecta {{ messages }} para mostrar alertas
#
#     CUSTOM:
#     - notificaciones_no_leidas → Inyecta {{ notifs_count }} para el badge
#     - dias_expiracion_password → Inyecta {{ password_dias_restantes }}
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Carpeta de templates personalizados
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # --- Context processors oficiales ---
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # --- Context processors personalizados ---
                'core.context_processors.notificaciones_no_leidas',
                'core.context_processors.dias_expiracion_password',
            ],
        },
    },
]

# ══════════════════════════════════════════════════════════════════════════
# WSGI (Interfaz para servidor de producción)
# ══════════════════════════════════════════════════════════════════════════
# WSGI_APPLICATION: Apunta a la función WSGI que conecta Django con
# servidores web de producción como Apache+mod_wsgi, Gunicorn, etc.
#
# El runserver tiene su propio servidor interno y NO usa esto.
# Esto solo se usa cuando despliegas con un servidor real.
#
# Flujo en producción:
#   Navegador → Apache/Gunicorn → wsgi.application → Django
WSGI_APPLICATION = 'suite_seguridad.wsgi.application'

# ══════════════════════════════════════════════════════════════════════════
# BASE DE DATOS
# ══════════════════════════════════════════════════════════════════════════
# DATABASES: Configuración de conexión a la base de datos.
#
#   ENGINE: Tipo de base de datos.
#           - sqlite3   → Archivo local, sin servidor, ideal para desarrollo
#           - postgresql → Servidor PostgreSQL, ideal para producción
#           - mysql      → Servidor MySQL/MariaDB
#
#   NAME: Ruta al archivo de la BD (SQLite) o nombre de la BD (PostgreSQL).
#
# Para producción se recomienda PostgreSQL porque:
#   - Soporta múltiples conexiones simultáneas (SQLite no)
#   - Mejor rendimiento en consultas complejas
#   - No se corrompe si 2 procesos escriben al mismo tiempo
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        # ── Para PostgreSQL en producción, cambiar a: ──
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'suite_seguridad',
        # 'USER': 'postgres',
        # 'PASSWORD': 'tu_password_segura',
        # 'HOST': 'localhost',
        # 'PORT': '5432',
    }
}

# ══════════════════════════════════════════════════════════════════════════
# VALIDACIÓN DE CONTRASEÑAS
# ══════════════════════════════════════════════════════════════════════════
# AUTH_PASSWORD_VALIDATORS: Reglas que se aplican al crear/cambiar contraseñas.
#
#   UserAttributeSimilarityValidator
#       → Rechaza contraseñas muy parecidas al nombre, email o atributos del user.
#
#   MinimumLengthValidator (min_length=8)
#       → La contraseña debe tener al menos 8 caracteres.
#
#   CommonPasswordValidator
#       → Rechaza contraseñas demasiado comunes (ej: "password123", "admin").
#       Usa una lista interna de ~20,000 contraseñas frecuentes.
#
#   NumericPasswordValidator
#       → Rechaza contraseñas que sean solo números (ej: "12345678").
#
# NOTA: Estos validadores NO se aplican al login, solo al registro/cambio.
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ══════════════════════════════════════════════════════════════════════════
# INTERNACIONALIZACIÓN Y ZONA HORARIA
# ══════════════════════════════════════════════════════════════════════════
# LANGUAGE_CODE: Idioma por defecto para la interfaz de Django.
#                'es-es' = Español de España (mensajes del admin, errores, etc.)
#
# TIME_ZONE: Zona horaria para datetime.now(), timezone.now(), etc.
#            'America/Havana' = Hora de Cuba (UTC-5)
#            Todos los datetime se guardan en UTC en la BD y se
#            convierten a esta zona al mostrarlos.
#
# USE_I18N: Activa el sistema de internacionalización (traducciones).
#           Si True, Django traduce sus mensajes internos al idioma configurado.
#
# USE_TZ: Activa el soporte de zonas horarias (timezone-aware datetimes).
#         Si True, timezone.now() devuelve un datetime con zona horaria (UTC).
#         Si False, usa datetimes "naive" (sin zona) → NO recomendado.
LANGUAGE_CODE = 'es-es'       # Español de España
TIME_ZONE = 'America/Havana'  # Zona horaria de Cuba
USE_I18N = True
USE_TZ = True

# ══════════════════════════════════════════════════════════════════════════
# ARCHIVOS ESTÁTICOS (CSS, JS, fuentes, iconos)
# ══════════════════════════════════════════════════════════════════════════
# Los archivos estáticos son los que NO cambian por usuario:
# CSS (.css), JavaScript (.js), imágenes (.png, .ico), fuentes (.woff2).
#
# Existen 3 settings que configuran esto:
#
#   STATIC_URL: URL pública para acceder a los estáticos en el navegador.
#               Si es '/static/', entonces <link href="/static/css/main.css">
#               servirá el archivo desde static/css/main.css.
#
#   STATICFILES_DIRS: Carpetas donde Django busca estáticos DURANTE DESARROLLO.
#                     Aquí apuntamos a la carpeta "static/" del proyecto.
#                     El runserver usa esto para servir los archivos directamente.
#
#   STATIC_ROOT: Carpeta donde "collectstatic" COPIA todos los estáticos
#                para producción. Apache/Nginx apuntan a esta carpeta.
#                El runserver NO usa esto. Solo es para deploy.
#
# Flujo:
#   Desarrollo: Browser → /static/css/main.css → STATICFILES_DIRS → archivo
#   Producción: Browser → /static/css/main.css → Apache → STATIC_ROOT → archivo
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ══════════════════════════════════════════════════════════════════════════
# ARCHIVOS MULTIMEDIA (Documentos subidos por usuarios)
# ══════════════════════════════════════════════════════════════════════════
# A diferencia de los estáticos, los multimedia son subidos por usuarios:
# documentos, fotos de perfil, reportes generados, etc.
#
#   MEDIA_URL: URL pública (ej: /media/documentos/reporte.pdf).
#
#   MEDIA_ROOT: Carpeta física en el servidor donde se guardan los archivos.
#               Django NO crea esta carpeta automáticamente; debes crearla.
#
# IMPORTANTE: En producción, Apache/Nginx debe servir esta carpeta directamente
#             (NO pasar por Django) por rendimiento y seguridad.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ══════════════════════════════════════════════════════════════════════════
# CAMPOS AUTOGENERADOS
# ══════════════════════════════════════════════════════════════════════════
# DEFAULT_AUTO_FIELD: Tipo de campo que Django usa para los campos "id"
#                     cuando no lo especificas en un modelo.
#
#   BigAutoField    → Entero de 64 bits (hasta 9,223,372,036,854,775,807)
#   AutoField       → Entero de 32 bits (hasta 2,147,483,647)
#
# BigAutoField es el estándar desde Django 3.2. Usa BigInt para evitar
# problemas si la tabla crece mucho (logs, auditoría, etc.).
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ══════════════════════════════════════════════════════════════════════════
# AUTENTICACIÓN PERSONALIZADA
# ══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION_BACKENDS: Clases que verifican si un usuario puede iniciar sesión.
#
#   ModelBackend: Backend por defecto de Django.
#                 Verifica que username coincida Y que la contraseña (hasheada)
#                 coincida usando check_password().
#                 También verifica que el usuario esté activo (is_active=True).
#
#   Si quisieras login con email, crearías un backend custom que busque
#   por email en vez de username, y lo agregarías aquí.
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# LOGIN_URL: URL a la que se redirige cuando @login_required detecta
#            que el usuario no ha iniciado sesión.
#            Django usa reverse() internamente con este nombre de URL.
# LOGIN_REDIRECT_URL: URL a la que se redirige después de un login exitoso
#                     (cuando se usa la vista LoginView de Django).
# LOGOUT_REDIRECT_URL: URL a la que se redirige después de cerrar sesión.
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ══════════════════════════════════════════════════════════════════════════
# SEGURIDAD PARA PRODUCCIÓN (CUANDO DEBUG = FALSE)
# ══════════════════════════════════════════════════════════════════════════
#
# Estas configuraciones son INNECESARIAS con DEBUG=True porque:
#   - SecurityMiddleware las desactiva automáticamente en modo debug
#   - El runserver no es un servidor de producción
#
# DESCOMENTAR cuando vayas a desplegar con DEBUG=False.
#
# ── SECURE_SSL_REDIRECT ──
# Fuerza que TODA petición HTTP sea redirigida a HTTPS.
# Si alguien entra a http://cyseg.kalm → redirige a https://cyseg.kalm.
# ⚠️ Requiere que tengas un certificado SSL configurado en el servidor.
# SECURE_SSL_REDIRECT = True

# ── SESSION_COOKIE_SECURE ──
# La cookie de sesión solo se envía sobre HTTPS.
# Sin esto, alguien en la misma red podría interceptar la cookie
# si el usuario entra por HTTP en vez de HTTPS.
# SESSION_COOKIE_SECURE = True

# ── CSRF_COOKIE_SECURE ──
# Igual que arriba pero para la cookie del token CSRF.
# Sin esto, los formularios POST fallarían si la cookie se intercepta.
# CSRF_COOKIE_SECURE = True

# ── SECURE_BROWSER_XSS_FILTER ──
# Agrega cabecera X-XSS-Protection: 1; mode=block.
# Hace que los navegadores bloqueen intentos de inyección XSS detectados.
# (Es un respaldo; tu código ya debería escapar todo con |escape).
# SECURE_BROWSER_XSS_FILTER = True

# ── SECURE_CONTENT_TYPE_NOSNIFF ──
# Agrega cabecera X-Content-Type-Options: nosniff.
# Impide que el navegador "adivine" el tipo de archivo.
# Ej: Si un .html se sirve como text/plain, el navegador NO lo
#     interpretará como HTML (evita ataques de MIME sniffing).
# SECURE_CONTENT_TYPE_NOSNIFF = True

# ── X_FRAME_OPTIONS ──
# Controla si tu sitio puede cargarse dentro de un <iframe>.
#   DENY         → Nunca se puede embeber.
#   SAMEORIGIN   → Solo se puede embeber desde el mismo dominio.
#   ALLOW-FROM   → Solo desde un dominio específico (obsoleto).
# Ya está configurado por XFrameOptionsMiddleware, pero se puede
# sobreescribir aquí si necesitas cambiarlo.
# X_FRAME_OPTIONS = 'DENY'

# ── SECURE_HSTS_SECONDS (Avanzado) ──
# Tiempo en segundos que el navegador DEBE usar solo HTTPS.
# Una vez activado, NO se puede desactivar durante ese tiempo.
# 31536000 = 1 año. ⚠️ Solo para producción con SSL permanente.
# SECURE_HSTS_SECONDS = 31536000

# ── SECURE_HSTS_INCLUDE_SUBDOMAINS ──
# Aplica HSTS también a subdominios (ej: admin.cyseg.kalm).
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ── SECURE_HSTS_PRELOAD ──
# Permite que tu dominio se incluya en la lista HSTS preload del navegador.
# Una vez en esa lista, es MUY difícil quitarlo.
# SECURE_HSTS_PRELOAD = True
# 🛡️ Suite de Seguridad Informática

<div align="center">
  <img src="https://github.com/calm291094-del/Suite_SI/blob/main/Suite-Icon.png" alt="KrootCorp Logo" width="200">
  <br>
  <strong> Sistema integral de gestión de seguridad informática desarrollado con Django para entidades cubanas. Cumple con los marcos legales vigentes: Decreto-Ley 370/2019, Resoluciones 128/2019 y 129/2019 del MINCOM, y Decreto-Ley 38/2023 de Ciberseguridad. </strong>
  <br>
  <em>Inspirado en el desarrollo de actividades de la indole de SI.</em>
</div>

## ✨ Características

- 🔐 **Autenticación robusta**: 2FA (TOTP), bloqueo por intentos fallidos, expiración de contraseñas
- 📄 **Gestión documental**: repositorio de documentos con control de acceso por departamento
- 💬 **Chat interno**: comunicación en tiempo real con canales generales y privados
- 🖥️ **Inventario de hardware**: gestión de equipos y componentes con historial de cambios y alertas automáticas
- 👥 **Control de usuarios**: roles (usuario, admin_red, seguridad, root) con permisos granulares
- 📊 **Dashboard interactivo**: estadísticas, gráficos y acceso rápido a módulos
- 📋 **Base legal integrada**: normativa cubana de seguridad informática, efemérides y enlaces útiles
- 📝 **Módulo de capacitación**: cursos con evaluación automática (70% mínimo para aprobar)
- 📜 **Políticas de seguridad**: gestión con fechas de vencimiento y notificaciones
- 🎫 **Sistema de tickets**: soporte y seguimiento de incidencias
- 🔍 **Centro de IA**: análisis heurístico de seguridad con detección de anomalías
- 📈 **Auditoría**: registro completo de acciones (login, cambios, eliminaciones)
- 🗺️ **Mapa de red**: visualización topológica de equipos y departamentos

## 🏗️ Estructura del Proyecto
Suite_SI/
├── manage.py
├── requirements.txt
├── suite_seguridad/ # Configuración del proyecto
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
├── core/ # Aplicación principal
│ ├── models.py # Modelos: Usuario, Perfil, Equipo, Documento, etc.
│ ├── views.py # Todas las vistas del sistema
│ ├── forms.py # Formularios de Django
│ ├── decorators.py # Decoradores: @login_requerido, @admin_requerido
│ ├── middleware.py # Middleware de expiración de contraseña
│ ├── utils.py # Utilidades: PDF, notificaciones, auditoría
│ ├── signals.py # Señales para crear Perfil automáticamente
│ └── management/commands/ # Comandos personalizados
│ └── crear_root.py # Crea el superusuario root
├── templates/ # Plantillas HTML
│ ├── base.html # Plantilla base con navbar y sidebar
│ ├── home.html # Página pública
│ ├── dashboard.html # Panel principal
│ ├── login.html # Inicio de sesión
│ ├── register.html # Registro de usuarios
│ ├── documentos.html # Gestión de documentos
│ ├── chat.html # Chat interno
│ ├── admin_usuarios.html # Administración de usuarios
│ ├── admin_inventario.html # Inventario de equipos
│ └── ... # Resto de plantillas
├── static/ # Archivos estáticos
│ ├── css/main.css # Estilos completos (Cyberpunk/Glassmorphism)
│ ├── js/main.js # Funcionalidades principales
│ ├── js/auth.js # Lógica de autenticación y fortaleza de contraseña
│ ├── js/chat.js # Polling y gestión del chat
│ └── js/inventario.js # CRUD de componentes vía AJAX
└── media/ # Archivos subidos por usuarios (documentos)
└── documentos/

## 🚀 Instalación Local

### Requisitos
- Python 3.10 o superior
- pip (gestor de paquetes de Python)

### Pasos

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/Suite_SI.git
cd Suite_SI
```

2. Crear y activar un entorno virtual
```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
# o
venv\Scripts\activate      # Windows
```

3. Instalar dependencias
```bash
pip install -r requirements.txt
```

5. Configurar variables de entorno (opcional)
```bash
# En Linux/macOS
export SECRET_KEY="tu-clave-secreta-aqui"
# En Windows (CMD)
set SECRET_KEY="tu-clave-secreta-aqui"
```

5. Ejecutar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Crear el superusuario root
```bash
python manage.py crear_root
```
Este comando crea automáticamente un usuario root con rol root y configura su perfil.

7. Crear datos iniciales (departamentos)
```bash
python manage.py crear_datos_iniciales
```

8. Iniciar el servidor de desarrollo
```bash
python manage.py runserver
```

9. Acceder a la aplicación
```bash
    Abre tu navegador en http://127.0.0.1:8000
```

🛠️ Comandos útiles
# Crear superusuario root
```bash
python manage.py crear_root
```

# Crear datos iniciales (departamentos)
```bash
python manage.py crear_datos_iniciales
```

# Crear un curso de capacitación desde la consola
```bash
python manage.py shell -c "
from core.models import CursoCapacitacion
CursoCapacitacion.objects.create(
    titulo='Normativa de Seguridad Informática',
    descripcion='Evaluación sobre el DL 370/2019 y la Resolución 128/2019.',
    preguntas='[{\"p\": \"¿Qué Decreto-Ley es la norma marco?\", \"o\": [\"DL 35/2021\", \"DL 370/2019\"], \"r\": 1}]'
)
"
```

# Generar PDF del inventario (desde el navegador)
```bash
# Visita: /inventario/pdf/?departamento=1
```

# Ver logs en producción (Render)
# Desde el dashboard de Render → Logs

📚 Tecnologías utilizadas

    Backend: Django 4.2.7

    Base de datos: SQLite (desarrollo) / PostgreSQL (producción)

    Frontend: HTML5, CSS3 (Glassmorphism/Cyberpunk), JavaScript Vanilla

    Autenticación 2FA: pyotp + qrcode

    Generación de PDFs: reportlab

    Procesamiento de imágenes: Pillow

    Servidor de producción: Gunicorn

    Despliegue: Render.com

📋 Normativa legal implementada

    Decreto-Ley 370/2019 - Informatización de la Sociedad

    Resolución 128/2019 del MINCOM - Reglamento de Seguridad Informática

    Resolución 129/2019 del MINCOM - Medidas Técnicas de Seguridad

    Decreto-Ley 35/2021 - Telecomunicaciones

    Resolución 105/2020 del MIC - Normas Cubanas de Gestión de Seguridad

    Decreto-Ley 38/2023 - Ciberseguridad de la República de Cuba

👨‍💻 Autor

Carlos A. Lorenzo Marro - GitHub
📄 Licencia

Este proyecto es de uso interno para entidades cubanas.

⭐ Si este proyecto te ha sido útil, ¡no olvides darle una estrella en GitHub! 

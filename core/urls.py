"""
Configuración de URLs de la aplicación core.
Define todas las rutas del sistema organizadas por funcionalidad.
Las URLs protegidas están aquí; el middleware/decorators se encargan
de la seguridad a nivel de vista.
"""

from django.urls import path
from . import views

# Importa las dos vistas:
from core.views import ia_analisis_page, api_ia_analisis

# Prefijo para las URLs administrativas (protege las rutas con una capa extra)
# Esto hace que las URLs de admin no sean predecibles

urlpatterns = [
    # ═══ Vistas Públicas ═══
    path('', views.vista_home, name='home'),
    path('base-legal/', views.vista_base_legal, name='base_legal'),
    path('efemerides/', views.vista_efemerides, name='efemerides'),
    path('enlaces/', views.vista_enlaces, name='enlaces'),
    path('manual/', views.vista_manual, name='manual'),

    # ═══ Seguridad Avanzada ═══
    path('verificar-2fa/', views.vista_verificar_2fa, name='verificar_2fa'),
    path('setup-2fa/', views.vista_setup_2fa, name='setup_2fa'),
    path('desactivar-2fa/', views.vista_desactivar_2fa, name='desactivar_2fa'),
    path('cambiar-password/', views.vista_cambiar_password, name='cambiar_password'),
    path('sesiones/', views.vista_sesiones, name='sesiones'),
    path('auditoria/', views.vista_auditoria, name='auditoria'),
    
    # ═══ Autenticación ═══
    path('login/', views.vista_login, name='login'),
    path('registro/', views.vista_registro, name='registro'),
    path('logout/', views.vista_logout, name='logout'),
    
    # ═══ Vistas Protegidas (requieren login) ═══
    path('dashboard/', views.vista_dashboard, name='dashboard'),
    path('documentos/', views.vista_documentos, name='documentos'),
    path('documentos/subir/', views.vista_subir_documento, name='subir_documento'),
    path('documentos/descargar/<int:doc_id>/', views.vista_descargar_documento, name='descargar_documento'),
    path('documentos/eliminar/<int:doc_id>/', views.vista_eliminar_documento, name='eliminar_documento'),
    path('chat/', views.vista_chat, name='chat'),
    path('notificaciones/', views.vista_notificaciones, name='notificaciones'),

    # Módulo de Capacitación
    path('capacitacion/', views.vista_cursos, name='cursos'),
    path('capacitacion/curso/<int:curso_id>/', views.vista_tomar_curso, name='tomar_curso'),
    path('api/capacitacion/evaluar/<int:curso_id>/', views.api_guardar_evaluacion, name='api_evaluar_curso'),
    
    # Gestión de Políticas
    path('politicas/', views.vista_politicas, name='politicas'),
    path('politicas/crear/', views.vista_crear_politica, name='crear_politica'),
    path('politicas/<int:pol_id>/', views.vista_detalle_politica, name='detalle_politica'),

    # ═══ APIs del Chat ═══
    path('api/chat/mensajes/', views.api_chat_mensajes, name='api_chat_mensajes'),
    path('api/chat/enviar/', views.api_chat_enviar, name='api_chat_enviar'),
    
    # ═══ APIs de Notificaciones ═══
    path('api/notificacion/<int:notif_id>/leida/', views.api_marcar_notificacion_leida, name='api_notif_leida'),
    path('api/notificaciones/todas-leidas/', views.api_marcar_todas_leidas, name='api_notifs_leidas'),
    
    # ═══ Vistas Administrativas (requieren rol admin) ═══
    path('admin/usuarios/', views.vista_admin_usuarios, name='admin_usuarios'),
    path('api/usuario/<int:user_id>/rol/', views.api_cambiar_rol, name='api_cambiar_rol'),
    path('api/usuario/<int:user_id>/toggle/', views.api_activar_desactivar_usuario, name='api_toggle_usuario'),
    path('api/usuario/<int:user_id>/eliminar/', views.api_eliminar_usuario, name='api_eliminar_usuario'),
    
    # ═══ Inventario de Equipos ═══
    path('admin/inventario/', views.vista_admin_inventario, name='admin_inventario'),
    path('admin/inventario/agregar/', views.vista_agregar_equipo, name='agregar_equipo'),
    path('admin/inventario/editar/<int:equipo_id>/', views.vista_editar_equipo, name='editar_equipo'),
    path('admin/inventario/pdf/', views.vista_descargar_pdf_inventario, name='descargar_pdf_inventario'),
    path('admin/inventario/eliminar/<int:equipo_id>/', views.api_eliminar_equipo, name='eliminar_equipo'),
    
    # ═══ APIs de Componentes ═══
    path('api/componente/agregar/<int:equipo_id>/', views.api_agregar_componente, name='api_agregar_componente'),
    path('api/componente/editar/<int:comp_id>/', views.api_editar_componente, name='api_editar_componente'),
    path('api/componente/eliminar/<int:comp_id>/', views.api_eliminar_componente, name='api_eliminar_componente'),

    # APIs auxiliares para llenar Modales de Edición
    path('api/cursos/datos/<int:curso_id>/', views.api_datos_curso, name='api_datos_curso'),
    path('api/politicas/datos/<int:pol_id>/', views.api_datos_politica, name='api_datos_politica'),

    path('api/stats/dashboard/', views.api_estadisticas_dashboard, name='api_stats_dashboard'),
    path('tickets/', views.vista_tickets, name='tickets'),
    path('tickets/crear/', views.vista_crear_ticket, name='crear_ticket'),
    path('tickets/<int:ticket_id>/', views.vista_detalle_ticket, name='detalle_ticket'),

    # CRUD de Administración
    path('admin/cursos/', views.vista_admin_cursos, name='admin_cursos'),
    path('api/admin/cursos/eliminar/<int:curso_id>/', views.api_eliminar_curso, name='api_eliminar_curso'),
    
    path('admin/politicas/', views.vista_admin_politicas, name='admin_politicas'),
    path('api/admin/politicas/eliminar/<int:pol_id>/', views.api_eliminar_politica, name='api_eliminar_politica'),

    # CRUD de Departamentos
    path('admin/departamentos/', views.vista_admin_departamentos, name='admin_departamentos'),
    path('api/admin/departamentos/eliminar/<int:dep_id>/', views.api_eliminar_departamento, name='api_eliminar_departamento'),
    path('api/departamentos/datos/<int:dep_id>/', views.api_datos_departamento, name='api_datos_departamento'),

    # Mapa de Red
    path('admin/mapa-red/', views.vista_mapa_red, name='mapa_red'),
    path('api/mapa-red/datos/', views.api_datos_mapa_red, name='api_datos_mapa_red'),

    # Incidentes
    path('admin/incidentes/', views.vista_incidentes, name='incidentes'),
    path('api/admin/incidentes/eliminar/<int:inc_id>/', views.api_eliminar_incidente, name='api_eliminar_incidente'),
    path('api/incidentes/datos/<int:inc_id>/', views.api_datos_incidente, name='api_datos_incidente'),

    # Página HTML del Centro de IA
    path('centro-ia/', ia_analisis_page, name='ia_analisis'),

    # API JSON que consume el JavaScript
    path('api/ia-analisis/', api_ia_analisis, name='api_ia_analisis'),
]
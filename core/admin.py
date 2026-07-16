"""
Registro de modelos en el panel de administración de Django.
Solo root tiene acceso al admin de Django (configurado en settings).
Se personalizan los display y filtros para facilitar la gestión.
"""

from django.contrib import admin
from .models import (
    Departamento, Perfil, Documento, Equipo, Componente,
    HistorialComponente, MensajeChat, Notificacion
)


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    """Configuración del modelo Departamento en el admin de Django.
    Muestra columnas clave, permite filtrar por estado y buscar por nombre/código."""
    list_display = ['nombre', 'codigo', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre', 'codigo']
    list_editable = ['activo']  # Permite cambiar activo/inactivo directamente desde la lista


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """Configuración del modelo Perfil en el admin.
    Permite ver todos los perfiles con su rol y departamento."""
    list_display = ['nombre_completo', 'user', 'cargo', 'departamento', 'rol']
    list_filter = ['rol', 'departamento']
    search_fields = ['nombre_completo', 'cargo', 'user__username']


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    """Configuración del modelo Documento en el admin.
    Muestra quién subió cada documento y cuántas descargas tiene."""
    list_display = ['nombre_original', 'subido_por', 'visible_todos', 'fecha_subida', 'descargas']
    list_filter = ['visible_todos', 'fecha_subida']
    search_fields = ['nombre_original', 'descripcion']
    # Muestra los departamentos con acceso en la vista detalle
    filter_horizontal = ['departamentos_visibles']


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    """Configuración del modelo Equipo en el admin.
    Permite filtrar por estado, tipo y departamento para encontrar equipos rápido."""
    list_display = ['identificacion', 'tipo_equipo', 'marca', 'modelo', 'estado', 'departamento', 'ip']
    list_filter = ['estado', 'tipo_equipo', 'departamento']
    search_fields = ['identificacion', 'marca', 'modelo', 'ubicacion', 'ip', 'responsable']


@admin.register(Componente)
class ComponenteAdmin(admin.ModelAdmin):
    """Configuración del modelo Componente en el admin."""
    list_display = ['tipo', 'marca', 'modelo', 'equipo', 'estado']
    list_filter = ['tipo', 'estado']
    search_fields = ['marca', 'modelo', 'numero_serie', 'especificaciones']


@admin.register(HistorialComponente)
class HistorialComponenteAdmin(admin.ModelAdmin):
    """Configuración del historial de cambios de componentes.
    Muestra quién cambió qué y cuándo, ordenado por fecha más reciente."""
    list_display = ['equipo', 'componente', 'accion', 'registrado_por', 'fecha']
    list_filter = ['accion', 'fecha']
    search_fields = ['equipo__identificacion', 'valor_anterior', 'valor_nuevo']
    readonly_fields = ['equipo', 'componente', 'accion', 'valor_anterior', 
                       'valor_nuevo', 'campos_cambiados', 'registrado_por', 'fecha']
    # Todos los campos son de solo lectura porque el historial no debe editarse
    def has_add_permission(self, request):
        return False  # No permitir agregar historial manualmente

    def has_change_permission(self, request, obj=None):
        return False  # No permitir editar historial

    def has_delete_permission(self, request, obj=None):
        return False  # No permitir eliminar historial (auditoría)


@admin.register(MensajeChat)
class MensajeChatAdmin(admin.ModelAdmin):
    """Configuración del chat en el admin.
    Permite monitorizar los mensajes del chat interno si es necesario."""
    list_display = ['remitente', 'canal', 'contenido_truncado', 'fecha', 'leido']
    list_filter = ['canal', 'leido', 'fecha']
    search_fields = ['remitente__username', 'contenido']

    def contenido_truncado(self, obj):
        """Muestra solo los primeros 50 caracteres del mensaje en la lista."""
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_truncado.short_description = 'Mensaje'


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    """Configuración de notificaciones en el admin."""
    list_display = ['titulo', 'tipo', 'destinatario', 'leida', 'fecha']
    list_filter = ['tipo', 'leida', 'fecha']
    search_fields = ['titulo', 'mensaje', 'destinatario__username']
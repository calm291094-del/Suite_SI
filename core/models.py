"""
Modelos de datos del sistema.
Define la estructura de la base de datos: departamentos, perfiles de usuario,
documentos, equipos, componentes, historial de cambios, chat y notificaciones.
Todos los modelos incluyen metadata para auditoría.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
import uuid

class Departamento(models.Model):
    """Modelo para documentos compartidos (funcionalidad FTP).
    Cada documento puede ser visible para todos los usuarios
    o restringido a uno o varios departamentos específicos."""
    
    nombre = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name='Nombre del departamento',
        help_text='Ej: Dirección de Informática, Recursos Humanos, etc.'
    )
    codigo = models.CharField(
        max_length=10, 
        unique=True,
        verbose_name='Código abreviado',
        help_text='Ej: DI, RRHH, etc.'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    """Modelo de perfil extendido para cada usuario.
    Contiene el rol, departamento, cargo y nombre completo.
    Se crea automáticamente cuando se registra un usuario (ver signals.py).
    
    Roles:
    - root: Super administrador (no puede ser eliminado)
    - admin_red: Administrador de red (gestiona infraestructura)
    - seguridad: Responsable de seguridad informática (gestiona políticas)
    - usuario: Usuario normal (solo puede usar funcionalidades básicas)
    """
    
    ROLES = [
        ('root', 'Super Administrador (Root)'),
        ('admin_red', 'Administrador de Red'),
        ('seguridad', 'Responsable de Seguridad Informática'),
        ('usuario', 'Usuario Normal'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='perfil',
        verbose_name='Usuario asociado'
    )
    nombre_completo = models.CharField(
        max_length=200, 
        verbose_name='Nombre completo'
    )
    cargo = models.CharField(
        max_length=150, 
        verbose_name='Cargo',
        help_text='Ej: Especialista en Redes, Director, etc.'
    )
    departamento = models.ForeignKey(
        Departamento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Departamento'
    )
    rol = models.CharField(
        max_length=20, 
        choices=ROLES, 
        default='usuario',
        verbose_name='Rol en el sistema'
    )
    telefono = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name='Teléfono'
    )
        # ═══ Campos de seguridad avanzada ═══
    fecha_ultimo_cambio_password = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Fecha del último cambio de contraseña',
        help_text='Se actualiza automáticamente al cambiar la contraseña'
    )
    dias_expiracion_password = models.PositiveIntegerField(
        default=90,
        verbose_name='Días para expiración de contraseña',
        help_text='Días después de los cuales se obliga a cambiar (0=sin expiración)'
    )
    intentos_fallidos_login = models.PositiveIntegerField(
        default=0,
        verbose_name='Intentos fallidos de login consecutivos'
    )
    bloqueado_hasta = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Bloqueado hasta (por intentos fallidos)'
    )
    secret_2fa = models.CharField(
        max_length=100, blank=True,
        verbose_name='Clave secreta TOTP (2FA)',
        help_text='Generada automáticamente al activar 2FA'
    )
    activado_2fa = models.BooleanField(
        default=False,
        verbose_name='Autenticación de dos factores activa'
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'
        permissions = [
            ('puede_gestionar_usuarios', 'Puede gestionar usuarios del sistema'),
            ('puede_gestionar_inventario', 'Puede gestionar inventario de equipos'),
            ('puede_ver_admin', 'Puede ver paneles administrativos'),
        ]

    def __str__(self):
        return f"{self.nombre_completo} - {self.get_rol_display()}"

    @property
    def es_admin(self):
        """Retorna True si el usuario tiene rol de administrador."""
        return self.rol in ['root', 'admin_red', 'seguridad']

    @property
    def es_root(self):
        """Retorna True si el usuario es root."""
        return self.rol == 'root'


class Documento(models.Model):
    """Modelo para documentos compartidos (funcionalidad FTP).
    Cada documento puede ser visible para todos los usuarios
    o restringido a uno o varios departamentos específicos."""
    
    archivo = models.FileField(
        upload_to='documentos/%Y/%m/',
        verbose_name='Archivo',
        help_text='Documento a compartir en la red interna'
    )
    nombre_original = models.CharField(
        max_length=255, 
        verbose_name='Nombre original del archivo'
    )
    descripcion = models.TextField(
        blank=True, 
        verbose_name='Descripción del documento'
    )
    subido_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Subido por'
    )
    departamentos_visibles = models.ManyToManyField(
        Departamento, 
        blank=True,
        verbose_name='Departamentos con acceso',
        help_text='Dejar vacío si es visible para todos'
    )
    visible_todos = models.BooleanField(
        default=True,
        verbose_name='Visible para todos',
        help_text='Si está activo, todos los usuarios pueden descargarlo'
    )
    tamano = models.PositiveBigIntegerField(
        default=0,
        verbose_name='Tamaño en bytes'
    )
    tipo_mime = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Tipo MIME'
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    descargas = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-fecha_subida']

    def __str__(self):
        return self.nombre_original

    def puede_ver(self, usuario):
        """Verifica si un usuario tiene permiso para ver este documento.
        Retorna True si: el documento es visible para todos,
        o si el departamento del usuario está en la lista de departamentos visibles,
        o si el usuario es administrador."""
        if self.visible_todos:
            return True
        if usuario.perfil.es_admin:
            return True
        if usuario.perfil.departamento:
            return self.departamentos_visibles.filter(
                id=usuario.perfil.departamento.id
            ).exists()
        return False


class Equipo(models.Model):
    """Modelo para equipos de cómputo en la red.
    Cada equipo tiene una ubicación, departamento, IP y MAC.
    Los componentes se asocian a través de relación inversa."""
    
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('mantenimiento', 'En mantenimiento'),
        ('dado_baja', 'Dado de baja'),
    ]
    
    identificacion = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name='Identificación del equipo',
        help_text='Ej: PC-001, LAP-DIR-003, etc.'
    )
    tipo_equipo = models.CharField(
        max_length=50,
        default='Desktop',
        verbose_name='Tipo de equipo',
        help_text='Ej: Desktop, Laptop, Servidor, Impresora'
    )
    marca = models.CharField(max_length=100, blank=True, verbose_name='Marca')
    modelo = models.CharField(max_length=150, blank=True, verbose_name='Modelo')
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='activo'
    )
    ubicacion = models.CharField(
        max_length=200, 
        verbose_name='Ubicación física',
        help_text='Ej: Oficina 201, Despacho del Director, Sala de servidores'
    )
    departamento = models.ForeignKey(
        Departamento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    ip = models.GenericIPAddressField(
        blank=True, 
        null=True,
        verbose_name='Dirección IP'
    )
    mac = models.CharField(
        max_length=17, 
        blank=True,
        verbose_name='Dirección MAC',
        help_text='Formato: AA:BB:CC:DD:EE:FF'
    )
    sistema_operativo = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Sistema operativo'
    )
    numero_inventario = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Número de inventario físico'
    )
    responsable = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name='Responsable del equipo'
    )
    observaciones = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    registrado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True
    )

    class Meta:
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['identificacion']

    def __str__(self):
        return f"{self.identificacion} - {self.ubicacion}"

    @property
    def total_componentes(self):
        """Cantidad de componentes registrados para este equipo."""
        return self.componentes.count()


class Componente(models.Model):
    """Modelo para componentes individuales de un equipo.
    Se usa para el inventario detallado y para detectar cambios
    cuando alguien modifica o reemplaza una pieza."""
    
    TIPOS = [
        ('cpu', 'Procesador (CPU)'),
        ('ram', 'Memoria RAM'),
        ('disco', 'Disco Duro / SSD'),
        ('gpu', 'Tarjeta Gráfica (GPU)'),
        ('motherboard', 'Placa Base'),
        ('fuente', 'Fuente de Poder'),
        ('tarjeta_red', 'Tarjeta de Red'),
        ('optico', 'Unidad Óptica (CD/DVD)'),
        ('case', 'Gabinete / Case'),
        ('monitor', 'Monitor'),
        ('teclado', 'Teclado'),
        ('mouse', 'Mouse'),
        ('impresora', 'Impresora'),
        ('ups', 'UPS / Regulador'),
        ('otro', 'Otro'),
    ]
    
    equipo = models.ForeignKey(
        Equipo, 
        on_delete=models.CASCADE, 
        related_name='componentes',
        verbose_name='Equipo al que pertenece'
    )
    tipo = models.CharField(max_length=20, choices=TIPOS, verbose_name='Tipo')
    marca = models.CharField(max_length=100, blank=True, verbose_name='Marca')
    modelo = models.CharField(max_length=200, blank=True, verbose_name='Modelo')
    especificaciones = models.TextField(
        blank=True,
        verbose_name='Especificaciones técnicas',
        help_text='Ej: Intel Core i5-10400, 2.9GHz, 6 núcleos'
    )
    numero_serie = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name='Número de serie'
    )
    capacidad = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Capacidad',
        help_text='Ej: 8GB, 500GB, 256GB SSD'
    )
    estado = models.CharField(
        max_length=20,
        choices=Equipo.ESTADOS,
        default='activo'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Componente'
        verbose_name_plural = 'Componentes'
        ordering = ['tipo']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.marca} {self.modelo}".strip()

    def obtener_descripcion_completa(self):
        """Retorna una cadena con todos los datos del componente
        para comparar y detectar cambios."""
        partes = [
            f"Tipo: {self.get_tipo_display()}",
            f"Marca: {self.marca}",
            f"Modelo: {self.modelo}",
            f"Especificaciones: {self.especificaciones}",
            f"NS: {self.numero_serie}",
            f"Capacidad: {self.capacidad}",
            f"Estado: {self.get_estado_display()}",
        ]
        return ' | '.join(p for p in partes if p.split(': ')[1])


class HistorialComponente(models.Model):
    """Registra cada cambio realizado en un componente.
    Permite saber quién cambió qué, cuándo y cómo era antes.
    Es la base del sistema de monitoreo y alertas de cambios de hardware."""
    
    ACCIONES = [
        ('creado', 'Componente creado'),
        ('modificado', 'Componente modificado'),
        ('eliminado', 'Componente eliminado'),
        ('cambio_detectado', 'Cambio no autorizado detectado'),
    ]
    
    componente = models.ForeignKey(
        Componente, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Componente afectado'
    )
    equipo = models.ForeignKey(
        Equipo, 
        on_delete=models.CASCADE,
        verbose_name='Equipo afectado'
    )
    accion = models.CharField(
        max_length=25, 
        choices=ACCIONES,
        verbose_name='Tipo de acción'
    )
    valor_anterior = models.TextField(
        blank=True,
        verbose_name='Estado anterior del componente'
    )
    valor_nuevo = models.TextField(
        blank=True,
        verbose_name='Nuevo estado del componente'
    )
    campos_cambiados = models.TextField(
        blank=True,
        verbose_name='Lista de campos que cambiaron'
    )
    registrado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Registrado por'
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Historial de componente'
        verbose_name_plural = 'Historiales de componentes'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.equipo.identificacion} - {self.get_accion_display()} - {self.fecha}"


class MensajeChat(models.Model):
    """Modelo para mensajes del chat interno.
    Soporta canales: 'general' para chat grupal,
    o 'privado_X_Y' para chat privado entre dos usuarios."""
    
    remitente = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='mensajes_enviados'
    )
    canal = models.CharField(
        max_length=100, 
        default='general',
        verbose_name='Canal del mensaje',
        help_text='general para chat de todos, privado_X_Y para privado'
    )
    contenido = models.TextField(verbose_name='Contenido del mensaje')
    fecha = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False, verbose_name='Leído')

    class Meta:
        verbose_name = 'Mensaje de chat'
        verbose_name_plural = 'Mensajes de chat'
        ordering = ['fecha']

    def __str__(self):
        return f"{self.remitente.username}: {self.contenido[:50]}..."


class Notificacion(models.Model):
    """Modelo para notificaciones del sistema.
    Se crean automáticamente cuando: se detecta un cambio de hardware,
    se registra un nuevo usuario, se sube un documento, etc."""
    
    TIPOS = [
        ('cambio_hardware', 'Cambio de Hardware Detectado'),
        ('nuevo_usuario', 'Nuevo Usuario Registrado'),
        ('nuevo_documento', 'Nuevo Documento Subido'),
        ('alerta_seguridad', 'Alerta de Seguridad'),
        ('sistema', 'Notificación del Sistema'),
        ('inventario', 'Actualización de Inventario'),
    ]
    
    tipo = models.CharField(max_length=30, choices=TIPOS)
    titulo = models.CharField(max_length=255, verbose_name='Título')
    mensaje = models.TextField(verbose_name='Mensaje detallado')
    destinatario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    leida = models.BooleanField(default=False)
    enlace = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name='Enlace relacionado',
        help_text='URL a la que redirige al hacer clic en la notificación'
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.titulo} -> {self.destinatario.username}"

# ══════════════════════════════════════════════════════════════
# MODELOS DE SEGURIDAD AVANZADA (Mejoras de alta prioridad)
# ══════════════════════════════════════════════════════════════

class SesionUsuario(models.Model):
    """Registro de cada inicio y cierre de sesión.
    Base legal: Res. 128/2019 Art. 8 (controles de acceso — registro de accesos)."""
    
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sesiones',
        verbose_name='Usuario'
    )
    fecha_hora = models.DateTimeField(
        verbose_name='Fecha y hora de inicio',
        auto_now_add=True
    )
    direccion_ip = models.CharField(
        max_length=45, verbose_name='Dirección IP',
        default='0.0.0.0'
    )
    navegador = models.CharField(
        max_length=50, verbose_name='Navegador', default='Otro'
    )
    sistema_operativo = models.CharField(
        max_length=30, verbose_name='Sistema operativo', default='Otro'
    )
    dispositivo = models.CharField(
        max_length=20, verbose_name='Tipo de dispositivo', default='Desktop'
    )
    exitosa = models.BooleanField(
        default=True, verbose_name='Login exitoso'
    )
    cierre_sesion = models.DateTimeField(
        null=True, blank=True, verbose_name='Fecha y hora de cierre'
    )

    class Meta:
        verbose_name = 'Registro de sesión'
        verbose_name_plural = 'Registros de sesiones'
        ordering = ['-fecha_hora']

    def __str__(self):
        estado = 'Cerrada' if self.cierre_sesion else 'Activa'
        return f"{self.user.username} - {self.fecha_hora:%d/%m/%Y %H:%M} ({estado})"

    @property
    def duracion(self):
        """Calcula la duración de la sesión."""
        if self.cierre_sesion:
            delta = self.cierre_sesion - self.fecha_hora
            return str(delta).split('.')[0]  # Quitar microsegundos
        return 'En curso'

class RegistroAuditoria(models.Model):
    """Registro inmutable de TODAS las acciones del sistema.
    Base legal: Res. 129/2019 Art. 16 (registros de eventos de seguridad).
    Los registros NO pueden editarse ni borrarse desde la interfaz."""
    
    # Lista completa de acciones del sistema
    ACCIONES = [
        ('login', 'Inicio de Sesión'),
        ('logout', 'Cierre de Sesión'),
        ('login_fallo', 'Login Fallido'),
        ('cuenta_bloqueada', 'Cuenta Bloqueada'),
        ('password_expirada', 'Contraseña Expirada'),
        ('cambiar_password', 'Cambio de Contraseña'),
        ('2fa_activada', '2FA Activada'),
        ('2fa_desactivada', '2FA Desactivada'),
        ('registro_usuario', 'Registro de Usuario'),
        ('cambiar_rol', 'Cambio de Rol'),
        ('activar_usuario', 'Activar/Desactivar Usuario'),
        ('eliminar_usuario', 'Eliminación de Usuario'),
        ('subir_documento', 'Subida de Documento'),
        ('eliminar_documento', 'Eliminación de Documento'),
        ('cambio_hardware', 'Modificación de Hardware'),
        ('creacion_hardware', 'Registro de Hardware'),
        ('eliminacion_hardware', 'Eliminación de Hardware'),
        ('crear_ticket', 'Creación de Ticket'),
        ('eliminar_ticket', 'Eliminación de Ticket'),
        ('crear_politica', 'Creación de Política'),
        ('editar_politica', 'Actualización de Política'),
        ('eliminar_politica', 'Eliminación de Política'),
        ('crear_curso', 'Creación de Curso'),
        ('eliminar_curso', 'Eliminación de Curso'),
        ('aprobacion_curso', 'Aprobación de Curso'),
        ('crear_departamento', 'Creación de Departamento'),
        ('editar_departamento', 'Edición de Departamento'),
        ('eliminar_departamento', 'Eliminación de Departamento'),
        ('crear_incidente', 'Registro de Incidente'),
        ('editar_incidente', 'Actualización de Incidente'),
        ('eliminar_incidente', 'Eliminación de Incidente'),
    ]
    
    usuario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='registros_auditoria',
        verbose_name='Usuario que ejecutó la acción'
    )
    accion = models.CharField(
        max_length=30, choices=ACCIONES,
        verbose_name='Tipo de acción'
    )
    
    # Nota: Usamos CharField en lugar de IntegerField para permitir IDs como "TK-1" o "DEP-2"
    modelo = models.CharField(
        max_length=100, blank=True,
        verbose_name='Modelo afectado'
    )
    objeto_id = models.CharField(
        max_length=100, blank=True,
        verbose_name='ID del objeto'
    )
    descripcion = models.TextField(
        verbose_name='Descripción de la acción'
    )
    
    # Usamos CharField por compatibilidad. Recibe tanto "192.168.1.1" como "0.0.0.0"
    direccion_ip = models.CharField(
        max_length=45, default='0.0.0.0',
        verbose_name='Dirección IP'
    )
    
    datos_anterior = models.TextField(
        blank=True, null=True,
        verbose_name='Estado anterior (JSON)',
        help_text='Valores del objeto antes de la modificación'
    )
    datos_nuevo = models.TextField(
        blank=True, null=True,
        verbose_name='Estado nuevo (JSON)',
        help_text='Valores del objeto después de la modificación'
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora')

    class Meta:
        verbose_name = 'Registro de auditoría'
        verbose_name_plural = 'Registros de auditoría'
        ordering = ['-fecha']
        # IMPUTABLE: Esta línea evita que el Admin de Django genere botones de Editar/Borrar
        managed = False 

    def __str__(self):
        return f"[{self.fecha|date:'d/m/Y H:i'}] {self.get_accion_display()} - {self.usuario}"

# ══════════════════════════════════════════════════════════════
# NUEVOS MÓDULOS (Ideas de Mejora)
# ══════════════════════════════════════════════════════════════

class Ticket(models.Model):
    """Para el Sistema de Tickets de Soporte"""
    PRIORIDAD_CHOICES = [('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta'), ('critica', 'Crítica')]
    ESTADO_CHOICES = [('abierto', 'Abierto'), ('en_progreso', 'En Progreso'), ('espera', 'Espera de Respuesta'), ('cerrado', 'Cerrado')]
    
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción del problema")
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets_creados')
    asignado_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_asignados')
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierto')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    
    class Meta: ordering = ['-fecha_creacion']
    def __str__(self): return f"TK-{self.id} - {self.titulo}"

class MensajeTicket(models.Model):
    """Hilo de conversación dentro de un ticket"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='mensajes')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta: ordering = ['fecha']

class CursoCapacitacion(models.Model):
    """Para el Módulo de capacitación. Las preguntas se guardan en texto JSON."""
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    # CAMBIADO A TextField
    preguntas = models.TextField(default="[]", verbose_name="Preguntas y opciones (JSON)", help_text="Formato: [{'p': 'Pregunta', 'o': ['Opc1', 'Opc2'], 'r': 0}]")
    
    def __str__(self): return self.titulo

class EvaluacionCurso(models.Model):
    """Registra quién aprobó qué curso y sus respuestas"""
    curso = models.ForeignKey(CursoCapacitacion, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calificacion = models.IntegerField(help_text="Porcentaje de 0 a 100")
    # CAMBIADO A TextField
    respuestas = models.TextField(default="{}", blank=True, verbose_name="Respuestas seleccionadas (JSON)")
    aprobado = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta: unique_together = ('curso', 'usuario')

class PoliticaSeguridad(models.Model):
    """Para Gestión de políticas con vencimiento"""
    nombre = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_vigencia = models.DateField(verbose_name="Fecha de vencimiento")
    estado = models.CharField(max_length=20, default='vigente')
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): return self.nombre

class AnalisisVulnerabilidad(models.Model):
    """Para Análisis de vulnerabilidades"""
    titulo = models.CharField(max_length=200)
    analista = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): return self.titulo

class HallazgoVuln(models.Model):
    """Un hallazgo específico dentro de un análisis"""
    analisis = models.ForeignKey(AnalisisVulnerabilidad, on_delete=models.CASCADE, related_name='hallazgos')
    descripcion = models.TextField()
    severidad = models.CharField(max_length=20, choices=[('baja','Baja'),('media','Media'),('alta','Alta'),('critica','Crítica')])
    plan_accion = models.TextField(blank=True)

class RegistroIncidente(models.Model):
    """Para el Plan de respuesta a incidentes digital"""
    tipo_incidente = models.CharField(max_length=100)
    descripcion = models.TextField()
    respondedor = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, default='abierto')
    lecciones_aprendidas = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
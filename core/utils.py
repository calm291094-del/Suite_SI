"""
Funciones utilitarias del sistema.
Incluye: generación de PDFs de inventario, cálculo de fortaleza de contraseña,
envío de notificaciones masivas, yhelpers para el monitoreo de hardware.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    PageBreak, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from django.utils import timezone
from .models import Equipo, Componente, Notificacion
import hashlib
import json

def generar_pdf_inventario(equipo_ids=None, departamento=None):
    """Genera un PDF profesional con el inventario de equipos.
    
    Args:
        equipo_ids: Lista de IDs de equipos específicos (opcional)
        departamento: Si se pasa, filtra por ese departamento
    
    Returns:
        BytesIO con el PDF generado listo para descarga
    """
    buffer = BytesIO()
    
    # Crear documento PDF con márgenes
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    
    # Estilos de texto
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'TituloPersonalizado',
        parent=estilos['Title'],
        fontSize=18,
        textColor=colors.HexColor('#0a1628'),
        spaceAfter=20,
        alignment=TA_CENTER,
    )
    estilo_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=estilos['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#1a3a5c'),
        spaceAfter=10,
    )
    estilo_normal = ParagraphStyle(
        'Normal',
        parent=estilos['Normal'],
        fontSize=9,
        leading=12,
    )
    estilo_celda = ParagraphStyle(
        'Celda',
        parent=estilos['Normal'],
        fontSize=8,
        leading=10,
    )
    
    elementos = []
    
    # ── Encabezado del documento ──
    elementos.append(Paragraph(
        'INVENTARIO DE EQUIPOS DE CÓMPUTO',
        estilo_titulo
    ))
    elementos.append(Paragraph(
        f'Generado: {timezone.now().strftime("%d/%m/%Y a las %H:%M")} | '
        f'Base Legal: Resoluciones 128/2019 y 129/2019 del MINCOM',
        ParagraphStyle('Fecha', parent=estilo_normal, alignment=TA_CENTER, 
                       textColor=colors.gray, fontSize=9)
    ))
    elementos.append(Spacer(1, 0.5*cm))
    
    # ── Filtrar equipos según parámetros ──
    equipos = Equipo.objects.filter(estado='activo')
    if equipo_ids:
        equipos = equipos.filter(id__in=equipo_ids)
    if departamento:
        equipos = equipos.filter(departamento=departamento)
    
    # ── Tabla resumen de equipos ──
    elementos.append(Paragraph('RESUMEN DE EQUIPOS', estilo_subtitulo))
    
    datos_tabla = [['ID', 'Tipo', 'Marca/Modelo', 'Ubicación', 'Dept.', 'IP', 'Estado']]
    for eq in equipos:
        datos_tabla.append([
            eq.identificacion,
            eq.tipo_equipo,
            f'{eq.marca} {eq.modelo}'.strip(),
            eq.ubicacion[:40],
            eq.departamento.nombre if eq.departamento else '-',
            eq.ip or '-',
            eq.get_estado_display(),
        ])
    
    tabla = Table(datos_tabla, colWidths=[1.8*cm, 2*cm, 3.5*cm, 3.5*cm, 2.5*cm, 2.5*cm, 2*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0a1628')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elementos.append(tabla)
    
    # ── Detalle de componentes por equipo ──
    elementos.append(Spacer(1, 0.8*cm))
    elementos.append(Paragraph('DETALLE DE COMPONENTES POR EQUIPO', estilo_subtitulo))
    
    for eq in equipos:
        componentes = eq.componentes.all()
        if not componentes:
            continue
            
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(Paragraph(
            f'<b>Equipo: {eq.identificacion}</b> — {eq.ubicacion} '
            f'({"Activo" if eq.estado == "activo" else eq.get_estado_display()})',
            ParagraphStyle('EqTitle', parent=estilo_normal, fontSize=9, 
                          textColor=colors.HexColor('#0a1628'))
        ))
        
        datos_comp = [['Tipo', 'Marca', 'Modelo', 'Especificaciones', 'Capacidad', 'N/Serie']]
        for comp in componentes:
            datos_comp.append([
                comp.get_tipo_display(),
                comp.marca,
                comp.modelo,
                comp.especificaciones[:50] if comp.especificaciones else '-',
                comp.capacidad or '-',
                comp.numero_serie or '-',
            ])
        
        tabla_comp = Table(datos_comp, colWidths=[2.5*cm, 2.5*cm, 3*cm, 4.5*cm, 2*cm, 3*cm])
        tabla_comp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a5c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elementos.append(tabla_comp)
        
        # Salto de página cada 3 equipos para no saturar
        if equipos.index(eq) % 3 == 2 and equipos.index(eq) < len(equipos) - 1:
            elementos.append(PageBreak())
    
    # ── Pie del documento ──
    elementos.append(Spacer(1, 1*cm))
    elementos.append(Paragraph(
        'Este documento es propiedad de la institución y está amparado por las '
        'Resoluciones 128/2019 y 129/2019 del Ministerio de Comunicaciones (MINCOM) '
        'y el Decreto-Ley 370/2019. Su reproducción o distribución no autorizada está prohibida.',
        ParagraphStyle('Pie', parent=estilo_normal, fontSize=7, 
                       textColor=colors.gray, alignment=TA_CENTER)
    ))
    
    # Construir el PDF
    doc.build(elementos)
    buffer.seek(0)
    return buffer


def crear_notificacion(tipo, titulo, mensaje, destinatarios, enlace=''):
    """Crea notificaciones para múltiples usuarios.
    
    Args:
        tipo: str de choices de Notificacion.TIPOS
        titulo: Título corto de la notificación
        mensaje: Mensaje detallado
        destinatarios: QuerySet de User o lista de Users
        enlace: URL opcional a la que redirige la notificación
    """
    for user in destinatarios:
        Notificacion.objects.create(
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            destinatario=user,
            enlace=enlace
        )


def detectar_cambios_componente(componente, usuario_editor):
    """Compara el estado actual de un componente con el último registro
    en el historial. Si detecta cambios, crea una notificación de alerta
    para todos los administradores.
    
    Esto implementa el requerimiento de "vigilar y notificar si alguien
    cambia alguna pieza o componente".
    
    Args:
        componente: Instancia de Componente ya guardada
        usuario_editor: User que realizó la modificación
    """
    from .models import HistorialComponente
    
    # Buscar el último historial de este componente
    ultimo = HistorialComponente.objects.filter(
        componente=componente
    ).exclude(accion='eliminado').order_by('-fecha').first()
    
    descripcion_actual = componente.obtener_descripcion_completa()
    
    if ultimo and ultimo.valor_nuevo != descripcion_actual:
        # Se detectó un cambio - notificar a todos los admins
        admins = usuario_editor.__class__.objects.filter(
            perfil__rol__in=['root', 'admin_red', 'seguridad']
        ).exclude(id=usuario_editor.id)
        
        crear_notificacion(
            tipo='cambio_hardware',
            titulo=f'Cambio detectado en {componente.equipo.identificacion}',
            mensaje=(
                f'Se detectó una modificación en el componente {componente.get_tipo_display()} '
                f'del equipo {componente.equipo.identificacion} ({componente.equipo.ubicacion}).\n'
                f'Registrado por: {usuario_editor.perfil.nombre_completo}\n'
                f'Fecha: {timezone.now().strftime("%d/%m/%Y %H:%M")}'
            ),
            destinatarios=admins,
            enlace=f'/admin/inventario/editar/{componente.equipo.id}/'
        )

# ══════════════════════════════════════════════════════════════
# FUNCIONES DE SEGURIDAD AVANZADA
# ══════════════════════════════════════════════════════════════

def obtener_ip(request):
    """Obtiene la IP real del cliente (considera proxy inverso)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def obtener_navegador(request):
    """Detecta el navegador desde User-Agent."""
    ua = request.META.get('HTTP_USER_AGENT', '')
    if 'Edg' in ua: return 'Edge'
    if 'Firefox' in ua: return 'Firefox'
    if 'OPR' in ua or 'Opera' in ua: return 'Opera'
    if 'Chrome' in ua: return 'Chrome'
    if 'Safari' in ua: return 'Safari'
    return 'Otro'


def obtener_so(request):
    """Detecta el sistema operativo desde User-Agent."""
    ua = request.META.get('HTTP_USER_AGENT', '')
    if 'Android' in ua: return 'Android'
    if 'iPhone' in ua or 'iPad' in ua: return 'iOS'
    if 'Windows' in ua: return 'Windows'
    if 'Mac' in ua: return 'macOS'
    if 'Linux' in ua: return 'Linux'
    return 'Otro'


def obtener_dispositivo(request):
    """Detecta si es Desktop, Móvil o Tablet."""
    ua = request.META.get('HTTP_USER_AGENT', '')
    if 'Mobile' in ua or 'Android' in ua or 'iPhone' in ua:
        return 'Móvil'
    if 'Tablet' in ua or 'iPad' in ua:
        return 'Tablet'
    return 'Desktop'


def registrar_auditoria(
    request, accion, modelo='', objeto_id='',
    descripcion='', datos_anterior=None, datos_nuevo=None, usuario=None
):
    """Registra una acción en la tabla de auditoría inmutable.
    
    Args:
        request: Objeto HttpRequest
        accion: Código de acción (de las choices de RegistroAuditoria)
        modelo: Nombre del modelo afectado (ej: 'auth.User', 'core.Equipo')
        objeto_id: ID del objeto afectado
        descripcion: Descripción legible de la acción
        datos_anterior: Dict con valores anteriores (se guarda como JSON)
        datos_nuevo: Dict con valores nuevos (se guarda como JSON)
        usuario: Usuario override (si no es el de request)
    """
    from .models import RegistroAuditoria
    
    RegistroAuditoria.objects.create(
        usuario=usuario or (request.user if request.user.is_authenticated else None),
        accion=accion,
        modelo=modelo,
        objeto_id=str(objeto_id),
        descripcion=descripcion,
        direccion_ip=obtener_ip(request),
        datos_anterior=json.dumps(datos_anterior, ensure_ascii=False) if datos_anterior else None,
        datos_nuevo=json.dumps(datos_nuevo, ensure_ascii=False) if datos_nuevo else None,
    )


def dias_para_expirar(perfil):
    """Calcula días restantes antes de que expire la contraseña."""
    if not perfil.fecha_ultimo_cambio_password or perfil.dias_expiracion_password == 0:
        return None
    from datetime import timedelta
    delta = (perfil.fecha_ultimo_cambio_password + 
             timedelta(days=perfil.dias_expiracion_password) - timezone.now())
    return delta.days


def esta_bloqueado(perfil):
    """Verifica si una cuenta está bloqueada por intentos fallidos."""
    if not perfil.bloqueado_hasta:
        return False
    return timezone.now() < perfil.bloqueado_hasta


def bloquear_cuenta(perfil, minutos=30):
    """Bloquea una cuenta por N minutos."""
    from datetime import timedelta
    perfil.bloqueado_hasta = timezone.now() + timedelta(minutes=minutos)
    perfil.intentos_fallidos_login = 0
    perfil.save()


def reiniciar_intentos(perfil):
    """Reinicia el contador de intentos fallidos."""
    perfil.intentos_fallidos_login = 0
    perfil.bloqueado_hasta = None
    perfil.save()
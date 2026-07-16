"""
Vistas del sistema.
Cada vista maneja una página o acción específica:
- Públicas: home, legal, efemérides, enlaces
- Autenticación: login, registro, logout
- Protegidas: dashboard, documentos, chat
- Administrativas: gestión de usuarios, inventario, notificaciones
Todas las vistas protegidas usan los decoradores de core.decorators.
"""

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.utils import timezone
from django.db import transaction
from django.db.models import Count
from django.conf import settings 
from .models import (
    Perfil, Departamento, Documento, Equipo, Componente, PoliticaSeguridad,
    HistorialComponente, MensajeChat, Notificacion, RegistroIncidente,
    SesionUsuario, RegistroAuditoria, Ticket, CursoCapacitacion, EvaluacionCurso
)
from .forms import (
    FormularioLogin, FormularioRegistro, FormularioDocumento, FormularioIncidente,
    FormularioEquipo, FormularioComponente, FormularioTicket, FormularioPolitica, FormularioCurso,
    FormularioCambiarPassword, FormularioVerificar2FA, FormularioDepartamento, FormularioMensajeTicket
)
from .decorators import login_requerido, admin_requerido, root_requerido
from .utils import (
    generar_pdf_inventario, crear_notificacion, detectar_cambios_componente,
    obtener_ip, obtener_navegador, obtener_so, obtener_dispositivo,
    registrar_auditoria, esta_bloqueado, bloquear_cuenta, reiniciar_intentos,
    dias_para_expirar,
)
from django.db.models import Count
from datetime import date, timedelta
import json
import pyotp
import qrcode
import io
import base64
from datetime import timedelta

# ══════════════════════════════════════════════════════════════
# VISTAS PÚBLICAS (no requieren autenticación)
# ══════════════════════════════════════════════════════════════
def vista_home(request):
    """Página principal pública.
    Muestra información detallada de la base legal vigente en Cuba
    en materia de seguridad informática, datos curiosos e importantes,
    y un resumen de las funcionalidades de la suite."""
    
    contexto = {
        'base_legal': [
            {
                'titulo': 'Decreto-Ley 370/2019',
                'subtitulo': 'Sobre la Informatización de la Sociedad en Cuba',
                'descripcion': (
                    'Establece los principios, objetivos y políticas para la informatización '
                    'de la sociedad cubana. Define las responsabilidades de las instituciones '
                    'en materia de seguridad de la información y protección de datos. '
                    'Obliga a las entidades a implementar medidas técnicas y organizativas '
                    'para proteger la información que procesan.'
                ),
                'datos_curiosos': [
                    'Fue publicado en la Gaceta Oficial Extraordinaria No. 47 de 2019.',
                    'Es la norma marco que da base a todas las demás resoluciones en materia informática.',
                    'Establece que la seguridad informática es responsabilidad de TODOS los niveles de la organización.',
                    'Define la obligatoriedad de contar con un responsable de seguridad informática por entidad.',
                ]
            },
            {
                'titulo': 'Resoluciones 128/2019 y 129/2019 del MINCOM',
                'subtitulo': 'Reglamento de la Seguridad Informática y Medidas Técnicas',
                'descripcion': (
                    'Estas dos resoluciones del Ministerio de Comunicaciones (MINCOM) sustituyeron '
                    'la derogada Resolución 127/2020. La Resolución 128/2019 establece el reglamento '
                    'general de la seguridad informática: controles de acceso, gestión de incidentes, '
                    'planes de contingencia y documentación requerida. La Resolución 129/2019 '
                    'complementa con las medidas técnicas mínimas: cifrado, respaldos, firewalls, '
                    'antivirus, segmentación de red y monitoreo de logs.'
                ),
                'datos_curiosos': [
                    'Sustituyen a la Resolución 127/2020 que fue derogada oficialmente.',
                    'La Res. 128/2019 exige un inventario actualizado de todos los activos de información.',
                    'Establecen la clasificación de la información en: pública, interna, confidencial y secreta.',
                    'La Res. 129/2019 requiere que las contraseñas tengan mínimo 8 caracteres y se cambien periódicamente.',
                    'Obligan a mantener registros de todos los incidentes de seguridad con retención mínima de 6 meses.',
                    'La Res. 129/2019 especifica que los respaldos deben ser verificados al menos mensualmente.',
                    'Exigen segmentar la red en zonas con diferentes niveles de seguridad.',
                    'Requieren que el software sea legal y debidamente licenciado.',
                ]
            },
            {
                'titulo': 'Decreto-Ley 35/2021',
                'subtitulo': 'De las Telecomunicaciones',
                'descripcion': (
                    'Regula las telecomunicaciones en Cuba, incluyendo el uso de redes, '
                    'servicios de internet y la infraestructura de comunicaciones. '
                    'Establece las obligaciones de los proveedores y los derechos de los usuarios.'
                ),
                'datos_curiosos': [
                    'Regula tanto redes públicas como redes privadas (intranets institucionales).',
                    'Establece que las entidades deben tener políticas de uso aceptable de las TIC.',
                    'Define las sanciones por uso indebido de los recursos de telecomunicaciones.',
                    'Incluye disposiciones sobre ciberseguridad de la infraestructura crítica.',
                ]
            },
            {
                'titulo': 'Resolución 105/2020 del MIC',
                'subtitulo': 'Normas Cubanas de Gestión de la Seguridad de la Información',
                'descripcion': (
                    'Establece los requisitos para implementar un Sistema de Gestión de Seguridad '
                    'de la Información (SGSI) basado en la familia de normas ISO/IEC 27000 '
                    'adaptadas al contexto cubano. Define el ciclo PDCA para la mejora continua '
                    'y exige auditorías internas anuales del SGSI.'
                ),
                'datos_curiosos': [
                    'Se basa en la familia NC-ISO/IEC 27000 adaptadas a la realidad cubana.',
                    'Requiere un ciclo PDCA (Planificar, Hacer, Verificar, Actuar) para la seguridad.',
                    'Exige auditorías internas del SGSI al menos una vez al año.',
                    'Define la figura del "responsable del SGSI" que debe reportar a la alta dirección.',
                ]
            },
            {
                'titulo': 'Constitución de la República (2019)',
                'subtitulo': 'Artículos relacionados con la informática y datos personales',
                'descripcion': (
                    'La Constitución cubana de 2019 incluye disposiciones sobre la privacidad '
                    'de las comunicaciones y la protección de datos personales. El Art. 40 '
                    'garantiza la inviolabilidad de la correspondence, y el Art. 48 protege '
                    'los datos personales contra uso indebido.'
                ),
                'datos_curiosos': [
                    'Art. 40: Toda persona tiene derecho a la inviolabilidad de su correspondence.',
                    'Art. 48: Los datos personales solo pueden ser recogidos y procesados con consentimiento.',
                    'Art. 97: Regula el derecho de acceso a la información pública.',
                    'Es la primera Constitución cubana que menciona explícitamente la protección de datos personales.',
                ]
            },
            {
                'titulo': 'Decreto-Ley 38/2023',
                'subtitulo': 'De la Ciberseguridad de la República de Cuba',
                'descripcion': (
                    'Marco jurídico específico para la ciberseguridad nacional. Define las '
                    'amenazas cibernéticas, establece la estrategia nacional de ciberseguridad, '
                    'crea mecanismos de coordinación interinstitucional y regula la protección '
                    'de la infraestructura crítica de información y las comunicaciones.'
                ),
                'datos_curiosos': [
                    'Es la norma más reciente y específica sobre ciberseguridad en Cuba.',
                    'Define la infraestructura crítica de información (ICI) que debe tener protección especial.',
                    'Establece la obligatoriedad de reportar incidentes de ciberseguridad al CERT-CU.',
                    'Crea el Consejo Nacional de Ciberseguridad como órgano coordinador.',
                    'Regula las operaciones de inteligencia cibernética defensiva del Estado.',
                ]
            },
        ],
        'responsabilidades': {
            'admin_red': {
                'titulo': 'Administrador de Red',
                'funciones': [
                    'Instalar, configurar y mantener la infraestructura de red (switches, routers, access points, cableado).',
                    'Gestionar las direcciones IP, VLANs, DNS interno y DHCP.',
                    'Configurar y mantener firewalls, reglas de filtrado y segmentación de red.',
                    'Monitorear el tráfico de red para detectar anomalías y accesos no autorizados.',
                    'Mantener actualizado el inventario detallado de todos los equipos conectados a la red.',
                    'Gestionar los accesos Wi-Fi y las políticas de seguridad de la red inalámbrica.',
                    'Implementar y verificar los sistemas de respaldo de la configuración de red.',
                    'Documentar la topología de red y cualquier cambio realizado.',
                    'Vigilar que ningún equipo no autorizado se conecte a la red institucional.',
                    'Responder ante caídas de red y degraded service, minimizando el tiempo de inactividad.',
                    'Coordinar con el proveedor de internet la conexión WAN y resolver incidencias.',
                    'Mantener actualizados los firmwares de los dispositivos de red.',
                ],
                'base_legal': 'Res. 128/2019 (Cap. III, Art. 15-18), Res. 129/2019 (Cap. II), Decreto-Ley 35/2021, DL 38/2023'
            },
            'seguridad': {
                'titulo': 'Responsable de Seguridad Informática',
                'funciones': [
                    'Elaborar, actualizar y difundir las políticas de seguridad de la información.',
                    'Realizar evaluaciones de riesgo periódicas según la Res. 105/2020.',
                    'Gestionar el Sistema de Gestión de Seguridad de la Información (SGSI).',
                    'Investigar y documentar todos los incidentes de seguridad informática.',
                    'Planificar y ejecutar auditorías de seguridad internas.',
                    'Coordinar las pruebas de penetración y evaluaciones de vulnerabilidades.',
                    'Gestionar los accesos lógicos a los sistemas y bases de datos.',
                    'Verificar el cumplimiento de las normativas vigentes en materia informática.',
                    'Capacitar al personal en buenas prácticas de seguridad informática.',
                    'Mantener actualizado el plan de respuesta a incidentes.',
                    'Clasificar la información según los niveles definidos en la Res. 128/2019.',
                    'Verificar que los controles criptográficos se implementen correctamente.',
                    'Supervisar la gestión de contraseñas y políticas de autenticación.',
                    'Elaborar informes periódicos para la alta dirección sobre el estado de la seguridad.',
                    'Gestionar las relaciones con entidades de ciberseguridad a nivel nacional (CERT-CU, MINCOM).',
                ],
                'base_legal': 'DL 370/2019 (Art. 26-28), Res. 128/2019 (Cap. IV, Art. 22-30), Res. 129/2019, Res. 105/2020, DL 38/2023'
            }
        }
    }
    return render(request, 'home.html', contexto)

def vista_base_legal(request):
    """Página dedicada exclusivamente a la base legal vigente.
    Contenido más extenso y detallado que el resumen del home."""
    contexto = {
        'normas': [
            {
                'numero': 'Decreto-Ley 370/2019',
                'nombre': 'Sobre la Informatización de la Sociedad',
                'gaceta': 'Gaceta Oficial Extraordinaria No. 47 de 10 de septiembre de 2019',
                'articulos_clave': [
                    ('Art. 8', 'Principios de la informatización: soberanía tecnológica, seguridad, accesibilidad.'),
                    ('Art. 15', 'Las entidades deben garantizar la seguridad de la información que procesan.'),
                    ('Art. 22', 'Obligatoriedad de implementar medidas de seguridad informática proporcionales al riesgo.'),
                    ('Art. 26', 'Designación de responsables de seguridad informática en cada entidad.'),
                    ('Art. 28', 'Obligación de reportar incidentes de seguridad al MINCOM.'),
                    ('Art. 40', 'Sanciones por incumplimiento: multas, medidas disciplinarias, responsabilidad penal.'),
                ],
                'resumen': (
                    'Esta es la norma marco de la informatización cubana. Establece que todas las entidades '
                    'estatales y de otros sectores deben adoptar medidas para garantizar la seguridad de la '
                    'información. Crea la obligación de tener un responsable de seguridad informática, '
                    'implementar controles de acceso, realizar respaldos y mantener un inventario de activos.'
                ),
            },
            {
                'numero': 'Resolución 128/2019 del MINCOM',
                'nombre': 'Reglamento de la Seguridad Informática',
                'gaceta': 'Gaceta Oficial de la República de Cuba — Ministerio de Comunicaciones, 2019',
                'articulos_clave': [
                    ('Art. 3', 'Ámbito de aplicación: todas las entidades que procesan información digital.'),
                    ('Art. 5', 'Clasificación de la información: pública, interna, confidencial, secreta.'),
                    ('Art. 8', 'Controles de acceso: identificación, autenticación y autorización.'),
                    ('Art. 12', 'Gestión de contraseñas: mínimo 8 caracteres, mayúsculas, minúsculas, números, especiales.'),
                    ('Art. 15', 'Inventario de activos de información: hardware, software, datos, servicios.'),
                    ('Art. 20', 'Gestión de incidentes: clasificación, respuesta, documentación, lecciones aprendidas.'),
                    ('Art. 25', 'Plan de contingencia: debe probarse al menos una vez al año.'),
                    ('Art. 30', 'Formación y concienciación del personal en seguridad informática.'),
                ],
                'resumen': (
                    'Reglamento detallado que operationaliza el DL 370. Es la norma específica sobre '
                    'qué hacer en materia de seguridad informática. Sustituyó a la derogada Resolución 127/2020. '
                    'Define controles concretos que cada entidad debe implementar, desde la gestión de '
                    'contraseñas hasta los planes de contingencia. Es la base técnica para el trabajo del '
                    'administrador de red y el responsable de seguridad informática.'
                ),
            },
            {
                'numero': 'Resolución 129/2019 del MINCOM',
                'nombre': 'Medidas Técnicas de Seguridad para la Protección de la Información',
                'gaceta': 'Gaceta Oficial de la República de Cuba — Ministerio de Comunicaciones, 2019',
                'articulos_clave': [
                    ('Art. 4', 'Medidas de control de acceso lógico: autenticación multifactor cuando sea posible.'),
                    ('Art. 7', 'Protección contra malware: antivirus actualizado, políticas de ejecución.'),
                    ('Art. 10', 'Cifrado de información sensible en tránsito y en reposo.'),
                    ('Art. 13', 'Respaldo de información: periódico, verificado, almacenado fuera del sitio.'),
                    ('Art. 16', 'Registro y monitoreo de eventos de seguridad (logs) con retención mínima de 6 meses.'),
                    ('Art. 19', 'Protección de la red: firewalls, IDS/IPS, segmentación por zonas de seguridad.'),
                ],
                'resumen': (
                    'Establece las medidas técnicas mínimas que deben implementarse. Sustituyó a la derogada '
                    'Resolución 56/2019. Va desde el antivirus y el firewall hasta el cifrado y los respaldos. '
                    'Cada medida viene con criterios de implementación específicos. Es la guía técnica directa '
                    'para el administrador de red.'
                ),
            },
            {
                'numero': 'Decreto-Ley 35/2021',
                'nombre': 'De las Telecomunicaciones',
                'gaceta': 'Gaceta Oficial Extraordinaria No. 76 de 4 de agosto de 2021',
                'articulos_clave': [
                    ('Art. 12', 'Obligación de las entidades de tener políticas de uso de las TIC.'),
                    ('Art. 25', 'Protección de la infraestructura de telecomunicaciones crítica.'),
                    ('Art. 40', 'Seguridad de las redes de telecomunicaciones: monitoreo, detección de intrusiones.'),
                    ('Art. 55', 'Sanciones por interferir o dañar redes de telecomunicaciones.'),
                ],
                'resumen': (
                    'Regulación integral de las telecomunicaciones que incluye aspectos de ciberseguridad. '
                    'Establece obligaciones específicas para entidades que operan redes propias (intranets), '
                    'incluyendo la seguridad de la infraestructura y la protección contra ataques.'
                ),
            },
            {
                'numero': 'Resolución 105/2020 del MIC',
                'nombre': 'Normas Cubanas de Gestión de la Seguridad de la Información',
                'gaceta': 'Gaceta Oficial No. 85 de 2020',
                'articulos_clave': [
                    ('Art. 3', 'Adopción de la familia NC-ISO/IEC 27000 como marco normativo.'),
                    ('Art. 8', 'Requisitos para establecer el SGSI: alcance, política, evaluación de riesgos.'),
                    ('Art. 15', 'Ciclo PDCA para la mejora continua de la seguridad.'),
                    ('Art. 22', 'Auditorías internas del SGSI: frecuencia mínima anual.'),
                    ('Art. 30', 'Revisión por la dirección: al menos una vez al año.'),
                ],
                'resumen': (
                    'Adapta la normativa internacional ISO 27001 al contexto cubano. Establece los requisitos '
                    'para implementar un Sistema de Gestión de Seguridad de la Información formal y auditado. '
                    'Es la norma que da estructura metodológica al trabajo del responsable de seguridad.'
                ),
            },
            {
                'numero': 'Decreto-Ley 38/2023',
                'nombre': 'De la Ciberseguridad de la República de Cuba',
                'gaceta': 'Gaceta Oficial Extraordinaria de 2023',
                'articulos_clave': [
                    ('Art. 5', 'Definición de amenazas cibernéticas y niveles de alerta.'),
                    ('Art. 12', 'Infraestructura crítica de información (ICI): identificación y protección prioritaria.'),
                    ('Art. 18', 'Obligación de reportar incidentes de ciberseguridad al CERT-CU en plazo máximo de 72 horas.'),
                    ('Art. 22', 'Consejo Nacional de Ciberseguridad: coordinación interinstitucional.'),
                    ('Art. 30', 'Operaciones de inteligencia cibernética defensiva: marco legal y control civil.'),
                ],
                'resumen': (
                    'Norma más reciente y específica sobre ciberseguridad en Cuba. Establece la estrategia '
                    'nacional de ciberseguridad, crea el Consejo Nacional de Ciberseguridad, regula la '
                    'protección de la infraestructura crítica de información y establece obligaciones de '
                    'reporte de incidentes al CERT-CU. Es el complemento necesario del DL 370/2019.'
                ),
            },
        ]
    }
    return render(request, 'base_legal.html', contexto)

def vista_efemerides(request):
    """Página de efemérides cubanas organizadas por meses.
    Incluye efemérides nacionales y la cronología de Holguín."""
    contexto = {
        'efemerides': {
            'Enero': [
                ('1', 'Triunfo de la Revolución Cubana (1959)'),
                ('2', 'Declaración de La Habana (1960)'),
                ('5', 'Día del Educador Cubano'),
                ('8', 'Natalicio de José Martí (1853)'),
                ('15', 'Natalicio de Antonio Maceo (1845)'),
                ('28', 'Derrota de la Machetería de La Habana (1923)'),
            ],
            'Febrero': [
                ('4', 'Constitución de la República (1976)'),
                ('14', 'Día de los Enamorados'),
                ('18', 'Reinicio de las luchas por la independencia (1895)'),
                ('24', 'Grito de Baire - Inicio de la Guerra del 95'),
                ('27', 'Día de la Resistencia Cívica'),
            ],
            'Marzo': [
                ('4', 'Invasión por Girón - Día de la Milicia (1961)'),
                ('8', 'Día Internacional de la Mujer'),
                ('10', 'Creación de los CDR (1960)'),
                ('13', 'Asalto al Palacio Presidencial (1957)'),
                ('14', 'Día del Moncada - Constitución de la FMC (1960)'),
            ],
            'Abril': [
                ('10', 'Abolición de la esclavitud en Cuba (1886)'),
                ('15', 'Día del Combatiente Internacionalista'),
                ('16', 'Declaración del carácter socialista de la Revolución (1961)'),
                ('19', 'Victoria de Girón (1961)'),
                ('21', 'Día del Veterano de las FAR'),
            ],
            'Mayo': [
                ('1', 'Día Internacional de los Trabajadores'),
                ('8', 'Día del Trabajador de la Cultura'),
                ('17', 'Primera Ley de Reforma Agraria (1959)'),
                ('19', 'Caída en combate de José Martí (1895)'),
                ('20', 'Día de la Independencia de Cuba (1902)'),
            ],
            'Junio': [
                ('5', 'Día del Medio Ambiente'),
                ('11', 'Operación Antiescuela (1961)'),
                ('14', 'Natalicio de Ernesto Che Guevara (1928)'),
                ('22', 'Ataque a los cuarteles de Bayamo y Holguín (1956)'),
            ],
            'Julio': [
                ('4', 'Asalto a las tropas de Maceo en Perico (1896)'),
                ('7', 'Día del Veterano de la Guerra de Africa'),
                ('11', 'Día del Rebelde'),
                ('13', 'Día del Combate de la Plata (1957)'),
                ('26', 'Asalto a los cuarteles Moncada y Carlos Manuel de Céspedes (1953)'),
                ('30', 'Día de la Revolución (1953)'),
            ],
            'Agosto': [
                ('5', 'Día del Levantamiento Popular (1994)'),
                ('7', 'Fundación del Partido Comunista (1925)'),
                ('12', 'Natalicio de Fidel Castro (1926)'),
                ('13', 'Día del Internacionalista Cubano'),
                ('23', 'Día del Esclavo Rebelde'),
            ],
            'Septiembre': [
                ('1', 'Día del Combatiente (1981)'),
                ('8', 'Día de la Virgen de la Caridad del Cobre - Patrona de Cuba'),
                ('10', 'Inauguración de la televisión cubana (1950)'),
                ('13', 'Día del Maestro'),
                ('17', 'Día de la Cruz Roja Cubana'),
                ('28', 'Promulgación del Decreto-Ley 370 de Informatización (2019)'),
            ],
            'Octubre': [
                ('2', 'Derecho al voto de la mujer en Cuba (1934)'),
                ('8', 'Día del Heroico Pueblo de Camagüey'),
                ('10', 'Inicio de las luchas independentistas (1868) - Grito de Yara'),
                ('12', 'Día de la Resistencia Indígena'),
                ('20', 'Día de la Cultura Cubana'),
                ('28', 'Desastre del buque La Coubre (1960)'),
            ],
            'Noviembre': [
                ('4', 'Día de la Conciencia Nacional'),
                ('5', 'Desembarco del Granma (1956)'),
                ('7', 'Día de los Periodistas Cubanos'),
                ('16', 'Día de la Universidad de La Habana'),
                ('20', 'Día de la Revolución en las FAR'),
                ('27', 'Asesinato de los 8 estudiantes de Medicina (1871)'),
            ],
            'Diciembre': [
                ('2', 'Día de las FAR - Día de la Solidaridad Internacionalista'),
                ('7', 'Caída en combate de Antonio Maceo (1896)'),
                ('10', 'Día de los Derechos Humanos'),
                ('13', 'Llegada de Fidel a La Habana en Caravana de la Libertad (1959)'),
                ('21', 'Día del ALBA'),
                ('29', 'Triunfo de la Revolución en Santa Clara (1958)'),
            ],
        },
        'cronologia_holguin': [
            ('1525', 'Fundada como San Isidoro de Holguín por García Holguín.'),
            ('1545', 'Se establece como villa con el nombre de Holguín.'),
            ('1752', 'Se traslada la villa a su ubicación actual en las Lomas de Mayo.'),
            ('1812', 'Holguín obtiene el título de ciudad.'),
            ('1868', 'Holguineros se incorporan a la Guerra de los Diez Años.'),
            ('1869', 'Combate de las Guásimas - Primeras acciones armadas en la región.'),
            ('1874', 'Calixto García Iñiguez toma la ciudad de Holguín brevemente.'),
            ('1895', 'Holguín se levanta en armas al inicio de la Guerra de Independencia.'),
            ('1898', 'Ocupación norteamericana tras la guerra hispano-cubana-norteamericana.'),
            ('1910', 'Se inaugura el ferrocarril Holguín-Sagua-La Habana.'),
            ('1923', 'Fundación del Colegio de La Salle en Holguín.'),
            ('1940', 'Con la nueva Constitución, Holguín gains representation política.'),
            ('1953', 'Combatientes holguineros participan en el asalto al Moncada.'),
            ('1956', '22 de junio: Ataque al cuartel de Holguín por la clandestinidad.'),
            ('1957', 'Se crea el Movimiento 26 de Julio en la provincia.'),
            ('1958', 'Frank País cae en combate en Santiago, afectando la lucha en Holguín.'),
            ('1959', 'Triunfo de la Revolución. Holguín comienza su transformación social.'),
            ('1960', 'Creación de las primeras escuelas rurales y campañas de alfabetización.'),
            ('1961', 'Milicianos holguineros enfrentan la invasión de Girón.'),
            ('1976', 'Con la nueva división político-administrativa, Holguín se convierte en provincia.'),
            ('1976', 'Se funda la Universidad de Holguín "Oscar Lucero Moya".'),
            ('1993', 'Inauguración de la Plaza de la Revolución "Mariana Grajales" en Holguín.'),
            ('2003', 'Inauguración del Parque de la Ciudad "La Periquera" remodelado.'),
            ('2019', 'Holguín celebra el 500 aniversario de su fundación con múltiples actividades.'),
            ('2023', 'Celebración del 70 aniversario del asalto al Moncada con presencia holguinera.'),
        ]
    }
    return render(request, 'efemerides.html', contexto)


def vista_enlaces(request):
    """Página con enlaces a sitios web cubanos de noticias y búsquedas.
    Organizados por categoría para facilitar la navegación."""
    contexto = {
        'categorias': [
            {
                'nombre': 'Noticias Nacionales',
                'sitios': [
                    {'nombre': 'Granma', 'url': 'https://www.granma.cu', 'desc': 'Órgano oficial del PCC'},
                    {'nombre': 'Juventud Rebelde', 'url': 'https://www.juventudrebelde.cu', 'desc': 'Periódico de la juventud'},
                    {'nombre': 'Cubadebate', 'url': 'https://www.cubadebate.cu', 'desc': 'Portal de noticias y análisis'},
                    {'nombre': 'Antimperialista', 'url': 'https://www.antimperialista.cu', 'desc': 'Información alternativa'},
                    {'nombre': 'Portal del CITMA', 'url': 'https://www.citma.gob.cu', 'desc': 'Ciencia, Tecnología y Medio Ambiente'},
                    {'nombre': 'Cubanews', 'url': 'https://www.cubanews.acn.cu', 'desc': 'Agencia de Noticias de Cuba'},
                    {'nombre': 'ACN', 'url': 'https://www.acn.cu', 'desc': 'Agencia Cubana de Noticias'},
                    {'nombre': 'Prensa Latina', 'url': 'https://www.prensalatina.cu', 'desc': 'Agencia de noticias internacional'},
                    {'nombre': 'TVCubana', 'url': 'https://www.tvcubana.icrt.cu', 'desc': 'Televisión Cubana'},
                    {'nombre': 'Radio Rebelde', 'url': 'https://www.radiorebelde.cu', 'desc': 'Emisora radial'},
                ]
            },
            {
                'nombre': 'Noticias Provinciales',
                'sitios': [
                    {'nombre': 'AHora.cu', 'url': 'https://www.ahora.cu', 'desc': 'Noticias de Holguín'},
                    {'nombre': 'Telecristal', 'url': 'http://www.telecristal.icrt.cu', 'desc': 'TV Holguín'},
                    {'nombre': 'Radio Holguín', 'url': 'https://www.radioholguin.cu', 'desc': 'Emisora de Holguín'},
                    {'nombre': 'Adelante', 'url': 'https://www.adelante.cu', 'desc': 'Noticias de Villa Clara'},
                    {'nombre': '5 de Septiembre', 'url': 'https://www.5septiembre.cu', 'desc': 'Noticias de Cienfuegos'},
                    {'nombre': 'Escambray', 'url': 'https://www.escambray.cu', 'desc': 'Noticias de Sancti Spíritus'},
                    {'nombre': 'Periódico 26', 'url': 'https://www.26digital.cu', 'desc': 'Noticias de Granma'},
                    {'nombre': 'Venceremos', 'url': 'https://www.venceremos.cu', 'desc': 'Noticias de Pinar del Río'},
                ]
            },
            {
                'nombre': 'Buscadores y Portales Cubanos',
                'sitios': [
                    {'nombre': 'EcuRed', 'url': 'https://www.ecured.cu', 'desc': 'Enciclopedia colaborativa cubana'},
                    {'nombre': 'Cubasí', 'url': 'https://www.cubasi.cu', 'desc': 'Portal generalista cubano'},
                    {'nombre': 'Portal Cuba', 'url': 'https://www.portalcuba.cu', 'desc': 'Directorio de sitios cubanos'},
                    {'nombre': 'La Jiribilla', 'url': 'https://www.lajiribilla.cu', 'desc': 'Revista de cultura'},
                    {'nombre': 'Cubaliteraria', 'url': 'https://www.cubaliteraria.cu', 'desc': 'Portal de literatura cubana'},
                ]
            },
            {
                'nombre': 'Instituciones y Gobierno',
                'sitios': [
                    {'nombre': 'Asamblea Nacional', 'url': 'https://www.parlamentocubano.gob.cu', 'desc': 'Parlamento cubano'},
                    {'nombre': 'MINCOM', 'url': 'https://www.mincom.gob.cu', 'desc': 'Ministerio de Comunicaciones'},
                    {'nombre': 'MIC', 'url': 'https://www.mic.cu', 'desc': 'Ministerio de Informática y Comunicaciones'},
                    {'nombre': 'UPEC', 'url': 'https://www.upec.cu', 'desc': 'Unión de Periodistas de Cuba'},
                    {'nombre': 'ONEI', 'url': 'https://www.onei.gob.cu', 'desc': 'Oficina Nacional de Estadística'},
                    {'nombre': 'Desoft', 'url': 'https://www.desoft.cu', 'desc': 'Empresa de desarrollo de software'},
                    {'nombre': 'ETECSA', 'url': 'https://www.etecsa.cu', 'desc': 'Telecomunicaciones de Cuba'},
                    {'nombre': 'INFOMED', 'url': 'https://www.infomed.sld.cu', 'desc': 'Red de salud de Cuba'},
                    {'nombre': 'MES', 'url': 'https://www.mes.gob.cu', 'desc': 'Ministerio de Educación Superior'},
                    {'nombre': 'MINED', 'url': 'https://www.mined.gob.cu', 'desc': 'Ministerio de Educación'},
                ]
            },
            {
                'nombre': 'Cultura y Deporte',
                'sitios': [
                    {'nombre': 'Cubacine', 'url': 'https://www.cubacine.cu', 'desc': 'Instituto Cubano del Arte e Industria Cinematográficos'},
                    {'nombre': 'ICRT', 'url': 'https://www.icrt.cu', 'desc': 'Instituto Cubano de Radio y Televisión'},
                    {'nombre': 'INDER', 'url': 'https://www.inder.gob.cu', 'desc': 'Instituto Nacional de Deportes'},
                    {'nombre': 'Casas de Cultura', 'url': 'https://www.casadelacultura.cu', 'desc': 'Red de casas de cultura'},
                    {'nombre': 'Biblioteca Nacional', 'url': 'https://www.bnjm.cu', 'desc': 'Biblioteca Nacional José Martí'},
                ]
            },
        ]
    }
    return render(request, 'enlaces.html', contexto)


# ══════════════════════════════════════════════════════════════
# VISTAS DE AUTENTICACIÓN
# ══════════════════════════════════════════════════════════════
def vista_login(request):
    """Vista de inicio de sesión CON:
    - Bloqueo por intentos fallidos (5 intentos, 30 min)
    - Verificación de cuenta bloqueada
    - Flujo de 2FA si está activado
    - Registro de sesión y auditoría
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Si viene de verificar 2FA, no mostrar el formulario de login
    if request.GET.get('2fa_error'):
        messages.error(request, 'Código de verificación incorrecto. Intente de nuevo.')

    if request.method == 'POST':
        form = FormularioLogin(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.is_active:
                perfil = user.perfil
                
                # ── Verificar si la cuenta está bloqueada ──
                if esta_bloqueado(perfil):
                    restante = perfil.bloqueado_hasta - timezone.now()
                    minutos = int(restante.total_seconds() // 60) + 1
                    registrar_auditoria(request, 'cuenta_bloqueada', 'auth.User', user.id,
                        f'Cuenta bloqueada. Intentando acceder durante bloqueo ({minutos} min restantes).')
                    form.add_error(None, f'Cuenta bloqueada por intentos fallidos. '
                                      f'Intente de nuevo en {minutos} minutos.')
                else:
                    # ── Login exitoso: reiniciar intentos ──
                    reiniciar_intentos(perfil)
                    
                    # ── Verificar 2FA ──
                    if perfil.activado_2fa:
                        # No hacer login completo aún, guardar temp y pedir código
                        request.session['temp_2fa_user_id'] = user.id
                        # Registrar sesión (se actualizará con cierre al verificar)
                        SesionUsuario.objects.create(
                            user=user, direccion_ip=obtener_ip(request),
                            navegador=obtener_navegador(request),
                            sistema_operativo=obtener_so(request),
                            dispositivo=obtener_dispositivo(request),
                            exitosa=False,  # Se marcará true al verificar 2FA
                        )
                        return redirect('verificar_2fa')
                    
                    # ── Login completo (sin 2FA) ──
                    login(request, user)
                    SesionUsuario.objects.create(
                        user=user, direccion_ip=obtener_ip(request),
                        navegador=obtener_navegador(request),
                        sistema_operativo=obtener_so(request),
                        dispositivo=obtener_dispositivo(request),
                        exitosa=True,
                    )
                    registrar_auditoria(request, 'login', 'auth.User', user.id,
                        f'Login exitoso desde {obtener_ip(request)}')
                    
                    # Verificar expiración de contraseña después del login
                    if perfil.fecha_ultimo_cambio_password and perfil.dias_expiracion_password > 0:
                        vence = perfil.fecha_ultimo_cambio_password + timedelta(days=perfil.dias_expiracion_password)
                        if timezone.now() > vence:
                            registrar_auditoria(request, 'password_expirada', 'auth.User', user.id,
                                'Contraseña expirada, redirigido a cambiar contraseña.')
                            return redirect('cambiar_password')
                    
                    messages.success(request, f'Bienvenido, {user.perfil.nombre_completo}')
                    next_url = request.GET.get('next')
                    return redirect(next_url if next_url else 'dashboard')
            else:
                # ── Login fallido ──
                if user is not None and not user.is_active:
                    form.add_error(None, 'Cuenta desactivada. Contacte al administrador.')
                else:
                    # Incrementar intentos fallidos
                    try:
                        perfil = User.objects.get(username=username).perfil
                        perfil.intentos_fallidos_login += 1
                        
                        # Bloquear después de 5 intentos
                        if perfil.intentos_fallidos_login >= 5:
                            bloquear_cuenta(perfil, 30)
                            registrar_auditoria(request, 'cuenta_bloqueada', 'auth.User',
                                f'Bloqueada tras 5 intentos fallidos desde IP {obtener_ip(request)}')
                            form.add_error(None, 'Cuenta bloqueada por 5 intentos fallidos. '
                                              'Espere 30 minutos o contacte al administrador.')
                        else:
                            form.add_error(None, 'Usuario o contraseña incorrectos. '
                                              f'Intento {perfil.intentos_fallidos_login}/5.')
                            registrar_auditoria(request, 'login_fallido', 'auth.User',
                                username, f'Intento fallido desde IP {obtener_ip(request)}')
                        
                        perfil.save()
                    except User.DoesNotExist:
                        form.add_error(None, 'Usuario o contraseña incorrectos.')
                        registrar_auditoria(request, 'login_fallido', '', username,
                            f'Usuario no existe. IP: {obtener_ip(request)}')
        else:
            messages.error(request, 'Revise los datos ingresados.')
    else:
        form = FormularioLogin(request)
    
    return render(request, 'login.html', {'form': form})


def vista_registro(request):
    """Vista de registro de nuevos usuarios.
    Los campos solicitados son: nombre completo, nombre de usuario, cargo,
    departamento y contraseña (dos veces con indicador de fortaleza)."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            form.save()
            if form.is_valid():
                form.save()
                # Registrar en auditoría
                registrar_auditoria(request, 'registro_usuario', 'auth.User',
                    form.instance.id,
                    f'Nuevo usuario: {form.instance.username}, '
                    f'Dept: {form.cleaned_data["departamento"]}')
                messages.success(request, 'Cuenta creada exitosamente.')
                return redirect('login')
            messages.success(
                request, 
                'Cuenta creada exitosamente. Un administrador revisará su registro '
                'y asignará los permisos correspondientes. Puede iniciar sesión.'
            )
            return redirect('login')
    else:
        form = FormularioRegistro()
    
    departamentos = Departamento.objects.filter(activo=True)
    return render(request, 'register.html', {
        'form': form,
        'departamentos': departamentos,
    })

@login_requerido
def vista_logout(request):
    """Cierra sesión y registra el cierre en el historial."""
    # Marcar la última sesión abierta como cerrada
    SesionUsuario.objects.filter(
        user=request.user, cierre_sesion__isnull=True
    ).order_by('-fecha_hora').update(cierre_sesion=timezone.now())
    
    registrar_auditoria(request, 'logout', 'auth.User', request.user.id, 'Cierre de sesión')
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')

# ══════════════════════════════════════════════════════════════
# VISTAS PROTEGIDAS (requieren login)
# ══════════════════════════════════════════════════════════════

@login_requerido
def vista_dashboard(request):
    """Panel principal del usuario logueado.
    Muestra resumen de actividad: documentos recientes, equipos,
    notificaciones y accesos rápidos según el rol."""
    usuario = request.user
    perfil = usuario.perfil
    
    # Contar elementos para el dashboard
    total_documentos = Documento.objects.count()
    total_equipos = Equipo.objects.filter(estado='activo').count()
    total_usuarios = User.objects.filter(is_active=True).count()
    notifs_no_leidas = Notificacion.objects.filter(
        destinatario=usuario, leida=False
    ).count()
    
    # Documentos recientes (solo los que el usuario puede ver)
    if perfil.es_admin:
        docs_recientes = Documento.objects.all()[:5]
    else:
        docs_recientes = [
            d for d in Documento.objects.all()[:20]
            if d.puede_ver(usuario)
        ][:5]
    
    # Últimas notificaciones del usuario
    ultimas_notifs = Notificacion.objects.filter(
        destinatario=usuario
    ).order_by('-fecha')[:5]
    
    # Mensajes de chat recientes
    mensajes_recientes = MensajeChat.objects.filter(
        canal='general'
    ).order_by('-fecha')[:10]
    
    contexto = {
        'perfil': perfil,
        'total_documentos': total_documentos,
        'total_equipos': total_equipos,
        'total_usuarios': total_usuarios,
        'notifs_no_leidas': notifs_no_leidas,
        'docs_recientes': docs_recientes,
        'ultimas_notifs': ultimas_notifs,
        'mensajes_recientes': mensajes_recientes,
    }
    return render(request, 'dashboard.html', contexto)


# ══════════════════════════════════════════════════════════════
# VISTAS DE DOCUMENTOS (FTP INTERNO)
# ══════════════════════════════════════════════════════════════

@login_requerido
def vista_documentos(request):
    """Lista de documentos disponibles para el usuario actual.
    Solo muestra los documentos que el usuario tiene permiso de ver
    (según la configuración de visibilidad por departamento)."""
    todos_docs = Documento.objects.all().order_by('-fecha_subida')
    
    # Filtrar documentos que el usuario puede ver
    documentos_visibles = [
        doc for doc in todos_docs
        if doc.puede_ver(request.user)
    ]
    
    return render(request, 'documentos.html', {
        'documentos': documentos_visibles,
    })


@login_requerido
def vista_subir_documento(request):
    """Formulario para subir un nuevo documento.
    Permite configurar la visibilidad: para todos o por departamento."""
    if request.method == 'POST':
        form = FormularioDocumento(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.subido_por = request.user
            doc.nombre_original = request.FILES['archivo'].name
            doc.tamano = request.FILES['archivo'].size
            
            # Detectar tipo MIME
            import mimetypes
            mime, _ = mimetypes.guess_type(doc.nombre_original)
            doc.tipo_mime = mime or 'application/octet-stream'
            
            doc.save()
            form.save_m2m()  # Guardar la relación ManyToMany de departamentos
            
            # Notificar a los usuarios relevantes
            if doc.visible_todos:
                # Notificar a todos los usuarios
                destinatarios = User.objects.filter(is_active=True).exclude(id=request.user.id)
                crear_notificacion(
                    tipo='nuevo_documento',
                    titulo='Nuevo documento disponible',
                    mensaje=f'{request.user.perfil.nombre_completo} subió: {doc.nombre_original}',
                    destinatarios=destinatarios,
                    enlace='/documentos/'
                )
            else:
                # Notificar solo a los usuarios de los departamentos seleccionados
                for dept in doc.departamentos_visibles.all():
                    dests = User.objects.filter(
                        perfil__departamento=dept, is_active=True
                    ).exclude(id=request.user.id)
                    crear_notificacion(
                        tipo='nuevo_documento',
                        titulo='Nuevo documento para su departamento',
                        mensaje=f'{doc.nombre_original} fue compartido con {dept.nombre}',
                        destinatarios=dests,
                        enlace='/documentos/'
                    )
            
            messages.success(request, f'Documento "{doc.nombre_original}" subido correctamente.')
            return redirect('documentos')
    else:
        form = FormularioDocumento()
    
    return render(request, 'subir_documento.html', {'form': form})


@login_requerido
def vista_descargar_documento(request, doc_id):
    """Descarga un documento si el usuario tiene permiso.
    Incrementa el contador de descargas."""
    documento = get_object_or_404(Documento, id=doc_id)
    
    if not documento.puede_ver(request.user):
        messages.error(request, 'No tiene permiso para descargar este documento.')
        return redirect('documentos')
    
    # Incrementar contador de descargas
    documento.descargas += 1
    documento.save()
    
    # Servir el archivo
    response = FileResponse(
        documento.archivo.open('rb'),
        as_attachment=True,
        filename=documento.nombre_original
    )
    return response


@login_requerido
def vista_eliminar_documento(request, doc_id):
    """Elimina un documento (solo el que lo subió o un admin)."""
    documento = get_object_or_404(Documento, id=doc_id)
    
    # Solo el que subió o un admin puede eliminar
    if documento.subido_por != request.user and not request.user.perfil.es_admin:
        messages.error(request, 'Solo puede eliminar documentos que usted subió.')
        return redirect('documentos')
    
    nombre = documento.nombre_original
    documento.archivo.delete(save=False)  # Eliminar archivo físico
    documento.delete()
    messages.success(request, f'Documento "{nombre}" eliminado.')
    return redirect('documentos')


# ══════════════════════════════════════════════════════════════
# VISTAS DEL CHAT INTERNO
# ══════════════════════════════════════════════════════════════

@login_requerido
def vista_chat(request):
    """Vista del chat interno con canal general y privados.
    Retorna la página HTML que carga el chat via AJAX polling."""
    # Obtener usuarios activos para la lista de contactos
    usuarios_activos = User.objects.filter(
        is_active=True
    ).select_related('perfil').exclude(id=request.user.id)
    
    return render(request, 'chat.html', {
        'usuarios_activos': usuarios_activos,
    })


@login_requerido
def api_chat_mensajes(request):
    """API que retorna mensajes del chat vía AJAX.
    Soporta:
    - canal=general: mensajes del canal general
    - canal=privado_X: mensajes de chat privado con usuario X
    - after=timestamp: solo mensajes después de esa fecha (para polling)
    """
    canal = request.GET.get('canal', 'general')
    after = request.GET.get('after', '')
    
    mensajes = MensajeChat.objects.filter(canal=canal)
    
    # Filtrar por fecha para polling (solo mensajes nuevos)
    if after:
        from datetime import datetime
        try:
            fecha_limite = datetime.fromisoformat(after.replace('Z', '+00:00'))
            mensajes = mensajes.filter(fecha__gt=fecha_limite)
        except ValueError:
            pass
    
    # Marcar como leídos
    mensajes.update(leido=True)
    
    datos = [{
        'id': m.id,
        'remitente': m.remitente.username,
        'nombre': m.remitente.perfil.nombre_completo if hasattr(m.remitente, 'perfil') else m.remitente.username,
        'contenido': m.contenido,
        'fecha': m.fecha.isoformat(),
        'es_mio': m.remitente.id == request.user.id,
    } for m in mensajes.order_by('fecha')[:50]]
    
    return JsonResponse({'mensajes': datos})


@login_requerido
def api_chat_enviar(request):
    """API para enviar un mensaje al chat vía AJAX POST.
    Soporta envío al canal general o a un canal privado."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    
    contenido = data.get('mensaje', '').strip()
    canal = data.get('canal', 'general')
    
    if not contenido:
        return JsonResponse({'error': 'Mensaje vacío'}, status=400)
    
    if len(contenido) > 1000:
        return JsonResponse({'error': 'Mensaje demasiado largo (máx. 1000 caracteres)'}, status=400)
    
    # Validar que el canal privado sea válido
    if canal.startswith('privado_'):
        try:
            otro_user_id = int(canal.split('_')[1])
            otro_user = User.objects.get(id=otro_user_id, is_active=True)
            # Normalizar el canal: siempre el ID menor primero
            ids = sorted([request.user.id, otro_user_id])
            canal = f'privado_{ids[0]}_{ids[1]}'
        except (ValueError, User.DoesNotExist):
            return JsonResponse({'error': 'Usuario no válido'}, status=400)
    
    mensaje = MensajeChat.objects.create(
        remitente=request.user,
        canal=canal,
        contenido=contenido,
    )
    
    return JsonResponse({
        'id': mensaje.id,
        'remitente': request.user.username,
        'nombre': request.user.perfil.nombre_completo,
        'contenido': mensaje.contenido,
        'fecha': mensaje.fecha.isoformat(),
        'es_mio': True,
    })


# ══════════════════════════════════════════════════════════════
# VISTAS DE NOTIFICACIONES
# ══════════════════════════════════════════════════════════════

@login_requerido
def vista_notificaciones(request):
    """Lista todas las notificaciones del usuario actual."""
    notificaciones = Notificacion.objects.filter(
        destinatario=request.user
    ).order_by('-fecha')
    
    return render(request, 'notificaciones.html', {
        'notificaciones': notificaciones,
    })


@login_requerido
def api_marcar_notificacion_leida(request, notif_id):
    """Marca una notificación como leída vía AJAX."""
    notif = get_object_or_404(Notificacion, id=notif_id, destinatario=request.user)
    notif.leida = True
    notif.save()
    return JsonResponse({'ok': True})


@login_requerido
def api_marcar_todas_leidas(request):
    """Marca todas las notificaciones del usuario como leídas."""
    Notificacion.objects.filter(destinatario=request.user, leida=False).update(leida=True)
    return JsonResponse({'ok': True})


# ══════════════════════════════════════════════════════════════
# VISTAS ADMINISTRATIVAS (requieren rol admin)
# ══════════════════════════════════════════════════════════════

@admin_requerido
def vista_admin_usuarios(request):
    """Panel de administración de usuarios.
    Lista todos los usuarios con sus perfiles y permite:
    cambiar roles, activar/desactivar y eliminar (excepto root)."""
    usuarios = User.objects.select_related('perfil').all().order_by('-date_joined')
    departamentos = Departamento.objects.filter(activo=True)
    
    return render(request, 'admin_usuarios.html', {
        'usuarios': usuarios,
        'departamentos': departamentos,
    })


@admin_requerido
def api_cambiar_rol(request, user_id):
    """Cambia el rol de un usuario vía AJAX POST.
    Root solo puede ser cambiado por otro root."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    
    nuevo_rol = data.get('rol', '')
    roles_validos = ['usuario', 'admin_red', 'seguridad']
    
    if nuevo_rol not in roles_validos:
        return JsonResponse({'error': 'Rol no válido'}, status=400)
    
    target_user = get_object_or_404(User, id=user_id)
    target_perfil = target_user.perfil
    
    # Solo root puede cambiar roles de admins, y nadie puede cambiar a root via API
    if target_perfil.rol == 'root':
        return JsonResponse({'error': 'No se puede modificar el rol del super administrador'}, status=403)
    
    # Si se está promoviendo a admin, el que ejecuta debe ser root
    if nuevo_rol in ['admin_red', 'seguridad'] and request.user.perfil.rol != 'root':
        return JsonResponse({'error': 'Solo root puede asignar roles de administrador'}, status=403)
    
    target_perfil.rol = nuevo_rol
    target_perfil.save()
    
    return JsonResponse({'ok': True, 'nuevo_rol': nuevo_rol})


@admin_requerido
def api_activar_desactivar_usuario(request, user_id):
    """Activa o desactiva un usuario. Root nunca puede ser desactivado."""
    target_user = get_object_or_404(User, id=user_id)
    
    if target_user.perfil.rol == 'root':
        return JsonResponse({'error': 'No se puede desactivar al super administrador'}, status=403)
    
    target_user.is_active = not target_user.is_active
    target_user.save()
    
    estado = 'activado' if target_user.is_active else 'desactivado'
    return JsonResponse({'ok': True, 'estado': estado})


@admin_requerido
def api_eliminar_usuario(request, user_id):
    """Elimina un usuario. Root NUNCA puede ser eliminado.
    Esto está protegido incluso si alguien intenta hacerlo via API."""
    target_user = get_object_or_404(User, id=user_id)
    
    # Triple verificación: nunca eliminar root
    if target_user.username == 'root' or target_user.perfil.rol == 'root':
        return JsonResponse({'error': 'El super administrador ROOT no puede ser eliminado bajo ninguna circunstancia'}, status=403)
    
    if target_user == request.user:
        return JsonResponse({'error': 'No puede eliminar su propia cuenta'}, status=403)
    
    nombre = target_user.perfil.nombre_completo
    target_user.delete()
    return JsonResponse({'ok': True, 'mensaje': f'Usuario "{nombre}" eliminado correctamente'})


# ══════════════════════════════════════════════════════════════
# VISTAS DE INVENTARIO (requieren rol admin)
# ══════════════════════════════════════════════════════════════

@admin_requerido
def vista_admin_inventario(request):
    """Panel de inventario de equipos y componentes.
    Muestra todos los equipos con filtros por departamento y estado.
    Incluye botón para generar PDF del inventario completo."""
    equipos = Equipo.objects.select_related('departamento').all()
    
    # Filtros opcionales
    filtro_dept = request.GET.get('departamento', '')
    filtro_estado = request.GET.get('estado', '')
    filtro_busqueda = request.GET.get('busqueda', '')
    
    if filtro_dept:
        equipos = equipos.filter(departamento_id=filtro_dept)
    if filtro_estado:
        equipos = equipos.filter(estado=filtro_estado)
    if filtro_busqueda:
        from django.db.models import Q
        equipos = equipos.filter(
            Q(identificacion__icontains=filtro_busqueda) |
            Q(marca__icontains=filtro_busqueda) |
            Q(modelo__icontains=filtro_busqueda) |
            Q(ubicacion__icontains=filtro_busqueda) |
            Q(responsable__icontains=filtro_busqueda)
        )
    
    departamentos = Departamento.objects.filter(activo=True)
    
    # Obtener conteo de componentes por equipo (optimizado)
    from django.db.models import Count
    equipos = equipos.annotate(num_componentes=Count('componentes'))
    
    return render(request, 'admin_inventario.html', {
        'equipos': equipos,
        'departamentos': departamentos,
        'filtro_dept': filtro_dept,
        'filtro_estado': filtro_estado,
        'filtro_busqueda': filtro_busqueda,
    })


@admin_requerido
def vista_agregar_equipo(request):
    """Formulario para registrar un nuevo equipo en el inventario."""
    if request.method == 'POST':
        form = FormularioEquipo(request.POST)
        if form.is_valid():
            equipo = form.save(commit=False)
            equipo.registrado_por = request.user
            equipo.save()
            
            messages.success(request, f'Equipo "{equipo.identificacion}" registrado correctamente.')
            return redirect('admin_inventario')
    else:
        form = FormularioEquipo()
    
    departamentos = Departamento.objects.filter(activo=True)
    return render(request, 'agregar_equipo.html', {
        'form': form,
        'departamentos': departamentos,
    })


@admin_requerido
def vista_editar_equipo(request, equipo_id):
    """Edita un equipo existente y sus componentes.
    Detecta cambios en los componentes y genera alertas/historial."""
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    if request.method == 'POST':
        form = FormularioEquipo(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Equipo "{equipo.identificacion}" actualizado.')
            return redirect('admin_inventario')
    else:
        form = FormularioEquipo(instance=equipo)
    
    componentes = equipo.componentes.all()
    form_componente = FormularioComponente()
    
    # Historial de cambios de este equipo
    historial = HistorialComponente.objects.filter(
        equipo=equipo
    ).select_related('componente', 'registrado_por').order_by('-fecha')[:20]
    
    return render(request, 'editar_equipo.html', {
        'equipo': equipo,
        'form': form,
        'componentes': componentes,
        'form_componente': form_componente,
        'historial': historial,
    })


@admin_requerido
def api_agregar_componente(request, equipo_id):
    """Agrega un componente a un equipo vía AJAX POST.
    Registra en el historial y notifica a los administradores si se detecta algo sospechoso."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    equipo = get_object_or_404(Equipo, id=equipo_id)
    form = FormularioComponente(request.POST)
    
    if form.is_valid():
        componente = form.save(commit=False)
        componente.equipo = equipo
        componente.save()
        
        # Registrar en historial
        HistorialComponente.objects.create(
            componente=componente,
            equipo=equipo,
            accion='creado',
            valor_nuevo=componente.obtener_descripcion_completa(),
            registrado_por=request.user,
        )
        
        return JsonResponse({
            'ok': True,
            'id': componente.id,
            'tipo': componente.get_tipo_display(),
            'marca': componente.marca,
            'modelo': componente.modelo,
            'especificaciones': componente.especificaciones,
            'capacidad': componente.capacidad,
            'numero_serie': componente.numero_serie,
            'estado': componente.get_estado_display(),
        })
    
    errores = {campo: error[0] for campo, error in form.errors.items()}
    return JsonResponse({'error': errores}, status=400)


@admin_requerido
def api_editar_componente(request, comp_id):
    """Edita un componente existente vía AJAX POST.
    COMPARA el estado anterior con el nuevo y, si hay diferencias,
    crea una notificación de alerta para todos los administradores.
    Esto es el corazón del sistema de monitoreo de hardware."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    componente = get_object_or_404(Componente, id=comp_id)
    
    # Guardar estado ANTES de la modificación
    estado_anterior = componente.obtener_descripcion_completa()
    
    form = FormularioComponente(request.POST, instance=componente)
    
    if form.is_valid():
        componente_modificada = form.save()
        
        # Guardar estado DESPUÉS de la modificación
        estado_nuevo = componente_modificada.obtener_descripcion_completa()
        
        # Detectar qué campos cambiaron
        campos_cambiados = []
        for field in ['tipo', 'marca', 'modelo', 'especificaciones', 
                      'numero_serie', 'capacidad', 'estado']:
            valor_viejo = str(getattr(componente, field))  # Ya guardado
            # Usar initial para el valor original
        # Mejor: comparar las descripciones completas
        if estado_anterior != estado_nuevo:
            campos_cambiados.append('Múltiples campos modificados')
        
        # Registrar en historial SI hubo cambios
        if estado_anterior != estado_nuevo:
            HistorialComponente.objects.create(
                componente=componente_modificada,
                equipo=componente_modificada.equipo,
                accion='modificado',
                valor_anterior=estado_anterior,
                valor_nuevo=estado_nuevo,
                campos_cambiados='; '.join(campos_cambiados) if campos_cambiados else '',
                registrado_por=request.user,
            )
            
            # NOTIFICAR a todos los admins sobre el cambio
            detectar_cambios_componente(componente_modificada, request.user)
        
        return JsonResponse({
            'ok': True,
            'tipo': componente_modificada.get_tipo_display(),
            'marca': componente_modificada.marca,
            'modelo': componente_modificada.modelo,
            'especificaciones': componente_modificada.especificaciones,
            'capacidad': componente_modificada.capacidad,
            'numero_serie': componente_modificada.numero_serie,
            'estado': componente_modificada.get_estado_display(),
        })
    
    errores = {campo: error[0] for campo, error in form.errors.items()}
    return JsonResponse({'error': errores}, status=400)


@admin_requerido
def api_eliminar_componente(request, comp_id):
    """Elimina un componente y registra el cambio en el historial."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    componente = get_object_or_404(Componente, id=comp_id)
    
    # Registrar eliminación en historial ANTES de borrar
    HistorialComponente.objects.create(
        equipo=componente.equipo,
        accion='eliminado',
        valor_anterior=componente.obtener_descripcion_completa(),
        registrado_por=request.user,
    )
    
    tipo_display = componente.get_tipo_display()
    equipo_id = componente.equipo.id
    componente.delete()
    
    return JsonResponse({
        'ok': True, 
        'mensaje': f'{tipo_display} eliminado del equipo',
        'equipo_id': equipo_id,
    })


@admin_requerido
def vista_descargar_pdf_inventario(request):
    """Genera y descarga el inventario en formato PDF.
    Permite filtrar por departamento si se pasa el parámetro."""
    dept_id = request.GET.get('departamento', '')
    departamento = None
    
    if dept_id:
        departamento = get_object_or_404(Departamento, id=dept_id)
    
    # Generar el PDF usando la utilidad
    pdf_buffer = generar_pdf_inventario(departamento=departamento)
    
    # Nombre del archivo
    nombre_archivo = 'Inventario_Equipos'
    if departamento:
        nombre_archivo += f'_{departamento.nombre.replace(" ", "_")}'
    nombre_archivo += f'_{timezone.now().strftime("%Y%m%d")}.pdf'
    
    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    return response


@admin_requerido
def api_eliminar_equipo(request, equipo_id):
    """Elimina un equipo y todos sus componentes del inventario."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    equipo = get_object_or_404(Equipo, id=equipo_id)
    identificacion = equipo.identificacion
    
    # Registrar eliminación de todos los componentes en historial
    for comp in equipo.componentes.all():
        HistorialComponente.objects.create(
            equipo=equipo,
            accion='eliminado',
            valor_anterior=comp.obtener_descripcion_completa(),
            registrado_por=request.user,
        )
    
    equipo.delete()
    return JsonResponse({'ok': True, 'mensaje': f'Equipo "{identificacion}" eliminado'})

def vista_manual(request):
    """Renderiza el manual como plantilla de Django."""
    return render(request, 'manual.html')

# ══════════════════════════════════════════════════════════════
# VISTAS DE SEGURIDAD AVANZADA
# ══════════════════════════════════════════════════════════════

@login_requerido
def vista_verificar_2fa(request):
    """Página donde el usuario ingresa el código TOTP de 6 dígitos."""
    user_id = request.session.get('temp_2fa_user_id')
    if not user_id:
        messages.error(request, 'Sesión inválida. Inicie sesión nuevamente.')
        return redirect('login')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')
    
    if request.method == 'POST':
        form = FormularioVerificar2FA(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            totp = pyotp.TOTP(user.perfil.secret_2fa)
            
            if totp.verify(codigo, valid_window=1):
                # Código correcto: completar login
                del request.session['temp_2fa_user_id']
                login(request, user)
                
                # Actualizar la sesión como exitosa
                SesionUsuario.objects.filter(
                    user=user, cierre_sesion__isnull=True
                ).order_by('-fecha_hora').update(exitosa=True)
                
                registrar_auditoria(request, 'login', 'auth.User', user.id,
                    f'Login con 2FA exitoso desde {obtener_ip(request)}')
                
                # Actualizar fecha de cambio de password si es el primer login con 2FA
                if not user.perfil.fecha_ultimo_cambio_password:
                    user.perfil.fecha_ultimo_cambio_password = timezone.now()
                    user.perfil.save()
                
                messages.success(request, f'Bienvenido, {user.perfil.nombre_completo}')
                return redirect('dashboard')
            else:
                messages.error(request, 'Código incorrecto. Intente de nuevo.')
    else:
        form = FormularioVerificar2FA()
    
    return render(request, 'verificar_2fa.html', {'form': form, 'user': user})


@login_requerido
def vista_setup_2fa(request):
    """Página para activar 2FA: muestra QR y clave para escanear."""
    perfil = request.user.perfil
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '')
        
        if perfil.secret_2fa and codigo:
            totp = pyotp.TOTP(perfil.secret_2fa)
            if totp.verify(codigo, valid_window=1):
                perfil.activado_2fa = True
                if not perfil.fecha_ultimo_cambio_password:
                    perfil.fecha_ultimo_cambio_password = timezone.now()
                perfil.save()
                
                registrar_auditoria(request, '2fa_activada', 'core.Perfil', perfil.id,
                    'Autenticación de dos factores activada')
                
                messages.success(request, '2FA activada correctamente. '
                                 'En cada login deberá ingresar el código de su app authenticator.')
                return redirect('dashboard')
            else:
                messages.error(request, 'Código incorrecto. Verifique que su app muestre el código correcto.')
    
    # Generar secreto TOTP si no existe
    if not perfil.secret_2fa:
        perfil.secret_2fa = pyotp.random_base32()
        perfil.save()
    
    # Generar URI otpauth://totp/
    uri = pyotp.totp.TOTP(perfil.secret_2fa).provisioning_uri(
        name=f'SuiteSeg:{request.user.username}',
        issuer_name='SuiteSeg.cu'
    )
    
    # Generar QR code como imagen PNG base64 (fondo oscuro, QR cyan)
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#00f5d4", back_color="#0c1220")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    qr_img_tag = f'<img src="data:image/png;base64,{qr_base64}" alt="QR 2FA" style="border-radius:8px;">'
    
    return render(request, 'setup_2fa.html', {
        'perfil': perfil,
        'qr_img': qr_img_tag,
        'secret_key': perfil.secret_2fa,
        'uri': uri,
    })


@login_requerido
def vista_desactivar_2fa(request):
    """Desactiva 2FA para el usuario actual."""
    if request.method == 'POST':
        perfil = request.user.perfil
        if perfil.activado_2fa:
            perfil.activado_2fa = False
            perfil.secret_2fa = ''
            perfil.save()
            registrar_auditoria(request, '2fa_desactivada', 'core.Perfil', perfil.id,
                '2FA desactivada por el usuario')
            messages.success(request, '2FA desactivada.')
        return redirect('dashboard')
    return redirect('setup_2fa')


@login_requerido
def vista_cambiar_password(request):
    """Página para cambiar la contraseña (forzada o voluntaria)."""
    if request.method == 'POST':
        form = FormularioCambiarPassword(request.POST)
        if form.is_valid():
            actual = form.cleaned_data['password_actual']
            nueva = form.cleaned_data['password_nueva']
            
            # Verificar contraseña actual
            if not request.user.check_password(actual):
                form.add_error('password_actual', 'Contraseña actual incorrecta.')
            else:
                # Cambiar la contraseña
                request.user.set_password(nueva)
                request.user.save()
                
                # Actualizar fecha de último cambio
                perfil = request.user.perfil
                perfil.fecha_ultimo_cambio_password = timezone.now()
                perfil.intentos_fallidos_login = 0
                perfil.bloqueado_hasta = None
                perfil.save()
                
                registrar_auditoria(request, 'cambiar_password', 'auth.User', request.user.id,
                    'Contraseña cambiada exitosamente')
                
                messages.success(request, 'Contraseña actualizada correctamente.')
                return redirect('dashboard')
    else:
        form = FormularioCambiarPassword()
    
    # Calcular días restantes para mostrar en la página
    perfil = request.user.perfil
    dias_restantes = dias_para_expirar(perfil)
    
    return render(request, 'cambiar_password.html', {
        'form': form,
        'dias_restantes': dias_restantes,
        'dias_configurados': perfil.dias_expiracion_password,
    })


@admin_requerido
def vista_sesiones(request):
    """Panel de historial de sesiones. Admin ve todas, usuario solo las suyas."""
    if request.user.perfil.rol == 'root' or request.user.perfil.rol in ['admin_red', 'seguridad']:
        sesiones = SesionUsuario.objects.select_related('user').all()[:100]
        titulo = 'Historial de Sesiones — Todos los usuarios'
    else:
        sesiones = SesionUsuario.objects.filter(user=request.user)[:50]
        titulo = 'Mi Historial de Sesiones'
    
    return render(request, 'sesiones.html', {
        'sesiones': sesiones,
        'titulo': titulo,
    })


@admin_requerido
def vista_auditoria(request):
    """Panel de registro de auditoría (solo admins). Registros inmutables."""
    registros = RegistroAuditoria.objects.select_related('usuario').all()[:200]
    
    # Filtros opcionales
    filtro_accion = request.GET.get('accion', '')
    filtro_usuario = request.GET.get('usuario', '')
    filtro_fecha = request.GET.get('fecha', '')
    
    if filtro_accion:
        registros = registros.filter(accion=filtro_accion)
    if filtro_usuario:
        registros = registros.filter(usuario__username__icontains=filtro_usuario)
    if filtro_fecha:
        registros = registros.filter(fecha__date=filtro_fecha)
    
    return render(request, 'auditoria.html', {
        'registros': registros,
        'acciones': RegistroAuditoria.ACCIONES,
        'filtro_accion': filtro_accion,
        'filtro_usuario': filtro_usuario,
        'filtro_fecha': filtro_fecha,
    })

@admin_requerido
def api_estadisticas_dashboard(request):
    """API que retorna datos en formato JSON para los gráficos de Chart.js"""
    from django.db.models import Count
    from django.db.models.functions import TruncMonth
    from datetime import timedelta
    
    # 1. Equipos por Departamento (Para gráfico de torta/dona)
    equipos_dept = Equipo.objects.values('departamento__nombre').annotate(total=Count('id'))
    
    # 2. Tickets por Prioridad (Para gráfico de barras)
    tickets_pri = Ticket.objects.values('prioridad').annotate(total=Count('id'))
    
    # 3. Documentos subidos por mes (Últimos 6 meses para gráfico de línea)
    hace_6_meses = timezone.now() - timedelta(days=180)
    docs_mes = Documento.objects.filter(fecha_subida__gte=hace_6_meses).annotate(
        mes=TruncMonth('fecha_subida')
    ).values('mes').annotate(total=Count('id')).order_by('mes')
    
    return JsonResponse({
        'equipos_dept': list(equipos_dept),
        'tickets_pri': list(tickets_pri),
        'docs_mes': [{'mes': d['mes'].strftime('%Y-%m'), 'total': d['total']} for d in docs_mes]
    })

@login_requerido
def vista_tickets(request):
    """Lista todos los tickets. Admins ven todos, usuarios solo los suyos."""
    if request.user.perfil.es_admin:
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(creador=request.user)
    return render(request, 'tickets.html', {'tickets': tickets})

@login_requerido
def vista_crear_ticket(request):
    if request.method == 'POST':
        form = FormularioTicket(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.creador = request.user
            ticket.save()
            # Notificar a los admins
            crear_notificacion('nuevo_ticket', 'Nuevo Ticket de Soporte', f'{ticket.titulo}', 
                              User.objects.filter(perfil__es_admin=True), enlace=f'/tickets/{ticket.id}/')
            messages.success(request, 'Ticket creado correctamente.')
            return redirect('tickets')
    else:
        form = FormularioTicket()
    return render(request, 'crear_ticket.html', {'form': form})

@login_requerido
def vista_detalle_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    mensajes = ticket.mensajes.select_related('autor').all()
    
    if request.method == 'POST':
        form = FormularioMensajeTicket(request.POST)
        if form.is_valid():
            MensajeTicket.objects.create(
                ticket=ticket, autor=request.user, contenido=form.cleaned_data['contenido']
            )
            if ticket.estado == 'espera': ticket.estado = 'en_progreso'
            ticket.save()
            registrar_auditoria(request, 'crear_ticket', 'Ticket', ticket.id, 
                f'Ticket nuevo: {ticket.titulo} (Prioridad: {ticket.prioridad})')
            return redirect('detalle_ticket', ticket_id=ticket.id)
    else:
        form = FormularioMensajeTicket()
    return render(request, 'detalle_ticket.html', {'ticket': ticket, 'mensajes': mensajes, 'form': form})

# ═══════════════════════════════════════════════════
# MÓDULO DE CAPACITACIÓN
# ═══════════════════════════════════════════════════
@login_requerido
def vista_cursos(request):
    """Lista los cursos disponibles. Muestra si el usuario ya aprobó cuál."""
    cursos = CursoCapacitacion.objects.all()
    # Obtener IDs de cursos ya aprobados por el usuario actual
    evaluaciones = EvaluacionCurso.objects.filter(usuario=request.user, aprobado=True).values_list('curso_id', flat=True)
    
    return render(request, 'cursos.html', {
        'cursos': cursos,
        'cursos_aprobados': list(evaluaciones)
    })

@login_requerido
def vista_tomar_curso(request, curso_id):
    curso = get_object_or_404(CursoCapacitacion, id=curso_id)
    
    try:
        preguntas_lista = json.loads(curso.preguntas)
    except:
        preguntas_lista = []
        
    preguntas_con_indice = [
        {'indice': i, 'p': p.get('p', ''), 'o': p.get('o', []), 'r': p.get('r', 0)} 
        for i, p in enumerate(preguntas_lista)
    ]
    
    ya_aprobado = EvaluacionCurso.objects.filter(curso=curso, usuario=request.user, aprobado=True).exists()
    
    return render(request, 'tomar_curso.html', {
        'curso': curso,
        'preguntas': preguntas_con_indice,
        'total_preguntas': len(preguntas_con_indice), # <-- AGREGAR ESTA LÍNEA
        'ya_aprobado': ya_aprobado
    })

@login_requerido
def api_guardar_evaluacion(request, curso_id):
    """Recibe las respuestas via AJAX POST, calcula la nota y guarda"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    curso = get_object_or_404(CursoCapacitacion, id=curso_id)
    data = json.loads(request.body)
    respuestas = data.get('respuestas', {})
    
    # CONVERTIR TEXTO A LISTA PYTHON
    try:
        preguntas_lista = json.loads(curso.preguntas)
    except:
        preguntas_lista = []
        
    # Calcular nota
    total = len(preguntas_lista)
    correctas = 0
    for i, pregunta in enumerate(preguntas_lista):
        if str(respuestas.get(str(i))) == str(pregunta.get('r')):
            correctas += 1
            
    calificacion = int((correctas / total) * 100) if total > 0 else 0
    aprobado = calificacion >= 70
    
    # CONVERTIR LISTA A TEXTO PARA GUARDAR EN BD
    respuestas_texto = json.dumps(respuestas)
    
    evaluacion, created = EvaluacionCurso.objects.update_or_create(
        curso=curso, usuario=request.user,
        defaults={'calificacion': calificacion, 'aprobado': aprobado, 'respuestas': respuestas_texto}
    )
    
    return JsonResponse({
        'ok': True, 'calificacion': calificacion, 'correctas': correctas, 
        'total': total, 'aprobado': aprobado
    })

# ═══════════════════════════════════════════════════
# GESTIÓN DE POLÍTICAS CON VENCIMIENTO
# ═══════════════════════════════════════════════════
@admin_requerido
def vista_politicas(request):
    """Lista todas las políticas calculando su estado dinámicamente"""
    hoy = date.today()
    politicas = PoliticaSeguridad.objects.all().order_by('fecha_vigencia')
    
    # Calcular estado dinámicamente según la fecha
    for p in politicas:
        dias_restantes = (p.fecha_vigencia - hoy).days
        if dias_restantes < 0:
            p.estado_calculado = 'vencida'
            p.dias_restantes = abs(dias_restantes)
        elif dias_restantes <= 30:
            p.estado_calculado = 'por_vencer'
            p.dias_restantes = dias_restantes
        else:
            p.estado_calculado = 'vigente'
            p.dias_restantes = dias_restantes
            
    return render(request, 'politicas.html', {'politicas': politicas})

@admin_requerido
def vista_crear_politica(request):
    """Formulario para crear una nueva política"""
    if request.method == 'POST':
        form = FormularioPolitica(request.POST)
        if form.is_valid():
            politica = form.save(commit=False)
            politica.creado_por = request.user
            politica.save()
            messages.success(request, f'Política "{politica.nombre}" creada correctamente.')
            return redirect('politicas')
    else:
        form = FormularioPolitica()
    return render(request, 'crear_politica.html', {'form': form})

@admin_requerido
def vista_detalle_politica(request, pol_id):
    """Ver detalle de la política y option a editarla"""
    politica = get_object_or_404(PoliticaSeguridad, id=pol_id)
    
    if request.method == 'POST':
        form = FormularioPolitica(request.POST, instance=politica)
        if form.is_valid():
            form.save()
            messages.success(request, 'Política actualizada y fecha de vigencia reiniciada.')
            return redirect('politicas')
    else:
        form = FormularioPolitica(instance=politica)
        
    return render(request, 'detalle_politica.html', {'politica': politica, 'form': form})

# ═══════════════════════════════════════════════════
# CRUD ADMINISTRADOR (Cursos y Políticas)
# ═══════════════════════════════════════════════════
@admin_requerido
def vista_admin_cursos(request):
    """Vista principal del CRUD de Cursos."""
    cursos = CursoCapacitacion.objects.all().order_by('-id')
    
    if request.method == 'POST':
        curso_id = request.POST.get('curso_id') 
        if curso_id:
            curso = get_object_or_404(CursoCapacitacion, id=curso_id)
            form = FormularioCurso(request.POST, instance=curso)
        else:
            form = FormularioCurso(request.POST)
            
        if form.is_valid():
            curso_guardado = form.save()
            registrar_auditoria(request, 'crear_curso', 'CursoCapacitacion', curso_guardado.id, 
                f'Curso creado/actualizado: {curso_guardado.titulo} ({curso_guardado.preguntas|length} preguntas)')
            messages.success(request, 'Curso guardado correctamente.')
        else:
            messages.error(request, 'Revise los errores en el formulario.')
            
    else:
        form = FormularioCurso()
        
    # Calcular el número real de preguntas para cada curso
    for curso in cursos:
        try:
            curso.num_preguntas = len(json.loads(curso.preguntas))
        except:
            curso.num_preguntas = 0
        
    return render(request, 'admin_cursos.html', {
        'cursos': cursos, 
        'form': form,
        'total_cursos': cursos.count()
    })

@admin_requerido
def api_eliminar_curso(request, curso_id):
    """Elimina un curso vía AJAX. Retorna JSON."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        curso = get_object_or_404(CursoCapacitacion, id=curso_id)
        nombre_curso = curso.titulo
        registrar_auditoria(request, 'eliminar_curso', 'CursoCapacitacion', curso_id, 
            f'Curso eliminado permanentemente: {nombre_curso}')
        curso.delete()
        return JsonResponse({'ok': True, 'mensaje': 'Curso eliminado.'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@admin_requerido
def vista_admin_politicas(request):
    """Lista todas las políticas calculando su estado dinámicamente."""
    hoy = date.today()
    fecha_limite = hoy + timedelta(days=30)
    politicas = PoliticaSeguridad.objects.all().order_by('fecha_vigencia')
    
    if request.method == 'POST':
        pol_id = request.POST.get('pol_id')
        if pol_id:
            politica = get_object_or_404(PoliticaSeguridad, id=pol_id)
            form = FormularioPolitica(request.POST, instance=politica)
        else:
            form = FormularioPolitica(request.POST)
            
        if form.is_valid():
            politica_guardada = form.save(commit=False)
            if not pol_id:
                politica_guardada.creado_por = request.user
            politica_guardada.save()
            
            accion_aud = 'editar_politica' if pol_id else 'crear_politica'
            registrar_auditoria(request, accion_aud, 'PoliticaSeguridad', politica_guardada.id, 
                f'Política: {politica_guardada.nombre} (Vigencia: {politica_guardada.fecha_vigencia})')
            messages.success(request, 'Política guardada correctamente.')
        else:
            messages.error(request, 'Revise los errores en el formulario.')
            
    else:
        form = FormularioPolitica()
        
    return render(request, 'admin_politicas.html', {
        'politicas': politicas, 
        'form': form,
        'hoy': hoy,
        'fecha_limite': fecha_limite
    })

@admin_requerido
def api_eliminar_politica(request, pol_id):
    """Elimina una política vía AJAX."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        politica = get_object_or_404(PoliticaSeguridad, id=pol_id)
        nombre_pol = politica.nombre
        registrar_auditoria(request, 'eliminar_politica', 'PoliticaSeguridad', pol_id, 
            f'Política eliminada permanentemente: {nombre_pol}')
        politica.delete()
        return JsonResponse({'ok': True, 'mensaje': f'Política "{nombre_pol}" eliminada.'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_requerido
def api_datos_curso(request, curso_id):
    curso = get_object_or_404(CursoCapacitacion, id=curso_id)
    
    # CONVERTIR TEXTO A LISTA PARA MANDARLO AL JS
    try:
        preguntas_lista = json.loads(curso.preguntas)
    except:
        preguntas_lista = []
        
    return JsonResponse({
        'id': curso.id,
        'titulo': curso.titulo,
        'descripcion': curso.descripcion,
        'preguntas': preguntas_lista # Aquí mandamos la lista
    })

@login_requerido
def api_datos_politica(request, pol_id):
    """Retorna los datos de una política en JSON para llenar el modal"""
    politica = get_object_or_404(PoliticaSeguridad, id=pol_id)
    return JsonResponse({
        'id': politica.id,
        'nombre': politica.nombre,
        'contenido': politica.contenido,
        'fecha_vigencia': politica.fecha_vigencia.strftime('%Y-%m-%d') # Formato requerido por input type="date"
    })

# ═══════════════════════════════════════════════════
# CRUD DEPARTAMENTOS
# ═══════════════════════════════════════════════════
@admin_requerido
def vista_admin_departamentos(request):
    """Vista principal del CRUD de Departamentos."""
    departamentos = Departamento.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        dep_id = request.POST.get('dep_id') 
        if dep_id:
            dep = get_object_or_404(Departamento, id=dep_id)
            form = FormularioDepartamento(request.POST, instance=dep)
        else:
            form = FormularioDepartamento(request.POST)
            
        if form.is_valid():
            dep_guardado = form.save()
            accion_aud = 'editar_departamento' if dep_id else 'crear_departamento'
            registrar_auditoria(request, accion_aud, 'Departamento', dep_guardado.id, 
                f'Departamento: {dep_guardado.nombre} (Activo: {dep_guardado.activo})')
            messages.success(request, 'Departamento guardado correctamente.')
        else:
            messages.error(request, 'Revise los errores en el formulario.')
            
    else:
        form = FormularioDepartamento()
        
    return render(request, 'admin_departamentos.html', {
        'departamentos': departamentos, 
        'form': form
    })

@admin_requerido
def api_eliminar_departamento(request, dep_id):
    """Elimina un departamento vía AJAX. Protegido por Clave Foránea."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        dep = get_object_or_404(Departamento, id=dep_id)
        nombre_dep = dep.nombre
        registrar_auditoria(request, 'eliminar_departamento', 'Departamento', dep_id, 
            f'Departamento eliminado: {nombre_dep}')
        dep.delete()
        return JsonResponse({'ok': True, 'mensaje': f'Departamento "{nombre_dep}" eliminado.'})
    except Exception as e:
        if 'FOREIGN KEY' in str(e):
            return JsonResponse({'error': 'No se puede eliminar: hay usuarios o equipos asignados a este departamento.'}, status=400)
        return JsonResponse({'error': str(e)}, status=500)

@admin_requerido
def api_datos_departamento(request, dep_id):
    """Retorna los datos de un departamento en JSON para llenar el modal de edición"""
    dep = get_object_or_404(Departamento, id=dep_id)
    return JsonResponse({
        'id': dep.id,
        'nombre': dep.nombre,
        'activo': dep.activo
    })

@admin_requerido
def vista_mapa_red(request):
    """Retorna la página del mapa interactivo. Los datos se cargan vía JSON para vis.js"""
    return render(request, 'mapa_red.html')

@admin_requerido
def api_datos_mapa_red(request):
    """Retorna equipos y nodos para dibujar la topología en vis.js"""
    from django.db.models import Count
    
    # Obtener departamentos con cantidad de equipos
    departamentos = Departamento.objects.filter(activo=True).annotate(
        num_equipos=Count('equipo')
    ).filter(num_equipos__gt=0)
    
    nodes = []
    edges = []
    
    # 1. Crear un nodo central por cada departamento
    for dept in departamentos:
        nodes.append({
            'id': f'dept_{dept.id}',
            'label': dept.nombre,
            'group': 'departamento',
            'shape': 'icon',
            'icon': {
                'face': 'FontAwesome',
                'code': '\uf1ad', # Código de ícono de edificio
                'size': 50,
                'color': '#00bbf9'
            }
        })
    
    # 2. Crear un nodo por cada equipo activo
    equipos = Equipo.objects.filter(estado='activo').select_related('departamento')
    for eq in equipos:
        dept_id_str = f'dept_{eq.departamento.id}' if eq.departamento else None
        
        nodes.append({
            'id': f'eq_{eq.id}',
            'label': f"{eq.identificacion}\n{eq.marca} {eq.modelo}",
            'group': 'equipo',
            'title': f"IP: {eq.direccion_ip or 'N/A'}\nUbicación: {eq.ubicacion or 'N/A'}",
            'shape': 'icon',
            'icon': {
                'face': 'FontAwesome',
                'code': '\uf108', # Código de ícono de computadora
                'size': 35,
                'color': '#00f5d4'
            }
        })
        
        # 3. Crear la línea (edge) que conecta el equipo con su departamento
        if dept_id_str:
            edges.append({
                'from': dept_id_str,
                'to': f'eq_{eq.id}',
                'dashes': True, # Línea punteada
                'color': {'color': '#64748b', 'opacity': 0.5}
            })
            
    return JsonResponse({'nodes': nodes, 'edges': edges})

@admin_requerido
def vista_incidentes(request):
    """Lista principal de incidentes con buscador básico"""
    incidentes = RegistroIncidente.objects.select_related('respondedor').all().order_by('-fecha')
    
    if request.method == 'POST':
        inc_id = request.POST.get('inc_id')
        if inc_id:
            inc = get_object_or_404(RegistroIncidente, id=inc_id)
            form = FormularioIncidente(request.POST, instance=inc)
        else:
            form = FormularioIncidente(request.POST)
            
        if form.is_valid():
            incidente = form.save(commit=False)
            if not inc_id:
                incidente.respondedor = request.user
            incidente.save()
            
            accion_aud = 'editar_incidente' if inc_id else 'crear_incidente'
            registrar_auditoria(request, accion_aud, 'RegistroIncidente', incidente.id, 
                f'Incidente: {incidente.tipo_incidente} (Estado: {incidente.get_estado_display()})')
            messages.success(request, 'Incidente registrado correctamente.')
        else:
            messages.error(request, 'Revise los errores.')
    else:
        form = FormularioIncidente()
        
    return render(request, 'incidentes.html', {'incidentes': incidentes, 'form': form})

@admin_requerido
def api_eliminar_incidente(request, inc_id):
    """Elimina un incidente vía AJAX."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        inc = get_object_or_404(RegistroIncidente, id=inc_id)
        tipo_inc = inc.tipo_incidente
        registrar_auditoria(request, 'eliminar_incidente', 'RegistroIncidente', inc_id, 
            f'Incidente eliminado: {tipo_inc}')
        inc.delete()
        return JsonResponse({'ok': True, 'mensaje': 'Incidente eliminado.'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@admin_requerido
def api_datos_incidente(request, inc_id):
    inc = get_object_or_404(RegistroIncidente, id=inc_id)
    return JsonResponse({
        'id': inc.id, 'tipo_incidente': inc.tipo_incidente, 
        'descripcion': inc.descripcion, 'estado': inc.estado,
        'lecciones_aprendidas': inc.lecciones_aprendidas or ""
    })

# ═══ VISTA QUE RENDERIZA EL HTML ═══
@admin_requerido
def ia_analisis_page(request):
    """Renderiza la página del Centro de IA."""
    return render(request, 'ia_analisis.html')


# ═══ VISTA QUE DEVUELVE EL JSON (API) ═══
@admin_requerido
def api_ia_analisis(request):
    """Motor de IA Basado en Heurísticas."""
    try:
        hace_7_dias = timezone.now() - timedelta(days=7)
        hace_1_hora = timezone.now() - timedelta(hours=1)

        sesiones_totales = SesionUsuario.objects.filter(
            fecha_hora__gte=hace_7_dias, exitosa=True
        ).count()

        logs_fallidos = RegistroAuditoria.objects.filter(
            accion='login_fallido', fecha__gte=hace_1_hora
        ).count()

        cambios_hw = HistorialComponente.objects.filter(
            accion='modificado', fecha__gte=hace_7_dias
        ).count()

        anomalias = []
        puntuacion_riesgo = 0

        # ═══ Anomalía 1: Accesos nocturnos ═══
        # SIN usar __hour — filtramos en Python para evitar el error
        sesiones_recientes = SesionUsuario.objects.filter(
            exitosa=True, fecha_hora__gte=hace_7_dias
        )
        accesos_nocturnos = 0
        for s in sesiones_recientes:
            hora = s.fecha_hora.hour if hasattr(s.fecha_hora, 'hour') else 0
            if hora >= 22 or hora < 6:
                accesos_nocturnos += 1

        if accesos_nocturnos > 5:
            puntuacion_riesgo += 30
            anomalias.append({
                'tipo': 'Acceso Nocturno Excesivo',
                'descripcion': f'{accesos_nocturnos} inicios de sesión fuera del horario laboral (22:00 - 06:00) en los últimos 7 días.',
                'severidad': 'media'
            })

        # ═══ Anomalía 2: Fuerza bruta ═══
        if logs_fallidos >= 5:
            puntuacion_riesgo += 50
            anomalias.append({
                'tipo': 'Posible Ataque de Fuerza Bruta',
                'descripcion': f'{logs_fallidos} intentos de login fallidos en la última hora.',
                'severidad': 'critica'
            })
        elif logs_fallidos > 0:
            puntuacion_riesgo += 15

        # ═══ Anomalía 3: Hardware sospechoso ═══
        if cambios_hw > 10:
            puntuacion_riesgo += 20
            anomalias.append({
                'tipo': 'Actividad Sospechosa de Hardware',
                'descripcion': f'{cambios_hw} modificaciones de componentes en los últimos 7 días (Promedio normal: 1-3).',
                'severidad': 'alta'
            })

        # ═══ Anomalía 4: Eliminación de datos ═══
        logs_eliminacion = RegistroAuditoria.objects.filter(
            accion__icontains='eliminar', fecha__gte=hace_7_dias
        ).count()
        if logs_eliminacion > 0:
            puntuacion_riesgo += 25
            anomalias.append({
                'tipo': 'Eliminación de Datos',
                'descripcion': f'Se registraron {logs_eliminacion} eliminaciones de elementos en la última semana.',
                'severidad': 'alta'
            })

        # ═══ Calcular estado y color ═══
        if puntuacion_riesgo >= 80:
            estado, color = "CRÍTICO", "#ff3860"
        elif puntuacion_riesgo >= 40:
            estado, color = "EN ALERTA", "#fee440"
        else:
            estado, color = "NORMAL", "#00f5a0"

        return JsonResponse({
            'puntuacion': min(puntuacion_riesgo, 100),
            'estado': estado,
            'color': color,
            'anomalias': anomalias,
            'sesiones_totales': sesiones_totales,
            'fallos_ultima_hora': logs_fallidos
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'puntuacion': 0,
            'estado': 'ERROR',
            'color': '#ff3860',
            'anomalias': [],
            'sesiones_totales': 0,
            'fallos_ultima_hora': 0,
            'error_detalle': str(e)
        }, status=500)

@login_requerido
def vista_monitoreo_red(request):
    """Vista que simula tráfico de red. Listo para ser reemplazado por APIs reales."""
    return render(request, 'monitoreo_red.html')
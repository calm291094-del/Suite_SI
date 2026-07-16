"""
Comando para crear datos iniciales del sistema.
Ejecutar: python manage.py crear_datos_iniciales
Crea los departamentos más comunes en una institución cubana.
"""

from django.core.management.base import BaseCommand
from core.models import Departamento


class Command(BaseCommand):
    help = 'Crea departamentos iniciales para el sistema'

    def handle(self, *args, **options):
        departamentos = [
            ('Dirección', 'DIR'),
            ('Dirección de Informática', 'DI'),
            ('Recursos Humanos', 'RRHH'),
            ('Economía y Finanzas', 'ECOFIN'),
            ('Logística', 'LOGIS'),
            ('Investigación y Desarrollo', 'I+D'),
            ('Control Interno', 'CI'),
            ('Departamento Legal', 'LEGAL'),
            ('Capacitación', 'CAP'),
            ('Servicios Técnicos', 'ST'),
            ('Biblioteca', 'BIBL'),
            ('Secretaría General', 'SG'),
            ('Departamento de Calidad', 'CAL'),
            ('Comunicación', 'COMUN'),
            ('Seguridad Física', 'SEGFIS'),
        ]

        creados = 0
        for nombre, codigo in departamentos:
            dept, creado = Departamento.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': nombre, 'activo': True}
            )
            if creado:
                creados += 1
                self.stdout.write(f'  ✓ Creado: {nombre} ({codigo})')
            else:
                self.stdout.write(f'  — Ya existe: {nombre} ({codigo})')

        self.stdout.write(
            self.style.SUCCESS(f'\nProceso completado. {creados} departamentos nuevos creados.')
        )
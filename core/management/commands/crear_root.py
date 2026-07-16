"""
Comando para crear el usuario root.
Ejecutar: python manage.py crear_root
CORREGIDO: Usa update_or_create para no chocar con la señal.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Perfil, Departamento


class Command(BaseCommand):
    help = 'Crea el usuario root'

    def handle(self, *args, **options):
        username = 'root'
        password = '4815162342'

        # Si ya existe, eliminar usuario y su perfil
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING('Eliminando root anterior...'))
            old = User.objects.get(username=username)
            if hasattr(old, 'perfil'):
                old.perfil.delete()
            old.delete()

        # create_superuser guarda el usuario y dispara la señal
        # La señal crea un perfil vacío automáticamente
        root_user = User.objects.create_superuser(
            username=username,
            email='root@suite.local',
            password=password,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )

        # Crear departamento si no existe
        dept, _ = Departamento.objects.get_or_create(
            codigo='SIST',
            defaults={'nombre': 'Dirección de Informática y Sistemas', 'activo': True}
        )

        # ACTUALIZAR el perfil que la señal ya creó (no crear otro)
        Perfil.objects.update_or_create(
            user=root_user,
            defaults={
                'nombre_completo': 'Super Administrador Root',
                'cargo': 'Administrador General del Sistema',
                'departamento': dept,
                'rol': 'root',
                'telefono': 'N/A',
            }
        )

        self.stdout.write(self.style.SUCCESS(
            f'\n  ROOT creado exitosamente.\n'
            f'  Usuario: {username}\n'
            f'  Contraseña: {password}\n'
        ))
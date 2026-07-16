"""
Señales de Django: se ejecutan automáticamente ante ciertos eventos.
Crea el perfil cuando se crea un usuario NUEVO.
Verifica si ya existe antes de crear para evitar duplicados.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Perfil, Notificacion


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Se ejecuta después de guardar un usuario.
    Solo crea perfil si es un usuario NUEVO y NO existe uno ya.
    NOTA: El formulario de registro actualiza este perfil después,
    por eso aquí solo creamos el "esqueleto" vacío."""
    if created:
        # Verificación triple para evitar duplicados
        if not Perfil.objects.filter(user=instance).exists():
            Perfil.objects.create(
                user=instance,
                nombre_completo=instance.username,
                cargo='Sin asignar',
                rol='usuario'
            )


@receiver(post_save, sender=User)
def notificar_nuevo_usuario(sender, instance, created, **kwargs):
    """Notifica a los admins cuando alguien se registra."""
    if created and instance.username != 'root':
        admins = User.objects.filter(
            perfil__rol__in=['root', 'admin_red', 'seguridad']
        ).exclude(id=instance.id)
        for admin in admins:
            if hasattr(admin, 'perfil'):
                Notificacion.objects.create(
                    tipo='nuevo_usuario',
                    titulo='Nuevo usuario registrado',
                    mensaje=f'Se registró: {instance.username}. '
                            f'Asigne rol y departamento si es necesario.',
                    destinatario=admin,
                    enlace='/admin/usuarios/'
                )
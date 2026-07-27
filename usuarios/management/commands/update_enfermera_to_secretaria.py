from django.core.management.base import BaseCommand
from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Actualiza el rol de enfermera a secretaria para usuarios específicos'

    def handle(self, *args, **kwargs):
        # Actualizar usuarios que fueron cambiados de secretaria a enfermera
        # Si quieres mantenerlos como enfermera, comenta la siguiente línea
        # usuarios_actualizados = Usuario.objects.filter(rol='enfermera', username__in=['secretaria_username']).update(rol='secretaria')
        
        self.stdout.write(
            self.style.SUCCESS('Los roles están configurados para aceptar tanto enfermera como secretaria')
        )

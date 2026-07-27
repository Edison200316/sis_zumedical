from django.core.management.base import BaseCommand
from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Verifica los roles de todos los usuarios del sistema'

    def handle(self, *args, **kwargs):
        usuarios = Usuario.objects.all().order_by('rol', 'username')
        
        self.stdout.write(self.style.SUCCESS('\n=== USUARIOS DEL SISTEMA ===\n'))
        
        for u in usuarios:
            rol_display = dict(Usuario.ROLES).get(u.rol, u.rol)
            self.stdout.write(
                f"{u.id:3d} | {u.username:20s} | {u.rol:15s} ({rol_display:20s}) | {u.get_full_name() or '---':30s}"
            )
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal usuarios: {usuarios.count()}'))
        
        # Estadísticas por rol
        self.stdout.write(self.style.SUCCESS('\n=== ESTADÍSTICAS POR ROL ===\n'))
        for rol_code, rol_nombre in Usuario.ROLES:
            count = Usuario.objects.filter(rol=rol_code).count()
            self.stdout.write(f"{rol_nombre:20s}: {count} usuarios")

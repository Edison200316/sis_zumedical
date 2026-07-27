# Generated migration to update secretaria role to enfermera

from django.db import migrations


def update_secretaria_role(apps, schema_editor):
    """Actualiza todos los usuarios con rol 'secretaria' a 'enfermera'"""
    Usuario = apps.get_model('usuarios', 'Usuario')
    Usuario.objects.filter(rol='secretaria').update(rol='enfermera')
    print("Usuarios con rol 'secretaria' actualizados a 'enfermera'")


def reverse_update(apps, schema_editor):
    """Reverse: no hacer nada, mantener como enfermera"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0008_rename_usuarios_lo_fecha_idx_usuarios_lo_fecha_a802c0_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(update_secretaria_role, reverse_update),
    ]

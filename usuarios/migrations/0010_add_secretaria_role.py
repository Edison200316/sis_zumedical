# Generated migration to add secretaria as valid role

from django.db import migrations, models


def revert_secretaria_to_enfermera(apps, schema_editor):
    """Revierte usuarios de 'enfermera' de vuelta a 'secretaria' si corresponde"""
    # Esta es una migración de esquema, no de datos
    # Los datos se mantienen como están
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0009_update_secretaria_to_enfermera'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='rol',
            field=models.CharField(
                max_length=20, 
                choices=[
                    ('admin', 'Administrador'),
                    ('medico', 'Medico'),
                    ('enfermera', 'Enfermera'),
                    ('secretaria', 'Secretaria'),
                    ('paciente', 'Paciente'),
                ]
            ),
        ),
    ]

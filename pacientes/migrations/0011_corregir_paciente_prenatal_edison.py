from django.db import migrations


def marcar_paciente_prenatal(apps, schema_editor):
    Paciente = apps.get_model('pacientes', 'Paciente')
    Usuario = apps.get_model('usuarios', 'Usuario')

    paciente = Paciente.objects.filter(cedula='0501171623', usuario__rol='paciente').first()
    if not paciente:
        return

    paciente.estado_embarazo = 'ACTIVO'
    paciente.mensaje_prenatal_visto = False
    paciente.save(update_fields=['estado_embarazo', 'mensaje_prenatal_visto'])

    Usuario.objects.filter(pk=paciente.usuario_id).exclude(genero='femenino').update(genero='femenino')


def deshacer(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pacientes', '0010_alter_paciente_options_paciente_fecha_actualizacion_and_more'),
    ]

    operations = [
        migrations.RunPython(marcar_paciente_prenatal, deshacer),
    ]

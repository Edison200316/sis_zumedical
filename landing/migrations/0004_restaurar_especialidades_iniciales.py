from django.db import migrations


ESPECIALIDADES = [
    {
        'id': 1,
        'nombre': 'Ginecología y Obstetricia',
        'descripcion': 'Atención integral de la salud femenina, embarazo, parto y puerperio. Seguimiento prenatal personalizado con tecnología avanzada.',
        'icono': 'fa-baby',
        'tipo': 'prenatal',
        'activo': True,
    },
    {
        'id': 2,
        'nombre': 'Odontología',
        'descripcion': 'Salud bucal completa: limpieza dental, tratamientos estéticos, ortodoncia y atención preventiva para toda la familia.',
        'icono': 'fa-tooth',
        'tipo': 'general',
        'activo': True,
    },
    {
        'id': 3,
        'nombre': 'Medicina General',
        'descripcion': 'Consulta médica general, diagnóstico y tratamiento de enfermedades comunes, medicina preventiva y control de salud.',
        'icono': 'fa-stethoscope',
        'tipo': 'general',
        'activo': True,
    },
    {
        'id': 4,
        'nombre': 'Ecografía Diagnóstica',
        'descripcion': 'Diagnóstico por imágenes con equipos de última generación. Ecografías abdominales, pélvicas y de tejidos blandos.',
        'icono': 'fa-x-ray',
        'tipo': 'general',
        'activo': True,
    },
    {
        'id': 5,
        'nombre': 'Programación de Partos y Cesáreas',
        'descripcion': 'Planificación y coordinación profesional del nacimiento, con atención especializada para madre y bebé.',
        'icono': 'fa-hospital',
        'tipo': 'prenatal',
        'activo': True,
    },
]


def restaurar_especialidades(apps, schema_editor):
    Especialidad = apps.get_model('landing', 'Especialidad')
    for data in ESPECIALIDADES:
        Especialidad.objects.update_or_create(
            id=data['id'],
            defaults={k: v for k, v in data.items() if k != 'id'},
        )


def revertir_especialidades(apps, schema_editor):
    Especialidad = apps.get_model('landing', 'Especialidad')
    Especialidad.objects.filter(id__in=[item['id'] for item in ESPECIALIDADES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0003_informacioncontacto'),
    ]

    operations = [
        migrations.RunPython(restaurar_especialidades, revertir_especialidades),
    ]

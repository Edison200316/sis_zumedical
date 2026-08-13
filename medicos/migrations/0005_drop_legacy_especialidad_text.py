from django.db import migrations


def drop_legacy_especialidad_text(apps, schema_editor):
    table = 'medicos_medico'
    db = schema_editor.connection

    try:
        with db.cursor() as cursor:
            columns = [col.name for col in db.introspection.get_table_description(cursor, table)]
            if 'especialidad' not in columns or 'especialidad_id' not in columns:
                return

            vendor = db.vendor
            if vendor == 'postgresql':
                cursor.execute('ALTER TABLE medicos_medico DROP COLUMN especialidad')
            elif vendor == 'mysql':
                cursor.execute('ALTER TABLE medicos_medico DROP COLUMN especialidad')
            elif vendor == 'sqlite':
                cursor.execute('ALTER TABLE medicos_medico DROP COLUMN especialidad')
    except Exception:
        # La app ya tiene un helper compatible para la columna antigua. Si el motor
        # no permite eliminarla en esta migración, no bloqueamos el despliegue.
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('medicos', '0004_datos_iniciales_medicos'),
    ]

    operations = [
        migrations.RunPython(drop_legacy_especialidad_text, migrations.RunPython.noop),
    ]

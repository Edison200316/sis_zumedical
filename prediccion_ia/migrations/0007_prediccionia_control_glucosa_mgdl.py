from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('control_prenatal', '0006_observaciones_opcional'),
        ('prediccion_ia', '0006_alter_prediccionia_semanas_gestacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='prediccionia',
            name='control',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='predicciones_ia',
                to='control_prenatal.controlprenatal',
                verbose_name='Control prenatal asociado',
            ),
        ),
        migrations.AlterField(
            model_name='prediccionia',
            name='glucosa',
            field=models.FloatField(verbose_name='Glucosa (mg/dL)'),
        ),
    ]

# Generated migration for CodigoRecuperacionPassword model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0010_add_secretaria_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodigoRecuperacionPassword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=6, unique=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('expira_en', models.DateTimeField()),
                ('intentos_fallidos', models.IntegerField(default=0)),
                ('validado', models.BooleanField(default=False)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='codigo_recuperacion', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Código de Recuperación',
                'verbose_name_plural': 'Códigos de Recuperación',
            },
        ),
    ]

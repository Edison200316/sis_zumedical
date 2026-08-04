from django.db import models


class Especialidad(models.Model):
    TIPO_CHOICES = [
        ('prenatal', 'Prenatal'),
        ('general', 'General'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    icono = models.CharField(max_length=50, help_text="Clase de ícono Font Awesome, ej: fa-heartbeat")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='general')
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class MedicoLanding(models.Model):
    nombre = models.CharField(max_length=150)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True)
    foto = models.ImageField(upload_to='medicos_landing/', blank=True, null=True)
    descripcion = models.CharField(max_length=200)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Médico Landing"
        verbose_name_plural = "Médicos Landing"

    def __str__(self):
        return self.nombre


class InformacionContacto(models.Model):
    """Información de contacto del centro médico Zumedical"""
    
    direccion = models.CharField(max_length=300, default="2 de Agosto & Av. 13 de Diciembre, Valencia, Ecuador")
    telefono_1 = models.CharField(max_length=20, default="0994385607")
    telefono_2 = models.CharField(max_length=20, default="0989895673", blank=True)
    email = models.EmailField(default="zumedical20@gmail.com")
    horario_lunes_viernes = models.CharField(max_length=100, default="8:30 - 17:00")
    horario_sabados = models.CharField(max_length=100, default="9:00 - 15:00")
    horario_domingos = models.CharField(max_length=100, default="9:00 - 15:00")
    emergencias_24h = models.BooleanField(default=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Información de Contacto"
        verbose_name_plural = "Información de Contacto"

    def __str__(self):
        return "Información de Contacto - Zumedical"

    @classmethod
    def obtener(cls):
        """Obtiene o crea la única instancia"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
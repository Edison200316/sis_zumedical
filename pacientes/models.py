from django.db import models
from django.conf import settings

ESTADO_EMBARAZO_CHOICES = (
    ('NINGUNO', 'Ninguno'),
    ('ACTIVO', 'Activo'),
    ('FINALIZADO', 'Finalizado'),
    ('SUSPENDIDO', 'Suspendido'),
)

TIPO_PARTO_CHOICES = (
    ('normal', 'Parto Normal'),
    ('cesarea', 'Cesárea'),
    ('induccion', 'Inducción'),
    ('otro', 'Otro'),
)

class Paciente(models.Model):

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='paciente',
    )

    cedula = models.CharField(max_length=10, blank=True, default='')
    edad = models.IntegerField(null=True, blank=True)
    direccion = models.CharField(max_length=200, blank=True, default='')
    telefono = models.CharField(max_length=10, blank=True, default='')

    # Estos campos ahora son HEREDADOS del embarazo activo
    # Se mantienen por compatibilidad backward
    fecha_ultima_menstruacion = models.DateField(null=True, blank=True)
    fecha_probable_parto = models.DateField(null=True, blank=True)

    # Estado del embarazo ACTUAL (derivado de embarazos activos)
    estado_embarazo = models.CharField(
        max_length=20,
        choices=ESTADO_EMBARAZO_CHOICES,
        default='NINGUNO',
        verbose_name='Estado del Embarazo Actual',
        help_text='Indica si la paciente tiene un embarazo en curso'
    )

    # Médico prenatal del embarazo ACTUAL
    medico_prenatal = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pacientes_prenatales',
        verbose_name='Médico prenatal responsable (actual)',
    )

    mensaje_prenatal_visto = models.BooleanField(
        default=False,
        verbose_name='Mensaje Prenatal Visto',
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} ({self.cedula})"

    @property
    def embarazo_activo(self):
        """Retorna el embarazo activo actual, si existe"""
        return self.embarazos.filter(estado='Activo').first()

    @property
    def total_consultas_generales(self):
        """Cuenta total de consultas generales"""
        from paciente_general.models import ConsultaGeneral
        return ConsultaGeneral.objects.filter(paciente=self.usuario).count()

    @property
    def total_embarazos(self):
        """Cuenta total de embarazos (activos + finalizados)"""
        return self.embarazos.count()


class Embarazo(models.Model):
    """Registra cada embarazo de una paciente (puede tener múltiples)"""
    
    ESTADO_CHOICES = (
        ('Activo', 'Embarazo Activo'),
        ('Finalizado', 'Embarazo Finalizado'),
        ('Suspendido', 'Embarazo Suspendido'),
    )

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='embarazos',
        verbose_name='Paciente',
    )

    medico_prenatal = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='embarazos_dirigidos',
        verbose_name='Médico prenatal responsable',
    )

    # Fechas
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio del Embarazo',
        help_text='Fecha cuando se activa el seguimiento prenatal'
    )
    
    fecha_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Parto',
    )

    # Gestación
    semanas_gestacion_inicio = models.IntegerField(
        default=0,
        verbose_name='Semanas de Gestación al Inicio',
    )

    semanas_gestacion_fin = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Semanas de Gestación al Parto',
    )

    # Estado
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='Activo',
        verbose_name='Estado del Embarazo',
    )

    # Información del parto (solo cuando está finalizado)
    tipo_parto = models.CharField(
        max_length=15,
        choices=TIPO_PARTO_CHOICES,
        null=True,
        blank=True,
        verbose_name='Tipo de Parto',
    )

    observaciones_parto = models.TextField(
        blank=True,
        default='',
        verbose_name='Observaciones del Parto',
    )

    # Auditoría
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Embarazo'
        verbose_name_plural = 'Embarazos'
        ordering = ['-fecha_inicio']

    def __str__(self):
        estado_txt = f"({self.estado})"
        fecha_txt = self.fecha_inicio.strftime('%Y')
        return f"Embarazo {fecha_txt} - {self.paciente.usuario.first_name} {estado_txt}"

    def finalizar(self, fecha_parto, semanas_fin, tipo_parto, observaciones=''):
        """Finaliza el embarazo"""
        self.estado = 'Finalizado'
        self.fecha_fin = fecha_parto
        self.semanas_gestacion_fin = semanas_fin
        self.tipo_parto = tipo_parto
        self.observaciones_parto = observaciones
        self.save()

        # Actualizar estado del paciente
        self.paciente.estado_embarazo = 'FINALIZADO'
        self.paciente.save()

    def activar(self):
        """Activa el embarazo"""
        self.estado = 'Activo'
        self.save()

        # Actualizar estado del paciente
        self.paciente.estado_embarazo = 'ACTIVO'
        self.paciente.medico_prenatal = self.medico_prenatal
        self.paciente.save()
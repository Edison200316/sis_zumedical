from django.db import models
from django.conf import settings


class ConsultaGeneral(models.Model):
    """
    Historia clínica unificada para múltiples especialidades:
    - Medicina General
    - Odontología
    - Ecografía Diagnóstica
    
    Los campos se adaptan según la especialidad seleccionada.
    """
    ESPECIALIDAD_CHOICES = [
        ('medicina_general', 'Medicina General'),
        ('odontologia', 'Odontología'),
        ('ecografia', 'Ecografía Diagnóstica'),
    ]
    
    # ── Campos comunes (todas las especialidades) ────────────────────────
    especialidad = models.CharField(
        max_length=20,
        choices=ESPECIALIDAD_CHOICES,
        default='medicina_general',
        verbose_name='Especialidad'
    )
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consultas_generales',
        verbose_name='Paciente',
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='consultas_realizadas',
        verbose_name='Médico',
    )
    fecha = models.DateField(auto_now_add=True)

    # ── Motivo y antecedentes ─────────────────────────────────────────────
    motivo_consulta          = models.TextField(verbose_name='Motivo de consulta')
    antecedentes_personales  = models.TextField(blank=True, default='', verbose_name='Antecedentes personales')
    antecedentes_familiares  = models.TextField(blank=True, default='', verbose_name='Antecedentes familiares')
    antecedentes_alergicos   = models.TextField(blank=True, default='', verbose_name='Antecedentes alérgicos')
    antecedentes_quirurgicos = models.TextField(blank=True, default='', verbose_name='Antecedentes quirúrgicos')
    antecedentes_obstetricos = models.TextField(blank=True, default='', verbose_name='Antecedentes obstétricos')

    # ── Examen físico / Observaciones ─────────────────────────────────────
    examen_fisico = models.TextField(blank=True, default='', verbose_name='Examen físico / Observaciones clínicas')

    # ── Signos vitales (Medicina General principalmente) ──────────────────
    presion_arterial      = models.CharField(max_length=20, blank=True, default='', verbose_name='Presión arterial (P/A)')
    saturacion_oxigeno    = models.IntegerField(null=True, blank=True, verbose_name='Saturación de oxígeno (%)')
    frecuencia_cardiaca   = models.IntegerField(null=True, blank=True, verbose_name='Frecuencia cardíaca (lpm)')
    frecuencia_respiratoria = models.IntegerField(null=True, blank=True, verbose_name='Frecuencia respiratoria (rpm)')
    temperatura           = models.FloatField(null=True, blank=True, verbose_name='Temperatura (°C)')
    talla                 = models.FloatField(null=True, blank=True, verbose_name='Talla (m)')
    peso                  = models.FloatField(null=True, blank=True, verbose_name='Peso (kg)')

    # ── Diagnóstico y tratamiento (común) ─────────────────────────────────
    diagnostico_clinico   = models.TextField(blank=True, default='', verbose_name='Diagnóstico clínico')
    
    # ── Procedimiento / Tratamiento realizado ─────────────────────────────
    procedimiento_realizado = models.TextField(blank=True, default='', verbose_name='Procedimiento o tratamiento realizado')
    
    # ── Hallazgos (principalmente para Ecografía) ─────────────────────────
    hallazgos            = models.TextField(blank=True, default='', verbose_name='Hallazgos')
    
    # ── Medicamentos y recomendaciones ────────────────────────────────────
    medicamentos_recetados = models.TextField(blank=True, default='', verbose_name='Medicamentos recetados')
    recomendaciones       = models.TextField(blank=True, default='', verbose_name='Indicaciones / Recomendaciones')

    # ── Evolución y plan (Medicina General) ───────────────────────────────
    examenes_enviados     = models.TextField(blank=True, default='', verbose_name='Exámenes solicitados')
    evolucion_enfermedad  = models.TextField(blank=True, default='', verbose_name='Evolución de la enfermedad')
    plan                  = models.TextField(blank=True, default='', verbose_name='Plan')
    tratamiento           = models.TextField(blank=True, default='', verbose_name='Tratamiento')

    # ── Campos específicos de Odontología ─────────────────────────────────
    piezas_dentales_tratadas = models.CharField(max_length=200, blank=True, default='', verbose_name='Piezas dentales tratadas')
    odontograma              = models.TextField(blank=True, default='', verbose_name='Odontograma / Observaciones dentales')
    
    # ── Campos específicos de Ecografía ───────────────────────────────────
    tipo_ecografia    = models.CharField(max_length=100, blank=True, default='', verbose_name='Tipo de ecografía')
    region_examinada  = models.CharField(max_length=200, blank=True, default='', verbose_name='Región anatómica examinada')
    conclusion_diagnostica = models.TextField(blank=True, default='', verbose_name='Conclusión diagnóstica')

    # ── Diagnóstico CIE-10 (hasta 3 diagnósticos) ────────────────────────
    diagnostico_1_patologia   = models.CharField(max_length=200, blank=True, default='', verbose_name='Patología 1')
    diagnostico_1_cie10       = models.CharField(max_length=20,  blank=True, default='', verbose_name='CIE-10 1')
    diagnostico_1_presuntivo  = models.BooleanField(default=False, verbose_name='Presuntivo 1')
    diagnostico_1_definitivo  = models.BooleanField(default=False, verbose_name='Definitivo 1')

    diagnostico_2_patologia   = models.CharField(max_length=200, blank=True, default='', verbose_name='Patología 2')
    diagnostico_2_cie10       = models.CharField(max_length=20,  blank=True, default='', verbose_name='CIE-10 2')
    diagnostico_2_presuntivo  = models.BooleanField(default=False, verbose_name='Presuntivo 2')
    diagnostico_2_definitivo  = models.BooleanField(default=False, verbose_name='Definitivo 2')

    diagnostico_3_patologia   = models.CharField(max_length=200, blank=True, default='', verbose_name='Patología 3')
    diagnostico_3_cie10       = models.CharField(max_length=20,  blank=True, default='', verbose_name='CIE-10 3')
    diagnostico_3_presuntivo  = models.BooleanField(default=False, verbose_name='Presuntivo 3')
    diagnostico_3_definitivo  = models.BooleanField(default=False, verbose_name='Definitivo 3')

    # ── Próxima cita ──────────────────────────────────────────────────────
    proxima_cita = models.DateField(null=True, blank=True, verbose_name='Próxima cita')
    proxima_cita_hora = models.TimeField(null=True, blank=True, verbose_name='Hora de próxima cita')

    class Meta:
        verbose_name        = 'Consulta General'
        verbose_name_plural = 'Consultas Generales'
        ordering            = ['-fecha']

    def __str__(self):
        return f"{self.get_especialidad_display()} — {self.paciente.get_full_name()} — {self.fecha}"

    @property
    def imc(self):
        if self.peso and self.talla and self.talla > 0:
            return round(self.peso / (self.talla ** 2), 1)
        return None

    @property
    def diagnosticos(self):
        """Lista limpia de diagnósticos con datos."""
        result = []
        for i in [1, 2, 3]:
            pat = getattr(self, f'diagnostico_{i}_patologia')
            if pat:
                result.append({
                    'patologia':  pat,
                    'cie10':      getattr(self, f'diagnostico_{i}_cie10'),
                    'presuntivo': getattr(self, f'diagnostico_{i}_presuntivo'),
                    'definitivo': getattr(self, f'diagnostico_{i}_definitivo'),
                })
        return result
    
    @property
    def especialidad_display(self):
        """Retorna el nombre legible de la especialidad."""
        return self.get_especialidad_display()


class ProgramacionParto(models.Model):
    """
    Programación de parto o cesárea — la crea el médico para una paciente prenatal.
    La paciente la ve en su panel de dashboard.
    """
    TIPO_CHOICES = [
        ('parto_natural', 'Parto Natural'),
        ('cesarea',       'Cesárea Programada'),
        ('induccion',     'Inducción del Parto'),
    ]
    ESTADO_CHOICES = [
        ('programado',  'Programado'),
        ('confirmado',  'Confirmado'),
        ('realizado',   'Realizado'),
        ('cancelado',   'Cancelado'),
        ('reprogramado','Reprogramado'),
    ]

    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='programaciones_parto',
        verbose_name='Paciente',
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='partos_programados',
        verbose_name='Médico responsable',
    )
    tipo               = models.CharField(max_length=20, choices=TIPO_CHOICES, default='parto_natural', verbose_name='Tipo')
    fecha_programada   = models.DateField(verbose_name='Fecha programada')
    hora_programada    = models.TimeField(verbose_name='Hora programada')
    semanas_gestacion  = models.IntegerField(null=True, blank=True, verbose_name='Semanas de gestación al momento')
    lugar              = models.CharField(max_length=200, blank=True, default='Zumedical — Centro Médico', verbose_name='Lugar / Sala')
    indicaciones       = models.TextField(blank=True, default='', verbose_name='Indicaciones para la paciente')
    estado             = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='programado', verbose_name='Estado')
    fecha_registro     = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Programación de Parto'
        verbose_name_plural = 'Programaciones de Parto'
        ordering            = ['-fecha_programada']

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.paciente.get_full_name()} — {self.fecha_programada}"

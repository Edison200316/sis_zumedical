from django import forms
from .models import HistoriaClinica, ControlPrenatal
from django.conf import settings


class HistoriaClinicaForm(forms.ModelForm):
    class Meta:
        model = HistoriaClinica
        fields = [
            'paciente', 'antecedentes_personales', 'antecedentes_familiares',
            'antecedentes_obstetricos', 'gestas', 'partos', 'cesareas', 'abortos', 'hijos_vivos',
            'motivo_consulta',
            'presion_arterial_inicial', 'frecuencia_cardiaca_inicial', 'frecuencia_respiratoria',
            'temperatura_inicial', 'saturacion_oxigeno', 'estado_conciencia', 'proteinuria',
            'peso_inicial', 'talla',
            'examen_fisico', 'evolucion_enfermedad', 'resultado_examenes', 'diagnostico', 'tratamiento'
        ]
        widgets = {
            'antecedentes_personales': forms.Textarea(attrs={'rows': 3}),
            'antecedentes_familiares': forms.Textarea(attrs={'rows': 3}),
            'antecedentes_obstetricos': forms.Textarea(attrs={'rows': 3}),
            'motivo_consulta': forms.Textarea(attrs={'rows': 3}),
            'examen_fisico': forms.Textarea(attrs={'rows': 3}),
            'evolucion_enfermedad': forms.Textarea(attrs={'rows': 3}),
            'resultado_examenes': forms.Textarea(attrs={'rows': 3}),
            'diagnostico': forms.Textarea(attrs={'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        medico = kwargs.pop('medico', None)
        super().__init__(*args, **kwargs)
        # Filtrar solo pacientes en el campo paciente
        self.fields['paciente'].queryset = settings.AUTH_USER_MODEL.objects.filter(rol='paciente')


class ControlPrenatalForm(forms.ModelForm):
    class Meta:
        model = ControlPrenatal
        fields = [
            'paciente', 'semanas_gestacion', 'presion_arterial', 'peso', 'altura',
            'glucosa', 'frecuencia_cardiaca', 'temperatura', 'embarazos_previos',
            'complicaciones_previas', 'diabetes_preexistente', 'diabetes_gestacional',
            'proteinuria', 'diagnostico', 'tratamiento', 'proxima_cita',
            'examen_fisico', 'resultado_examenes', 'evolucion', 'observaciones'
        ]
        widgets = {
            'diagnostico': forms.Textarea(attrs={'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'rows': 3}),
            'examen_fisico': forms.Textarea(attrs={'rows': 3}),
            'resultado_examenes': forms.Textarea(attrs={'rows': 3}),
            'evolucion': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
            'proxima_cita': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        medico = kwargs.pop('medico', None)
        super().__init__(*args, **kwargs)
        # Filtrar solo pacientes prenatales (con embarazo activo)
        from pacientes.models import Paciente
        pacientes_prenatales_ids = Paciente.objects.filter(
            estado_embarazo='ACTIVO'
        ).values_list('usuario_id', flat=True)
        self.fields['paciente'].queryset = settings.AUTH_USER_MODEL.objects.filter(
            id__in=pacientes_prenatales_ids, rol='paciente'
        )

import re

from django import forms
from django.core.exceptions import ValidationError
from .models import HistoriaClinica, ControlPrenatal
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


CONTROL_PRENATAL_RANGOS = {
    'semanas_gestacion': (4, 42, 'semanas'),
    'peso': (30.0, 250.0, 'kg'),
    'altura': (1.20, 2.20, 'm'),
    'glucosa': (40.0, 400.0, 'mg/dL'),
    'frecuencia_cardiaca': (40, 180, 'lpm'),
    'temperatura': (95.0, 106.0, '°F'),
    'embarazos_previos': (0, 20, 'embarazos'),
}


def _validar_rango(valor, campo, etiqueta):
    minimo, maximo, unidad = CONTROL_PRENATAL_RANGOS[campo]
    if valor is None:
        raise ValidationError(f'{etiqueta} es obligatorio.')
    if valor < minimo or valor > maximo:
        raise ValidationError(
            f'{etiqueta} debe estar entre {minimo:g} y {maximo:g} {unidad}.'
        )
    return valor


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
        self.fields['paciente'].queryset = User.objects.filter(rol='paciente')


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
        labels = {
            'paciente': 'Paciente Prenatal',
        }

    def __init__(self, *args, **kwargs):
        medico = kwargs.pop('medico', None)
        super().__init__(*args, **kwargs)
        from pacientes.models import Paciente
        from citas.models import Cita
        
        if medico and getattr(medico, 'rol', '') == 'medico':
            ids_asignadas = Paciente.objects.filter(
                medico_prenatal=medico
            ).values_list('usuario_id', flat=True)
            ids_con_citas = Cita.objects.filter(
                medico=medico
            ).values_list('paciente_id', flat=True)
            todos_ids = set(ids_asignadas) | set(ids_con_citas)
            
            self.fields['paciente'].queryset = User.objects.filter(
                id__in=todos_ids,
                rol='paciente'
            ).select_related('paciente').order_by('first_name', 'last_name')
        else:
            self.fields['paciente'].queryset = User.objects.filter(
                rol='paciente'
            ).select_related('paciente').order_by('first_name', 'last_name')
        # Personalizar la representación de cada paciente en el select
        self.fields['paciente'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} - {getattr(obj.paciente, 'cedula', 'Sin cédula')}"

        campos_requeridos_ia = [
            'paciente', 'semanas_gestacion', 'presion_arterial', 'peso',
            'altura', 'glucosa', 'frecuencia_cardiaca', 'temperatura',
        ]
        for nombre in campos_requeridos_ia:
            self.fields[nombre].required = True

        attrs_por_campo = {
            'semanas_gestacion': {'min': '4', 'max': '42', 'step': '1', 'placeholder': 'Ej: 24'},
            'peso': {'min': '30', 'max': '250', 'step': '0.1', 'placeholder': 'Ej: 68.5'},
            'altura': {'min': '1.20', 'max': '2.20', 'step': '0.01', 'placeholder': 'Ej: 1.62'},
            'glucosa': {'min': '40', 'max': '400', 'step': '0.1', 'placeholder': 'Ej: 90'},
            'frecuencia_cardiaca': {'min': '40', 'max': '180', 'step': '1', 'placeholder': 'Ej: 75'},
            'temperatura': {'min': '95', 'max': '106', 'step': '0.1', 'placeholder': 'Ej: 98.6'},
            'embarazos_previos': {'min': '0', 'max': '20', 'step': '1', 'placeholder': 'Ej: 0'},
        }
        for nombre, attrs in attrs_por_campo.items():
            self.fields[nombre].widget.attrs.update(attrs)
        self.fields['presion_arterial'].widget.attrs.update({
            'placeholder': 'Ej: 120/80',
            'pattern': r'\d{2,3}/\d{2,3}',
        })

    def clean_semanas_gestacion(self):
        return _validar_rango(
            self.cleaned_data.get('semanas_gestacion'),
            'semanas_gestacion',
            'Las semanas de gestación'
        )

    def clean_paciente(self):
        paciente = self.cleaned_data.get('paciente')
        perfil = getattr(paciente, 'paciente', None) if paciente else None
        edad = getattr(perfil, 'edad', None)
        if edad is None:
            raise ValidationError('La paciente debe tener una edad registrada para evaluar el riesgo con IA.')
        if edad < 10 or edad > 60:
            raise ValidationError('La edad de la paciente debe estar entre 10 y 60 años para la evaluación IA.')
        return paciente

    def clean_peso(self):
        return _validar_rango(self.cleaned_data.get('peso'), 'peso', 'El peso')

    def clean_altura(self):
        return _validar_rango(self.cleaned_data.get('altura'), 'altura', 'La altura')

    def clean_glucosa(self):
        return _validar_rango(self.cleaned_data.get('glucosa'), 'glucosa', 'La glucosa')

    def clean_frecuencia_cardiaca(self):
        return _validar_rango(
            self.cleaned_data.get('frecuencia_cardiaca'),
            'frecuencia_cardiaca',
            'La frecuencia cardíaca'
        )

    def clean_temperatura(self):
        return _validar_rango(
            self.cleaned_data.get('temperatura'),
            'temperatura',
            'La temperatura'
        )

    def clean_embarazos_previos(self):
        return _validar_rango(
            self.cleaned_data.get('embarazos_previos'),
            'embarazos_previos',
            'Los embarazos anteriores'
        )

    def clean_presion_arterial(self):
        presion = (self.cleaned_data.get('presion_arterial') or '').strip()
        match = re.fullmatch(r'(\d{2,3})\s*/\s*(\d{2,3})', presion)
        if not match:
            raise ValidationError('Ingresa la presión arterial en formato sistólica/diastólica, por ejemplo 120/80.')

        sistolica = int(match.group(1))
        diastolica = int(match.group(2))
        if not (70 <= sistolica <= 250):
            raise ValidationError('La presión sistólica debe estar entre 70 y 250 mmHg.')
        if not (40 <= diastolica <= 150):
            raise ValidationError('La presión diastólica debe estar entre 40 y 150 mmHg.')
        if sistolica <= diastolica:
            raise ValidationError('La presión sistólica debe ser mayor que la diastólica.')

        return f'{sistolica}/{diastolica}'

    def clean(self):
        cleaned_data = super().clean()
        paciente = cleaned_data.get('paciente')
        proxima_cita = cleaned_data.get('proxima_cita')
        fecha_control = self.instance.fecha if self.instance and self.instance.pk else None
        if paciente and proxima_cita and fecha_control and proxima_cita < fecha_control:
            self.add_error('proxima_cita', 'La próxima cita no puede ser anterior al control.')
        return cleaned_data

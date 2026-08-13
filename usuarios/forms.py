import re

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import CodigoRecuperacionPassword
from pacientes.models import Paciente
from citas.models import Cita
from control_prenatal.models import ControlPrenatal
from control_prenatal.forms import _validar_rango
from .validators import (
    MENSAJE_CEDULA_INVALIDA,
    MENSAJE_EMAIL_INVALIDO,
    validar_cedula_ecuatoriana,
    validar_email_permitido,
)

Usuario = get_user_model()


# ════════════════════════════════════════════════════════════════════════════════════════
# FORMULARIOS DE RECUPERACIÓN DE CONTRASEÑA
# ════════════════════════════════════════════════════════════════════════════════════════

class VerificarEmailForm(forms.Form):
    """Formulario para verificar si el email existe en la BD"""
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'autocomplete': 'email',
        }),
        help_text='Ingresa el correo asociado a tu cuenta'
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if not validar_email_permitido(email):
                raise forms.ValidationError(MENSAJE_EMAIL_INVALIDO)
            # Buscar usuario por email (case-insensitive)
            usuario = Usuario.objects.filter(email__iexact=email).first()
            if not usuario:
                raise forms.ValidationError('No existe una cuenta asociada a este correo electrónico.')
            if not usuario.is_active:
                raise forms.ValidationError('Esta cuenta ha sido desactivada. Contacta al administrador.')
        return email


class VerificarCodigoForm(forms.Form):
    """Formulario para verificar el código enviado por email"""
    codigo = forms.CharField(
        label='Código de Recuperación',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': '000000',
            'autocomplete': 'off',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
            'style': 'letter-spacing: 0.5em; font-size: 1.5rem; font-weight: 600;',
        }),
        help_text='Ingresa el código de 6 dígitos que enviamos a tu correo'
    )

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        
        if not self.usuario:
            raise forms.ValidationError('Error al procesar la solicitud. Intenta de nuevo.')

        try:
            codigo_obj = CodigoRecuperacionPassword.objects.get(
                usuario=self.usuario,
                codigo=codigo
            )
        except CodigoRecuperacionPassword.DoesNotExist:
            # Incrementar intentos fallidos
            try:
                codigo_guardado = CodigoRecuperacionPassword.objects.get(usuario=self.usuario)
                codigo_guardado.intentos_fallidos += 1
                codigo_guardado.save()
            except:
                pass
            raise forms.ValidationError('Código incorrecto. Intenta de nuevo.')

        # Validar que el código sea válido
        if not codigo_obj.es_valido():
            if codigo_obj.es_expirado():
                raise forms.ValidationError('El código ha expirado. Solicita uno nuevo.')
            else:
                raise forms.ValidationError('Demasiados intentos fallidos. Solicita un nuevo código.')

        return codigo


class ResetPasswordForm(forms.Form):
    """Formulario para establecer nueva contraseña"""
    password1 = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu nueva contraseña',
            'autocomplete': 'new-password',
        }),
        min_length=8,
        help_text='Mínimo 8 caracteres'
    )
    
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu nueva contraseña',
            'autocomplete': 'new-password',
        }),
        min_length=8,
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Las contraseñas no coinciden.')

            # Validaciones de seguridad
            if password1.isdigit():
                raise forms.ValidationError('La contraseña no puede contener solo números.')
            
            if len(password1) < 8:
                raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')

        return cleaned_data


# ════════════════════════════════════════════════════════════════════════════════════════
# FORMULARIOS DE PACIENTES Y CITAS (EXISTENTES)
# ════════════════════════════════════════════════════════════════════════════════════════

class RegistroPacienteForm(forms.ModelForm):
    """Formulario para registro de pacientes"""
    username = forms.CharField(
        label='Usuario/Cédula',
        max_length=150,
        required=True,
        help_text='Ingresa tu número de cédula como usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 1234567890'
        })
    )
    first_name = forms.CharField(
        label='Nombre',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'})
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'})
    )
    email = forms.EmailField(
        label='Correo Electrónico',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'correo@ejemplo.com (opcional)'
        })
    )
    cedula = forms.CharField(
        label='Cédula',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de cédula'
        })
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 0987654321'
        })
    )
    genero = forms.ChoiceField(
        label='Género',
        choices=[('', 'Seleccionar...'), ('femenino', 'Femenino'), ('masculino', 'Masculino'), ('otro', 'Otro')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres'
        }),
        min_length=8,
        help_text='Mínimo 8 caracteres'
    )
    password_confirm = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite la contraseña'
        }),
        required=True
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('Este usuario/cédula ya está registrado.')
        return username

    def clean_cedula(self):
        from pacientes.models import Paciente
        cedula = (self.cleaned_data.get('cedula') or '').strip()
        if not validar_cedula_ecuatoriana(cedula):
            raise forms.ValidationError(MENSAJE_CEDULA_INVALIDA)
        if Paciente.objects.filter(cedula=cedula).exists():
            raise forms.ValidationError('Esta cédula ya está registrada.')
        return cedula

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if email and not validar_email_permitido(email):
            raise forms.ValidationError(MENSAJE_EMAIL_INVALIDO)
        if email and Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password:
            import re
            if len(password) < 8:
                self.add_error('password', 'La contraseña debe tener mínimo 8 caracteres.')
            if not re.search(r'[A-ZÁÉÍÓÚÑ]', password):
                self.add_error('password', 'La contraseña debe incluir una letra mayúscula.')
            if not re.search(r'\d', password):
                self.add_error('password', 'La contraseña debe incluir un número.')
            if not re.search(r'[^A-Za-z0-9ÁÉÍÓÚÑáéíóúñ]', password):
                self.add_error('password', 'La contraseña debe incluir un símbolo.')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Las contraseñas no coinciden.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.rol = 'paciente'
        user.genero = self.cleaned_data.get('genero', '')
        if commit:
            user.save()
            from pacientes.models import Paciente
            paciente, _ = Paciente.objects.get_or_create(usuario=user)
            paciente.cedula = self.cleaned_data.get('cedula', '')
            paciente.telefono = self.cleaned_data.get('telefono', '')
            paciente.estado_embarazo = 'NINGUNO'
            paciente.save()
        return user


class CitaForm(forms.ModelForm):
    """Formulario para agendar citas"""
    class Meta:
        model = Cita
        fields = ['especialidad', 'medico', 'fecha', 'hora', 'motivo']
        widgets = {
            'especialidad': forms.Select(attrs={'class': 'form-control'}),
            'medico': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CitaEnfermeraForm(forms.ModelForm):
    """Formulario para agendar citas (versión enfermera)"""
    class Meta:
        model = Cita
        fields = ['paciente', 'especialidad', 'medico', 'fecha', 'hora', 'motivo']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'especialidad': forms.Select(attrs={'class': 'form-control'}),
            'medico': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from medicos.models import Medico

        medicos_reales_ids = Medico.objects.filter(
            usuario__is_active=True,
            usuario__rol='medico',
            especialidad__isnull=False,
        ).exclude(
            usuario__username__iregex=r'^(medico_verif|medico_test|test_medico)'
        ).values_list('usuario_id', flat=True)

        self.fields['medico'].queryset = Usuario.objects.filter(
            id__in=medicos_reales_ids,
            is_active=True,
            rol='medico',
        ).order_by('first_name', 'last_name', 'username')

        def medico_label(obj):
            return obj.get_full_name() or obj.username

        self.fields['medico'].label_from_instance = medico_label


class ControlPrenatalForm(forms.ModelForm):
    """Formulario para registrar controles prenatales"""
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
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'semanas_gestacion': forms.NumberInput(attrs={'class': 'form-control'}),
            'presion_arterial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '120/80'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'altura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'glucosa': forms.NumberInput(attrs={'class': 'form-control'}),
            'frecuencia_cardiaca': forms.NumberInput(attrs={'class': 'form-control'}),
            'temperatura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'embarazos_previos': forms.NumberInput(attrs={'class': 'form-control'}),
            'complicaciones_previas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'diabetes_preexistente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'diabetes_gestacional': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'proteinuria': forms.TextInput(attrs={'class': 'form-control'}),
            'proxima_cita': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'examen_fisico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'resultado_examenes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'evolucion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'paciente': 'Paciente Prenatal',
        }

    def __init__(self, *args, **kwargs):
        # Extraer el parámetro medico si existe (para compatibilidad)
        medico = kwargs.pop('medico', None)
        super().__init__(*args, **kwargs)
        
        from pacientes.models import Paciente
        from citas.models import Cita
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
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
        def label_from_instance(obj):
            cedula = getattr(obj.paciente, 'cedula', '') if hasattr(obj, 'paciente') else ''
            nombre = obj.get_full_name() or obj.username
            if cedula:
                return f"{nombre} - {cedula}"
            return nombre
        
        self.fields['paciente'].label_from_instance = label_from_instance

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


class EditarPacienteEnfermeraForm(forms.ModelForm):
    """Formulario para que enfermera edite datos de paciente"""
    username = forms.CharField(
        label='Usuario',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label='Nombre',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Correo',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Paciente
        fields = ['cedula', 'edad', 'direccion', 'telefono']
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        if usuario:
            self.fields['username'].initial = usuario.username
            self.fields['first_name'].initial = usuario.first_name
            self.fields['last_name'].initial = usuario.last_name
            self.fields['email'].initial = usuario.email

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if email and not validar_email_permitido(email):
            raise forms.ValidationError(MENSAJE_EMAIL_INVALIDO)
        if email:
            qs = Usuario.objects.filter(email__iexact=email)
            if self.usuario:
                qs = qs.exclude(pk=self.usuario.pk)
            if qs.exists():
                raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean_cedula(self):
        cedula = (self.cleaned_data.get('cedula') or '').strip()
        if cedula and not validar_cedula_ecuatoriana(cedula):
            raise forms.ValidationError(MENSAJE_CEDULA_INVALIDA)
        return cedula

    def save(self, commit=True, usuario=None):
        paciente = super().save(commit=False)
        if usuario:
            usuario.username = self.cleaned_data.get('username')
            usuario.first_name = self.cleaned_data.get('first_name')
            usuario.last_name = self.cleaned_data.get('last_name')
            usuario.email = self.cleaned_data.get('email')
            if commit:
                usuario.save()
        if commit:
            paciente.save()
        return paciente

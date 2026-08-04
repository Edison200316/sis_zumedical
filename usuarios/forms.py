from django import forms
from django.contrib.auth import get_user_model
from .models import CodigoRecuperacionPassword
from pacientes.models import Paciente
from citas.models import Cita
from control_prenatal.models import ControlPrenatal

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
        cedula = self.cleaned_data.get('cedula')
        if Paciente.objects.filter(cedula=cedula).exists():
            raise forms.ValidationError('Esta cédula ya está registrada.')
        return cedula

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
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
        
        if medico:
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
        if email:
            qs = Usuario.objects.filter(email__iexact=email)
            if self.usuario:
                qs = qs.exclude(pk=self.usuario.pk)
            if qs.exists():
                raise forms.ValidationError('Este correo ya está registrado.')
        return email

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

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
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.rol = 'paciente'
        if commit:
            user.save()
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


class ControlPrenatalForm(forms.ModelForm):
    """Formulario para registrar controles prenatales"""
    class Meta:
        model = ControlPrenatal
        fields = [
            'paciente', 'semanas_gestacion', 'presion_arterial', 'peso',
            'glucosa', 'frecuencia_cardiaca', 'diagnostico', 'tratamiento'
        ]
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'semanas_gestacion': forms.NumberInput(attrs={'class': 'form-control'}),
            'presion_arterial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '120/80'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'glucosa': forms.NumberInput(attrs={'class': 'form-control'}),
            'frecuencia_cardiaca': forms.NumberInput(attrs={'class': 'form-control'}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EditarPacienteEnfermeraForm(forms.ModelForm):
    """Formulario para que enfermera edite datos de paciente"""
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
        required=True,
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
        if usuario:
            self.fields['first_name'].initial = usuario.first_name
            self.fields['last_name'].initial = usuario.last_name
            self.fields['email'].initial = usuario.email

    def save(self, commit=True, usuario=None):
        paciente = super().save(commit=False)
        if usuario:
            usuario.first_name = self.cleaned_data.get('first_name')
            usuario.last_name = self.cleaned_data.get('last_name')
            usuario.email = self.cleaned_data.get('email')
            if commit:
                usuario.save()
        if commit:
            paciente.save()
        return paciente

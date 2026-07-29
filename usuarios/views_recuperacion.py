"""
Vistas para recuperación de contraseña olvidada.
Sistema personalizado con código de 6 dígitos enviado por email.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse
from .forms import VerificarEmailForm, VerificarCodigoForm, ResetPasswordForm
from .models import CodigoRecuperacionPassword

Usuario = get_user_model()


def recuperar_contrasena(request):
    """
    Vista 1: Formulario para ingresa el email
    Verifica si el email existe en la BD
    """
    if request.user.is_authenticated:
        return redirect('paciente_dashboard')  # O el dashboard según su rol

    if request.method == 'POST':
        form = VerificarEmailForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                # Buscar usuario por email
                usuario = Usuario.objects.get(email__iexact=email)
                
                # Crear o actualizar código de recuperación
                codigo_obj = CodigoRecuperacionPassword.crear_para_usuario(usuario)
                
                # Enviar email con código
                enviar_email_codigo(usuario, codigo_obj.codigo)
                
                # Guardar el email en la sesión para la siguiente vista
                request.session['email_recuperacion'] = email
                
                # Redirigir a verificación de código
                return redirect('verificar_codigo_recuperacion')
                
            except Usuario.DoesNotExist:
                # No revelar si el email existe o no (seguridad)
                messages.info(request, 'Si el correo está registrado, recibirás un código en tu bandeja de entrada.')
                return redirect('recuperar_contrasena')
    else:
        form = VerificarEmailForm()

    return render(request, 'recuperacion/paso_1_email.html', {'form': form})


def verificar_codigo_recuperacion(request):
    """
    Vista 2: Formulario para ingresar el código de 6 dígitos
    Verifica que el código sea válido
    """
    # Obtener el email de la sesión
    email = request.session.get('email_recuperacion')
    
    if not email:
        messages.error(request, 'Debes comenzar desde el paso 1.')
        return redirect('recuperar_contrasena')

    try:
        usuario = Usuario.objects.get(email__iexact=email)
    except Usuario.DoesNotExist:
        messages.error(request, 'El usuario no existe.')
        return redirect('recuperar_contrasena')

    if request.method == 'POST':
        form = VerificarCodigoForm(request.POST, usuario=usuario)
        
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            
            try:
                codigo_obj = CodigoRecuperacionPassword.objects.get(
                    usuario=usuario,
                    codigo=codigo
                )
                codigo_obj.validado = True
                codigo_obj.save()
                
                # Guardar usuario en sesión para el reset
                request.session['usuario_id_recuperacion'] = usuario.id
                
                return redirect('reset_password_form')
                
            except CodigoRecuperacionPassword.DoesNotExist:
                messages.error(request, 'Código incorrecto.')
    else:
        form = VerificarCodigoForm(usuario=usuario)

    # Obtener el código guardado para mostrar tiempo restante
    try:
        codigo_obj = CodigoRecuperacionPassword.objects.get(usuario=usuario)
        minutos_restantes = max(0, (codigo_obj.expira_en - timezone.now()).total_seconds() // 60)
        intentos_restantes = codigo_obj.max_intentos - codigo_obj.intentos_fallidos
        expira_timestamp = codigo_obj.expira_en.isoformat()  # Para JavaScript
    except:
        minutos_restantes = 0
        intentos_restantes = 0
        expira_timestamp = timezone.now().isoformat()

    return render(request, 'recuperacion/paso_2_codigo.html', {
        'form': form,
        'usuario_nombre': usuario.get_full_name() or usuario.username,
        'minutos_restantes': int(minutos_restantes),
        'intentos_restantes': intentos_restantes,
        'email': email,
        'expira_timestamp': expira_timestamp,  # Para el contador JavaScript
    })


def reset_password_form(request):
    """
    Vista 3: Formulario para establecer nueva contraseña
    """
    usuario_id = request.session.get('usuario_id_recuperacion')
    
    if not usuario_id:
        messages.error(request, 'Sesión expirada. Intenta de nuevo.')
        return redirect('recuperar_contrasena')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        messages.error(request, 'El usuario no existe.')
        return redirect('recuperar_contrasena')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        
        if form.is_valid():
            password = form.cleaned_data['password1']
            
            # Cambiar la contraseña
            usuario.set_password(password)
            usuario.save()
            
            # Eliminar el código de recuperación
            try:
                CodigoRecuperacionPassword.objects.get(usuario=usuario).delete()
            except:
                pass
            
            # Limpiar sesión
            if 'email_recuperacion' in request.session:
                del request.session['email_recuperacion']
            if 'usuario_id_recuperacion' in request.session:
                del request.session['usuario_id_recuperacion']
            
            messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
            return redirect('reset_password_completado')
    else:
        form = ResetPasswordForm()

    return render(request, 'recuperacion/paso_3_password.html', {
        'form': form,
        'usuario_nombre': usuario.get_full_name() or usuario.username,
    })


def reset_password_completado(request):
    """
    Vista 4: Confirmación de reset exitoso
    """
    return render(request, 'recuperacion/paso_4_completado.html')


def reenviar_codigo(request):
    """
    AJAX: Reenvía el código de recuperación
    """
    if request.method != 'POST':
        return redirect('recuperar_contrasena')

    email = request.session.get('email_recuperacion')
    
    if not email:
        messages.error(request, 'Sesión expirada.')
        return redirect('recuperar_contrasena')

    try:
        usuario = Usuario.objects.get(email__iexact=email)
        
        # Crear nuevo código
        codigo_obj = CodigoRecuperacionPassword.crear_para_usuario(usuario)
        
        # Enviar email
        enviar_email_codigo(usuario, codigo_obj.codigo)
        
        messages.success(request, 'Se ha reenviado el código a tu correo.')
        return redirect('verificar_codigo_recuperacion')
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('recuperar_contrasena')


def enviar_email_codigo(usuario, codigo):
    """
    Envía el email con el código de recuperación
    Incluye firma profesional y HTML renderizado correctamente
    """
    # Asunto profesional
    subject = '🔐 Tu código de recuperación - ZUMedical'
    
    # Obtener nombre completo o username
    nombre = usuario.get_full_name() if usuario.get_full_name() else usuario.username
    
    # Contexto para la plantilla
    context = {
        'nombre': nombre,
        'codigo': codigo,
        'tiempo_expiracion': 15,  # 15 minutos
    }
    
    # Renderizar HTML desde plantilla
    try:
        html_message = render_to_string('emails/codigo_recuperacion.html', context)
    except Exception as e:
        print(f"Error al renderizar plantilla: {e}")
        # Fallback a mensaje de texto
        html_message = f"""
        Hola {nombre},

        Tu código de recuperación de contraseña es:

        {codigo}

        Este código es válido por 15 minutos.

        Si no solicitaste este cambio, ignora este correo.

        --
        ZUMedical - Centro Médico Especializado
        """

    try:
        send_mail(
            subject=subject,
            message=f"Código: {codigo}",  # Texto plano como fallback
            from_email=settings.DEFAULT_FROM_EMAIL,  # Usar la firma del settings
            recipient_list=[usuario.email],
            html_message=html_message,  # Enviar HTML
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# VALIDACIÓN EN TIEMPO REAL (AJAX)
# ═══════════════════════════════════════════════════════════════

def validar_usuario_existe(request):
    """
    AJAX: Valida si un usuario/email existe en la base de datos
    Used by: Login form
    GET params: username
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    username_or_email = request.GET.get('username', '').strip()
    
    if not username_or_email:
        return JsonResponse({
            'existe': False,
            'mensaje': 'Ingresa tu usuario o correo'
        })
    
    # Buscar por username o email
    user_obj = None
    try:
        user_obj = Usuario.objects.get(username=username_or_email)
    except Usuario.DoesNotExist:
        try:
            user_obj = Usuario.objects.get(email__iexact=username_or_email)
        except Usuario.DoesNotExist:
            pass
        except Usuario.MultipleObjectsReturned:
            user_obj = Usuario.objects.filter(email__iexact=username_or_email).first()
    
    if user_obj:
        # Verificar si está desactivado
        if not user_obj.is_active:
            return JsonResponse({
                'existe': True,
                'desactivado': True,
                'mensaje': 'Cuenta desactivada'
            })
        return JsonResponse({
            'existe': True,
            'desactivado': False,
            'mensaje': 'Usuario encontrado'
        })
    else:
        return JsonResponse({
            'existe': False,
            'mensaje': 'Usuario o correo no existe'
        })


def validar_passwords_coinciden(request):
    """
    AJAX: Valida que dos contraseñas coincidan
    Used by: Password reset form
    GET params: password1, password2
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    password1 = request.GET.get('password1', '')
    password2 = request.GET.get('password2', '')
    
    if not password2:
        return JsonResponse({
            'coinciden': None,
            'mensaje': ''
        })
    
    if password1 == password2:
        return JsonResponse({
            'coinciden': True,
            'mensaje': 'Las contraseñas coinciden'
        })
    else:
        return JsonResponse({
            'coinciden': False,
            'mensaje': 'Las contraseñas no coinciden'
        })

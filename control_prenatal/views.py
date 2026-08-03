from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import HistoriaClinica, ControlPrenatal
from .forms import HistoriaClinicaForm, ControlPrenatalForm
from django.conf import settings
import json


@login_required
def lista_historias(request):
    """Muestra la lista de historias clínicas (para médicos y admin)."""
    if request.user.rol not in ['medico', 'admin']:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    historias = HistoriaClinica.objects.select_related('paciente', 'medico').all().order_by('-fecha_registro')
    return render(request, 'control_prenatal/lista_historias.html', {'historias': historias})


@login_required
def detalle_historia(request, historia_id):
    """Muestra el detalle de una historia clínica y sus controles prenatales."""
    historia = get_object_or_404(HistoriaClinica, id=historia_id)
    controles = historia.paciente.controles_paciente.all().order_by('-fecha')
    
    # Verificar permisos: médico, admin o la propia paciente
    if request.user.rol not in ['medico', 'admin'] and request.user != historia.paciente:
        messages.error(request, 'No tienes permisos para acceder a esta historia.')
        return redirect('home')
    
    return render(request, 'control_prenatal/detalle_historia.html', {
        'historia': historia,
        'controles': controles
    })


@login_required
def crear_historia(request):
    """Crea una nueva historia clínica obstétrica."""
    if request.user.rol not in ['medico', 'admin']:
        messages.error(request, 'No tienes permisos para crear historias.')
        return redirect('home')
    
    if request.method == 'POST':
        form = HistoriaClinicaForm(request.POST, medico=request.user)
        if form.is_valid():
            historia = form.save(commit=False)
            historia.medico = request.user
            historia.save()
            messages.success(request, 'Historia clínica creada exitosamente.')
            return redirect('detalle_historia', historia_id=historia.id)
    else:
        form = HistoriaClinicaForm(medico=request.user)
    
    return render(request, 'control_prenatal/form_historia.html', {'form': form, 'titulo': 'Nueva Historia Clínica'})


@login_required
def editar_historia(request, historia_id):
    """Edita una historia clínica existente."""
    historia = get_object_or_404(HistoriaClinica, id=historia_id)
    
    if request.user.rol not in ['medico', 'admin']:
        messages.error(request, 'No tienes permisos para editar esta historia.')
        return redirect('home')
    
    if request.method == 'POST':
        form = HistoriaClinicaForm(request.POST, instance=historia, medico=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Historia clínica actualizada exitosamente.')
            return redirect('detalle_historia', historia_id=historia.id)
    else:
        form = HistoriaClinicaForm(instance=historia, medico=request.user)
    
    return render(request, 'control_prenatal/form_historia.html', {'form': form, 'titulo': 'Editar Historia Clínica'})


@login_required
def crear_control(request, paciente_id=None):
    """Crea un nuevo control prenatal."""
    if request.user.rol not in ['medico', 'admin']:
        messages.error(request, 'No tienes permisos para crear controles.')
        return redirect('home')
    
    paciente = None
    if paciente_id:
        paciente = get_object_or_404(settings.AUTH_USER_MODEL, id=paciente_id, rol='paciente')
    
    if request.method == 'POST':
        form = ControlPrenatalForm(request.POST, medico=request.user)
        if form.is_valid():
            control = form.save(commit=False)
            control.medico = request.user
            control.save()
            
            # Activar modo prenatal automáticamente si estaba en NINGUNO
            if hasattr(control.paciente, 'paciente'):
                perfil_pac = control.paciente.paciente
                if perfil_pac.estado_embarazo == 'NINGUNO':
                    perfil_pac.estado_embarazo = 'ACTIVO'
                    perfil_pac.save()
                    
            messages.success(request, 'Control prenatal registrado exitosamente.')
            # Redirigir a la historia clínica del paciente
            try:
                historia = HistoriaClinica.objects.get(paciente=control.paciente)
                return redirect('detalle_historia', historia_id=historia.id)
            except HistoriaClinica.DoesNotExist:
                return redirect('lista_historias')
    else:
        initial = {'paciente': paciente} if paciente else {}
        form = ControlPrenatalForm(initial=initial, medico=request.user)
    
    return render(request, 'control_prenatal/form_control.html', {'form': form, 'titulo': 'Nuevo Control Prenatal', 'paciente': paciente})


@login_required
def editar_control(request, control_id):
    """Edita un control prenatal existente."""
    control = get_object_or_404(ControlPrenatal, id=control_id)
    
    if request.user.rol not in ['medico', 'admin']:
        messages.error(request, 'No tienes permisos para editar este control.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ControlPrenatalForm(request.POST, instance=control, medico=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Control prenatal actualizado exitosamente.')
            try:
                historia = HistoriaClinica.objects.get(paciente=control.paciente)
                return redirect('detalle_historia', historia_id=historia.id)
            except HistoriaClinica.DoesNotExist:
                return redirect('lista_historias')
    else:
        form = ControlPrenatalForm(instance=control, medico=request.user)
    
    return render(request, 'control_prenatal/form_control.html', {'form': form, 'titulo': 'Editar Control Prenatal'})


@login_required
def mi_historial(request):
    """Bloqueado por política del centro médico - Los pacientes no pueden ver su historial."""
    messages.warning(request, 'Por política del centro médico, los pacientes no tienen acceso al historial de controles prenatales.')
    return redirect('paciente_dashboard')


# ── API Endpoints para editar/eliminar controles ────────────────────────

@login_required
@require_http_methods(["GET", "POST"])
def editar_control_prenatal(request, control_id):
    """
    Edita un control prenatal existente mediante API JSON.
    
    GET: Retorna JSON con datos del control
    POST: Recibe datos, valida, guarda y retorna JSON de éxito/error
    """
    # Verificar permisos: solo médicos y admin
    if request.user.rol not in ['medico', 'admin']:
        return JsonResponse({
            'success': False,
            'error': 'No tienes permisos para editar controles.'
        }, status=403)
    
    control = get_object_or_404(ControlPrenatal, id=control_id)
    
    if request.method == 'GET':
        # Retornar datos del control en formato JSON
        return JsonResponse({
            'success': True,
            'data': {
                'id': control.id,
                'fecha': control.fecha.isoformat(),
                'semanas_gestacion': control.semanas_gestacion,
                'presion_arterial': control.presion_arterial,
                'glucosa': control.glucosa,
                'peso': control.peso,
                'altura': control.altura,
                'frecuencia_cardiaca': control.frecuencia_cardiaca,
                'temperatura': control.temperatura,
                'observaciones': control.observaciones,
                'diagnostico': control.diagnostico,
                'tratamiento': control.tratamiento,
                'examen_fisico': control.examen_fisico,
                'resultado_examenes': control.resultado_examenes,
                'evolucion': control.evolucion,
                'proteinuria': control.proteinuria,
                'proxima_cita': control.proxima_cita.isoformat() if control.proxima_cita else None,
            }
        })
    
    elif request.method == 'POST':
        try:
            # Obtener datos JSON del request
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Datos JSON inválidos.'
            }, status=400)
        
        # Rellenar campos obligatorios que no vienen en el JSON desde la instancia
        campos_modelo = [f.name for f in ControlPrenatal._meta.get_fields() 
                        if f.name not in ['id', 'medico'] and not f.auto_created]
        for campo in campos_modelo:
            if campo not in data or (data[campo] is None and campo != 'proxima_cita'):
                valor = getattr(control, campo)
                # Para campos booleanos False es un valor válido, no lo sobreescribas
                if isinstance(valor, bool):
                    if campo not in data:
                        data[campo] = valor
                elif campo == 'paciente':
                    data[campo] = valor.id if hasattr(valor, 'id') else valor
                elif campo == 'proxima_cita':
                    # proxima_cita puede ser null
                    data[campo] = valor.isoformat() if valor else None
                elif hasattr(valor, 'isoformat'):
                    # Fechas
                    data[campo] = valor.isoformat()
                else:
                    data[campo] = valor
        
        # Sobreescribir paciente siempre (no debe cambiar al editar)
        data['paciente'] = control.paciente_id
        
        # Crear formulario con datos y la instancia del control
        form = ControlPrenatalForm(data, instance=control, medico=request.user)
        
        if form.is_valid():
            # Guardar el control actualizado
            control = form.save()
            prediccion = None
            try:
                from usuarios.views import _ejecutar_ia_en_control
                prediccion = _ejecutar_ia_en_control(control, request)
            except Exception:
                prediccion = None
            return JsonResponse({
                'success': True,
                'message': 'Control prenatal actualizado correctamente.',
                'ia_actualizada': bool(prediccion),
            })
        else:
            # Retornar errores de validación
            return JsonResponse({
                'success': False,
                'error': 'Error en los datos proporcionados.',
                'errors': form.errors
            }, status=400)


@login_required
@require_http_methods(["POST"])
def eliminar_control_prenatal(request, control_id):
    """
    Elimina un control prenatal existente mediante API JSON.
    
    POST: Recibe control_id, elimina el control, retorna JSON de éxito
    """
    # Verificar permisos: solo médicos y admin
    if request.user.rol not in ['medico', 'admin']:
        return JsonResponse({
            'success': False,
            'error': 'No tienes permisos para eliminar controles.'
        }, status=403)
    
    control = get_object_or_404(ControlPrenatal, id=control_id)
    
    try:
        # Guardar información antes de eliminar (para logging si se necesita)
        control_info = {
            'paciente': control.paciente.get_full_name(),
            'fecha': str(control.fecha),
            'semanas': control.semanas_gestacion
        }
        
        # Eliminar el control
        control.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Control prenatal eliminado correctamente. ({control_info["fecha"]}, {control_info["semanas"]} semanas)'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al eliminar el control: {str(e)}'
        }, status=500)


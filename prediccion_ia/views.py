"""
views.py — prediccion_ia
=========================
RF-18 / RF-19: Evaluación de riesgo gestacional con ML (Random Forest).

Flujo correcto:
  Médico registra control → IA se dispara automáticamente (en usuarios/views.py)
  Paciente: solo VISUALIZA el resultado generado por la IA, no llena datos manualmente.
  Médico:   panel clínico completo con evolución, complicaciones y recomendaciones.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import PrediccionIA
from pacientes.models import Paciente
from usuarios.models import Usuario


def _medico_prenatal_check(request):
    """Devuelve True si el médico es prenatal, False en caso contrario."""
    try:
        return (request.user.medico.especialidad and
                request.user.medico.especialidad.tipo == 'prenatal')
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# VISTA PACIENTE — Solo visualización del resultado IA
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def evaluar_riesgo(request):
    """
    Vista para la paciente prenatal — solo visualización.
    No requiere @login_required — hace su propio redirect al paciente_login.
    """
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    if user.rol != 'paciente':
        if user.rol == 'medico':
            return redirect('medico_dashboard')
        return redirect('login')
    if not user.puede_prenatal:
        return redirect('paciente_general_dashboard')

    perfil = Paciente.objects.filter(usuario=user).first()

    predicciones = []
    ultima_prediccion = None

    if perfil:
        predicciones = list(
            PrediccionIA.objects.filter(paciente=perfil).order_by('-fecha')[:10]
        )
        ultima_prediccion = predicciones[0] if predicciones else None

    return render(request, 'paciente/evaluar_riesgo.html', {
        'perfil':            perfil,
        'predicciones':      predicciones,
        'ultima_prediccion': ultima_prediccion,
    })


# ─────────────────────────────────────────────────────────────────────────────
# VISTA MÉDICO — Panel clínico completo
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def ver_predicciones_paciente(request, paciente_id):
    """
    Vista para el médico: panel clínico completo.
    Solo médicos de especialidad prenatal pueden ver datos de embarazo.
    """
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    if user.rol != 'medico':
        return redirect('login')

    # Solo médicos prenatales pueden ver esto
    try:
        es_prenatal = user.medico.especialidad and user.medico.especialidad.tipo == 'prenatal'
    except Exception:
        es_prenatal = False

    if not es_prenatal:
        from django.contrib import messages as msg
        msg.error(request, 'No tienes acceso a los datos prenatales de esta paciente.')
        return redirect('medico_dashboard')

    paciente_usuario = get_object_or_404(Usuario, id=paciente_id)
    perfil           = Paciente.objects.filter(usuario=paciente_usuario).first()
    predicciones_qs  = PrediccionIA.objects.filter(
        paciente=perfil
    ).order_by('-fecha') if perfil else PrediccionIA.objects.none()

    # Parsear JSON de cada predicción
    predicciones = []
    for pred in predicciones_qs:
        pred.datos = pred.datos_resultado
        predicciones.append(pred)

    tendencia = _calcular_tendencia(predicciones[:5])
    ultima    = predicciones[0] if predicciones else None

    # Delta entre la última y la anterior predicción
    delta_tendencia = None
    if len(predicciones) >= 2:
        delta_tendencia = predicciones[0].puntuacion_riesgo - predicciones[1].puntuacion_riesgo

    return render(request, 'medico/ver_predicciones.html', {
        'paciente':        paciente_usuario,
        'perfil':          perfil,
        'predicciones':    predicciones,
        'ultima':          ultima,
        'tendencia':       tendencia,
        'delta_tendencia': delta_tendencia,
    })


# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────────────────────

_NIVEL_NUM = {'Bajo': 0, 'Medio': 1, 'Alto': 2}


def _calcular_tendencia(predicciones: list) -> str:
    if len(predicciones) < 2:
        return 'sin_datos'
    reciente = _NIVEL_NUM.get(predicciones[0].nivel_riesgo, 1)
    antigua  = _NIVEL_NUM.get(predicciones[-1].nivel_riesgo, 1)
    if reciente < antigua:
        return 'mejorando'
    elif reciente > antigua:
        return 'empeorando'
    return 'estable'

"""
context_processors.py — Zumedical
Inyecta variables globales al contexto de todos los templates.
"""


def medico_context(request):
    """
    Disponible en todos los templates:
        es_prenatal      — bool: True si el médico logueado es de especialidad prenatal, ginecología u obstetricia
        sb_citas_pendientes — int: citas pendientes del médico hoy (para el badge del sidebar)
    """
    if not request.user.is_authenticated or request.user.rol != 'medico':
        return {}

    # Determinar tipo de médico
    try:
        from medicos.models import Medico
        medico_perfil = Medico.objects.get(usuario=request.user)
        
        if medico_perfil.especialidad:
            tipo_esp = medico_perfil.especialidad.tipo.lower() if medico_perfil.especialidad.tipo else ''
            nombre_esp = medico_perfil.especialidad.nombre.lower() if medico_perfil.especialidad.nombre else ''
            es_prenatal = (
                tipo_esp == 'prenatal' or 
                'ginecolog' in nombre_esp or 
                'obstetr' in nombre_esp or
                'prenatal' in nombre_esp
            )
        else:
            es_prenatal = True  # Si no tiene especialidad, mostrar opciones prenatales
    except Exception:
        es_prenatal = True  # Por defecto mostrar opciones prenatales

    # Badge de citas pendientes (hoy)
    try:
        from django.utils import timezone
        from citas.models import Cita
        hoy = timezone.now().date()
        sb_citas_pendientes = Cita.objects.filter(
            medico=request.user,
            estado='pendiente',
            fecha=hoy,
        ).count()
    except Exception:
        sb_citas_pendientes = 0

    return {
        'es_prenatal':         es_prenatal,
        'sb_citas_pendientes': sb_citas_pendientes,
    }

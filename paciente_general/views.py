from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from citas.models import Cita
from medicos.models import Medico
from landing.models import Especialidad
from usuarios.models import Usuario, LogAuditoria
from django.contrib.auth import authenticate, login as auth_login
from functools import wraps
from .models import ConsultaGeneral


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def auto_cancelar_citas(user):
    """Cancela citas vencidas dando 30 min de margen al paciente."""
    from django.db.models import Q
    from datetime import timedelta, datetime
    from zoneinfo import ZoneInfo

    ecuador = ZoneInfo('America/Guayaquil')
    ahora_ec = datetime.now(ecuador)
    hoy = ahora_ec.date()
    limite = (ahora_ec - timedelta(minutes=30)).time()

    Cita.objects.filter(paciente=user, estado='pendiente').filter(
        Q(fecha__lt=hoy) | Q(fecha=hoy, hora__lt=limite)
    ).update(estado='cancelada')


def registrar_log(request, accion, modulo='', descripcion='', severidad='INFO', usuario=None):
    """Registra una acción en el log de auditoría.
    Por defecto usa request.user; si se pasa `usuario` explícito (útil en login,
    donde request.user todavía no está autenticado en el momento del registro),
    se usa ese en su lugar."""
    try:
        actor = usuario if usuario is not None else (
            request.user if request.user.is_authenticated else None
        )
        LogAuditoria.objects.create(
            usuario     = actor,
            accion      = accion,
            modulo      = modulo,
            descripcion = descripcion,
            ip_address  = get_client_ip(request),
            severidad   = severidad,
        )
    except Exception:
        pass  # Nunca romper el flujo por un log fallido


def no_cache_view(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    return wrapper


def paciente_general_required(view_func):
    """
    Decorator: accesible por cualquier paciente (general o prenatal).
    Una paciente general con módulo prenatal también puede ver su historial general.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.rol != 'paciente':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@paciente_general_required
@no_cache_view
def dashboard(request):
    user = request.user
    hoy = timezone.localdate()

    # ── AUTO-CANCELAR citas vencidas (con 30 min de margen) ──
    auto_cancelar_citas(user)

    proxima_cita = Cita.objects.filter(
        paciente=user, fecha__gte=hoy, estado__in=['pendiente', 'confirmada']
    ).order_by('fecha', 'hora').first()
    total_citas = Cita.objects.filter(paciente=user).count()
    citas_pendientes = Cita.objects.filter(
        paciente=user, estado__in=['pendiente', 'confirmada'], fecha__gte=hoy
    ).count()
    ultimas_citas = Cita.objects.filter(paciente=user).order_by('-fecha', 'hora')[:3]
    
    # ── CONSULTAS ──
    ultima_consulta = ConsultaGeneral.objects.filter(
        paciente=user
    ).order_by('-fecha').first()
    total_consultas = ConsultaGeneral.objects.filter(paciente=user).count()
    
    perfil = getattr(user, 'paciente', None)
    tiene_prenatal_activo = bool(
        perfil
        and getattr(perfil, 'tiene_prenatal', False)
        and getattr(perfil, 'estado_embarazo', '') == 'ACTIVO'
    )
    parto_programado = None
    if tiene_prenatal_activo:
        from .models import ProgramacionParto
        parto_programado = ProgramacionParto.objects.filter(
            paciente=user,
            estado__in=['programado', 'confirmado']
        ).first()

    return render(request, 'paciente_general/dashboard.html', {
        'user': user,
        'tiene_prenatal_activo': tiene_prenatal_activo,
        'proxima_cita': proxima_cita,
        'total_citas': total_citas,
        'citas_pendientes': citas_pendientes,
        'ultimas_citas': ultimas_citas,
        'hoy': hoy,
        'parto_programado': parto_programado,
        'ultima_consulta': ultima_consulta,
        'total_consultas': total_consultas,
    })

@login_required
@paciente_general_required
def dismiss_prenatal_welcome(request):
    if hasattr(request.user, 'paciente'):
        request.user.paciente.mensaje_prenatal_visto = True
        request.user.paciente.save()
    from django.http import JsonResponse
    return JsonResponse({'status': 'ok'})


@paciente_general_required
@no_cache_view
def mis_citas(request):
    user = request.user
    hoy = timezone.localdate()

    # ── AUTO-CANCELAR citas vencidas (con 30 min de margen) ──
    auto_cancelar_citas(user)

    citas_proximas = Cita.objects.filter(
        paciente=user, fecha__gte=hoy
    ).order_by('fecha', 'hora')
    citas_pasadas = Cita.objects.filter(
        paciente=user, fecha__lt=hoy
    ).order_by('-fecha', 'hora')
    todas = Cita.objects.filter(paciente=user)
    citas_pendientes_badge = Cita.objects.filter(
        paciente=user, estado__in=['pendiente', 'confirmada'], fecha__gte=hoy
    ).count()
    return render(request, 'paciente_general/mis_citas.html', {
        'citas_proximas': citas_proximas,
        'citas_pasadas':  citas_pasadas,
        'hoy':            hoy,
        'citas_pendientes': citas_pendientes_badge,
        'total_citas':    todas.count(),
        'pendientes':     todas.filter(estado__in=['pendiente', 'confirmada']).count(),
        'atendidas':      todas.filter(estado='atendido').count(),
        'canceladas':     todas.filter(estado__in=['cancelada', 'cancelado']).count(),
    })


@paciente_general_required
def cancelar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
    if request.method == 'POST':
        motivo_cancelacion = request.POST.get('motivo_cancelacion', '').strip()
        cita.estado = 'cancelada'
        cita.motivo_cancelacion = motivo_cancelacion
        cita.save()
        registrar_log(request, 'CANCELACION', 'Citas',
            f'Cita #{cita.id} cancelada por el paciente. Motivo: {motivo_cancelacion}', 'INFO')
        messages.success(request, 'Cita cancelada correctamente.')
    return redirect('paciente_general_citas')


@paciente_general_required
@no_cache_view
def agendar_cita(request):
    especialidades = Especialidad.objects.filter(activo=True).exclude(nombre__icontains='parto').exclude(nombre__icontains='cesárea')
    if request.method == 'POST':
        especialidad_id = request.POST.get('especialidad')
        medico_id = request.POST.get('medico')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        if especialidad_id and medico_id and fecha and hora:
            from datetime import date
            hoy = timezone.localdate()
            hora_actual = timezone.localtime().time()
            fecha_obj = date.fromisoformat(fecha)
            
            # Validar fecha y hora pasada
            from datetime import time
            h_h, h_m = map(int, hora.split(':'))
            hora_obj = time(h_h, h_m)

            if fecha_obj < hoy or (fecha_obj == hoy and hora_obj < hora_actual):
                messages.error(request, 'No puedes agendar una cita en una fecha u hora pasada.')
                return render(request, 'paciente_general/agendar_cita.html', {
                    'especialidades': especialidades,
                    'hoy': hoy,
                })
            medico = get_object_or_404(Medico, id=medico_id)
            motivo = request.POST.get('motivo', '').strip()

            # Verificar que el horario no esté ocupado
            if Cita.objects.filter(
                medico=medico.usuario,
                fecha=fecha,
                hora=hora,
                estado__in=['pendiente', 'confirmada', 'atendido']
            ).exists():
                messages.error(request, 'Ese horario ya está ocupado para el médico seleccionado. Por favor elige otra hora.')
                return render(request, 'paciente_general/agendar_cita.html', {
                    'especialidades': especialidades,
                    'hoy': hoy,
                })

            cita = Cita.objects.create(
                paciente=request.user,
                medico=medico.usuario,
                fecha=fecha,
                hora=hora,
                estado='pendiente',
                especialidad_id=especialidad_id,
                motivo=motivo,
            )
            registrar_log(request, 'CREATE', 'Citas',
                f'Cita #{cita.id} agendada para {fecha} {hora}', 'INFO')
            messages.success(request, '¡Cita agendada correctamente!')
            return redirect('paciente_general_citas')
        else:
            messages.error(request, 'Por favor completa todos los campos.')
    hoy = timezone.localdate()
    citas_pendientes_badge = Cita.objects.filter(
        paciente=request.user, estado__in=['pendiente', 'confirmada'], fecha__gte=hoy
    ).count()
    return render(request, 'paciente_general/agendar_cita.html', {
        'especialidades': especialidades,
        'hoy': hoy,
        'citas_pendientes': citas_pendientes_badge,
    })


@paciente_general_required
@no_cache_view
def mi_perfil(request):
    user = request.user
    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'datos')

        if form_type == 'datos':
            user.first_name = request.POST.get('first_name', user.first_name).strip()
            user.last_name  = request.POST.get('last_name',  user.last_name).strip()
            user.email      = request.POST.get('email',      user.email).strip()
            user.save()
            registrar_log(request, 'UPDATE', 'Perfil',
                'El paciente actualizó sus datos personales', 'INFO')
            messages.success(request, 'Datos personales actualizados correctamente.')

        elif form_type == 'password':
            password_actual    = request.POST.get('password_actual', '')
            password_nueva     = request.POST.get('password_nueva', '')
            password_confirmar = request.POST.get('password_confirmar', '')

            if not user.check_password(password_actual):
                messages.error(request, 'La contraseña actual es incorrecta.')
            elif password_nueva != password_confirmar:
                messages.error(request, 'Las contraseñas nuevas no coinciden.')
            elif len(password_nueva) < 8:
                messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            else:
                user.set_password(password_nueva)
                user.save()
                registrar_log(request, 'UPDATE', 'Perfil',
                    'El paciente cambió su contraseña', 'INFO')
                messages.success(request, 'Contraseña actualizada correctamente. Por favor inicia sesión nuevamente.')
                return redirect('login')

        return redirect('paciente_general_perfil')

    hoy = timezone.localdate()
    citas_pendientes_badge = Cita.objects.filter(
        paciente=user, estado__in=['pendiente', 'confirmada'], fecha__gte=hoy
    ).count()
    return render(request, 'paciente_general/mi_perfil.html', {
        'user': user,
        'citas_pendientes': citas_pendientes_badge,
    })


def medicos_disponibles(request):
    especialidad_id = request.GET.get('especialidad_id')
    if especialidad_id:
        medicos = Medico.objects.filter(
            especialidad_id=especialidad_id
        ).select_related('usuario')
        data = [{'id': m.id, 'nombre': str(m)} for m in medicos]
    else:
        data = []
    return JsonResponse({'medicos': data})


def horas_disponibles(request):
    from datetime import date, time
    medico_id = request.GET.get('medico_id')
    fecha = request.GET.get('fecha')
    
    # Horarios según día de la semana
    # Lunes a Viernes: 8:30 - 17:00
    horas_semana = [
        '08:30', '09:00', '09:30', '10:00', '10:30',
        '11:00', '11:30', '12:00', '12:30', '13:00', '13:30',
        '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00',
    ]
    # Sábados y Domingos: 9:00 - 15:00
    horas_finde = [
        '09:00', '09:30', '10:00', '10:30',
        '11:00', '11:30', '12:00', '12:30',
        '13:00', '13:30', '14:00', '14:30', '15:00',
    ]
    
    if medico_id and fecha:
        fecha_obj = date.fromisoformat(fecha)
        es_finde = fecha_obj.weekday() in [5, 6]  # 5=sábado, 6=domingo
        todas_horas = horas_finde if es_finde else horas_semana
        
        ocupadas = Cita.objects.filter(
            medico_id=medico_id, fecha=fecha, estado__in=['pendiente', 'confirmada']
        ).values_list('hora', flat=True)
        ocupadas_str = [str(h)[:5] for h in ocupadas]
        
        # Filtro de horas pasadas si es hoy
        hoy = timezone.localdate()
        
        if fecha_obj == hoy:
            hora_actual = timezone.localtime().time()
            hora_actual_str = f"{hora_actual.hour:02d}:{hora_actual.minute:02d}"
            disponibles = [h for h in todas_horas if h not in ocupadas_str and h > hora_actual_str]
        elif fecha_obj < hoy:
            disponibles = []
        else:
            disponibles = [h for h in todas_horas if h not in ocupadas_str]
    else:
        disponibles = horas_semana
    return JsonResponse({'horas': disponibles})


@paciente_general_required
@no_cache_view
def mis_consultas(request):
    """Muestra el historial de consultas generales del paciente."""
    user = request.user
    hoy = timezone.localdate()
    
    # Obtener todas las consultas del paciente
    consultas = ConsultaGeneral.objects.filter(
        paciente=user
    ).select_related('medico').order_by('-fecha')
    
    # Filtros opcionales
    filtro_medico = request.GET.get('medico_id', '')
    filtro_mes = request.GET.get('mes', '')
    
    if filtro_medico:
        consultas = consultas.filter(medico_id=filtro_medico)
    
    if filtro_mes:
        try:
            año, mes = map(int, filtro_mes.split('-'))
            consultas = consultas.filter(fecha__year=año, fecha__month=mes)
        except:
            pass
    
    # Médicos únicos para el filtro
    medicos_unicos = ConsultaGeneral.objects.filter(
        paciente=user
    ).values_list('medico__id', 'medico__first_name', 'medico__last_name').distinct()
    
    # Stats
    total_consultas = ConsultaGeneral.objects.filter(paciente=user).count()
    citas_pendientes_badge = Cita.objects.filter(
        paciente=user, estado__in=['pendiente', 'confirmada'], fecha__gte=hoy
    ).count()
    
    return render(request, 'paciente_general/mis_consultas.html', {
        'consultas': consultas,
        'total_consultas': total_consultas,
        'citas_pendientes': citas_pendientes_badge,
        'medicos_unicos': medicos_unicos,
        'filtro_medico': filtro_medico,
        'filtro_mes': filtro_mes,
    })


@paciente_general_required
def ver_consulta(request, consulta_id):
    """Muestra el detalle de una consulta específica."""
    user = request.user
    consulta = get_object_or_404(ConsultaGeneral, id=consulta_id, paciente=user)
    
    hoy = timezone.localdate()
    citas_pendientes_badge = Cita.objects.filter(
        paciente=user, estado__in=['pendiente', 'confirmada'], fecha__gte=hoy
    ).count()
    
    return render(request, 'paciente_general/ver_consulta.html', {
        'consulta': consulta,
        'citas_pendientes': citas_pendientes_badge,
    })


@paciente_general_required
def descargar_consulta_pdf(request, consulta_id):
    """Descarga en PDF una consulta del paciente."""
    user = request.user
    consulta = get_object_or_404(ConsultaGeneral, id=consulta_id, paciente=user)
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib import colors
        from io import BytesIO
        from datetime import datetime
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#B03580'),
            spaceAfter=6,
            alignment=1,  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#8A2563'),
            spaceAfter=6,
            spaceBefore=12,
        )
        
        # Título
        story.append(Paragraph('ZUMEDICAL — Consulta General', title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Información del paciente
        paciente_data = [
            ['Paciente:', consulta.paciente.get_full_name()],
            ['Médico:', consulta.medico.get_full_name() if consulta.medico else 'N/A'],
            ['Fecha:', consulta.fecha.strftime('%d/%m/%Y')],
            ['IMC:', f"{consulta.imc} kg/m²" if consulta.imc else 'N/A'],
        ]
        paciente_table = Table(paciente_data, colWidths=[1.5*inch, 4*inch])
        paciente_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FBF0F7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E8AAD4')),
        ]))
        story.append(paciente_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Motivo de consulta
        story.append(Paragraph('MOTIVO DE CONSULTA', heading_style))
        story.append(Paragraph(consulta.motivo_consulta or 'N/A', styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Signos vitales
        story.append(Paragraph('SIGNOS VITALES', heading_style))
        vitales_data = [
            ['PA', 'FC', 'FR', 'Temp', 'SpO₂', 'Peso', 'Talla'],
            [
                consulta.presion_arterial or 'N/A',
                str(consulta.frecuencia_cardiaca) if consulta.frecuencia_cardiaca else 'N/A',
                str(consulta.frecuencia_respiratoria) if consulta.frecuencia_respiratoria else 'N/A',
                str(consulta.temperatura) if consulta.temperatura else 'N/A',
                str(consulta.saturacion_oxigeno) if consulta.saturacion_oxigeno else 'N/A',
                str(consulta.peso) if consulta.peso else 'N/A',
                str(consulta.talla) if consulta.talla else 'N/A',
            ]
        ]
        vitales_table = Table(vitales_data, colWidths=[0.8*inch]*7)
        vitales_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#B03580')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E8AAD4')),
        ]))
        story.append(vitales_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Examen físico
        if consulta.examen_fisico:
            story.append(Paragraph('EXAMEN FÍSICO', heading_style))
            story.append(Paragraph(consulta.examen_fisico, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Diagnósticos
        if consulta.diagnosticos:
            story.append(Paragraph('DIAGNÓSTICOS', heading_style))
            diag_data = [['Patología', 'CIE-10', 'Tipo']]
            for d in consulta.diagnosticos:
                tipo = 'Presuntivo' if d['presuntivo'] else ('Definitivo' if d['definitivo'] else 'N/A')
                diag_data.append([d['patologia'], d['cie10'] or 'N/A', tipo])
            diag_table = Table(diag_data, colWidths=[3*inch, 1.2*inch, 1.3*inch])
            diag_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#B03580')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E8AAD4')),
            ]))
            story.append(diag_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Plan y tratamiento
        if consulta.plan:
            story.append(Paragraph('PLAN', heading_style))
            story.append(Paragraph(consulta.plan, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        if consulta.tratamiento:
            story.append(Paragraph('TRATAMIENTO', heading_style))
            story.append(Paragraph(consulta.tratamiento, styles['Normal']))
        
        # Generar PDF
        doc.build(story)
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f"Consulta_{consulta.paciente.get_full_name()}_{consulta.fecha.strftime('%d_%m_%Y')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except ImportError:
        messages.error(request, 'No se puede generar el PDF en este momento.')
        return redirect('paciente_general_consultas')



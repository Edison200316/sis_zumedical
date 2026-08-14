"""
Asistente Virtual de Zumedical — Backend del chatbot guiado por menús.
"""

import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import InteraccionChatbot
from ai.knowledge_base import CATEGORIAS_CHATBOT, FAQ_CHATBOT


# ---------------------------------------------------------------------------
# Respuestas de texto del bot (centralizado para fácil edición)
# ---------------------------------------------------------------------------
MSG_BIENVENIDA = (
    "Hola, soy el <strong>Asistente Virtual de Zumedical</strong>.<br><br>"
    "Estoy aquí para ayudarte con información sobre nuestros servicios, "
    "el embarazo y el uso de la plataforma.<br><br>"
    "Selecciona una de las siguientes categorías para comenzar:"
)

MSG_CATEGORIA = "Has seleccionado <strong>{nombre}</strong>. ¿Sobre qué deseas saber?"

MSG_RESPUESTA_FOOTER = (
    "<br><br><em>⚕️ Recuerda que este asistente brinda información general. "
    "Para diagnósticos o situaciones de emergencia, consulta a tu médico.</em>"
)

MSG_NO_ENCONTRADO = (
    "No encontré esa opción. Por favor selecciona una de las categorías del menú."
)

MSG_EMERGENCIA = (
    "🚨 <strong>En caso de emergencia</strong>, llama inmediatamente al "
    "<strong>+593 98 123 4567</strong> o acude a urgencias más cercanas."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')


def _build_categorias_payload():
    """Devuelve la lista de categorías con emoji y nombre para el frontend."""
    categorias_con_faqs = {faq["categoria"] for faq in _get_faqs_activas()}
    return [
        {
            "slug": cat["slug"],
            "nombre": cat["nombre"],
            "emoji": cat["emoji"],
            "descripcion": cat["descripcion"],
        }
        for cat in CATEGORIAS_CHATBOT
        if cat["slug"] in categorias_con_faqs
    ]


def _get_faqs_activas():
    faqs = []
    for index, faq in enumerate(FAQ_CHATBOT, start=1):
        if faq.get("activo", True):
            faqs.append({
                "id": faq.get("id", index),
                "categoria": faq.get("categoria", ""),
                "pregunta": faq.get("pregunta", ""),
                "respuesta": faq.get("respuesta", ""),
                "palabras_clave": faq.get("palabras_clave", ""),
                "orden": faq.get("orden", index),
            })
    return faqs


def _build_preguntas_payload(categoria_slug):
    """Devuelve las preguntas activas de una categoría."""
    faqs = [
        {"id": faq["id"], "pregunta": faq["pregunta"]}
        for faq in _get_faqs_activas()
        if faq["categoria"] == categoria_slug
    ]
    return sorted(faqs, key=lambda faq: faq["id"])


def _get_faq_por_id(faq_id):
    return next((faq for faq in _get_faqs_activas() if faq["id"] == faq_id), None)


def _get_categoria_nombre(categoria_slug):
    categoria = next((cat for cat in CATEGORIAS_CHATBOT if cat["slug"] == categoria_slug), None)
    return categoria["nombre"] if categoria else categoria_slug


def _log_interaccion(request, estado, pregunta_texto, respuesta_texto, faq_pregunta=''):
    try:
        InteraccionChatbot.objects.create(
            canal='landing',
            estado=estado,
            pregunta=pregunta_texto,
            respuesta=respuesta_texto,
            pregunta_relacionada=faq_pregunta,
            direccion_ip=_get_client_ip(request),
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Vista principal del chatbot
# ---------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(['POST'])
def chatbot_response(request):
    """
    Endpoint único del asistente virtual.

    Payload esperado:
        {
            "estado": "inicio" | "cat:<slug>" | "faq:<id>" | "volver",
            "canal":  "landing"   (opcional)
        }

    Respuesta exitosa:
        {
            "tipo":       "bienvenida" | "categorias" | "preguntas" | "respuesta",
            "mensaje":    "<html permitido>",
            "categorias": [...],   // solo en tipo=bienvenida/categorias
            "preguntas":  [...],   // solo en tipo=preguntas
            "categoria":  {...},   // solo en tipo=preguntas
        }
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    estado = data.get('estado', 'inicio').strip().lower()

    # ── INICIO / VOLVER ─────────────────────────────────────────────────────
    if estado in ('inicio', 'volver', ''):
        categorias = _build_categorias_payload()
        _log_interaccion(request, 'inicio', 'inicio', MSG_BIENVENIDA)
        return JsonResponse({
            'tipo': 'bienvenida',
            'mensaje': MSG_BIENVENIDA,
            'categorias': categorias,
        })

    # ── SELECCIÓN DE CATEGORÍA ───────────────────────────────────────────────
    if estado.startswith('cat:'):
        slug = estado[4:]
        cat_info = next((c for c in CATEGORIAS_CHATBOT if c['slug'] == slug), None)

        if not cat_info:
            return JsonResponse({'tipo': 'error', 'mensaje': MSG_NO_ENCONTRADO})

        preguntas = _build_preguntas_payload(slug)
        if not preguntas:
            return JsonResponse({'tipo': 'error', 'mensaje': MSG_NO_ENCONTRADO})

        mensaje = MSG_CATEGORIA.format(nombre=cat_info['nombre'])
        _log_interaccion(request, estado, cat_info['nombre'], mensaje)

        return JsonResponse({
            'tipo': 'preguntas',
            'mensaje': mensaje,
            'categoria': {
                'slug': cat_info['slug'],
                'nombre': cat_info['nombre'],
                'emoji': cat_info['emoji'],
            },
            'preguntas': preguntas,
        })

    # ── SELECCIÓN DE PREGUNTA ────────────────────────────────────────────────
    if estado.startswith('faq:'):
        try:
            faq_id = int(estado[4:])
        except ValueError:
            return JsonResponse({'tipo': 'error', 'mensaje': MSG_NO_ENCONTRADO})

        faq = _get_faq_por_id(faq_id)
        if not faq:
            return JsonResponse({'tipo': 'error', 'mensaje': MSG_NO_ENCONTRADO})

        # Agregar footer de advertencia médica si es categoría de síntomas
        respuesta = faq["respuesta"]
        if faq["categoria"] == 'sintomas_alarmas':
            respuesta += MSG_RESPUESTA_FOOTER

        _log_interaccion(
            request, estado,
            faq["pregunta"], respuesta,
            faq_pregunta=faq["pregunta"],
        )

        return JsonResponse({
            'tipo': 'respuesta',
            'mensaje': respuesta,
            'faq': {
                'id': faq["id"],
                'pregunta': faq["pregunta"],
                'categoria_slug': faq["categoria"],
                'categoria_nombre': _get_categoria_nombre(faq["categoria"]),
            },
        })

    # ── FALLBACK ─────────────────────────────────────────────────────────────
    return JsonResponse({'tipo': 'error', 'mensaje': MSG_NO_ENCONTRADO})


# ---------------------------------------------------------------------------
# Página del chatbot para paciente autenticada (RF - Asistente Virtual)
# ---------------------------------------------------------------------------

@login_required
def chatbot_page(request):
    """
    Página del Asistente Virtual para la paciente prenatal autenticada.
    Solo accesible por pacientes (prenatal); los demás roles se redirigen.
    """
    user = request.user

    # Guard de rol
    if user.rol != 'paciente':
        return redirect('login')
    if not user.puede_prenatal:
        return redirect('paciente_general_dashboard')

    from pacientes.models import Paciente
    perfil = Paciente.objects.filter(usuario=user).first()

    return render(request, 'paciente/chatbot.html', {
        'perfil': perfil,
        'chatbot_endpoint': '/chatbot/response/',
    })

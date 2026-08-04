"""
Base de conocimiento del Asistente Virtual de Zumedical.
Integra datos dinámicos del landing page para respuestas profesionales y actualizadas.

CATEGORÍAS:
    centro_medico        → 10 preguntas (con datos del landing)
    citas_medicas        → 12 preguntas
    controles_prenatales → 20 preguntas
    sintomas_alarmas     → 20 preguntas
    nutricion            → 15 preguntas
    uso_sistema          → 10 preguntas
    posparto_lactancia   → 15 preguntas
    TOTAL                → 102 preguntas
"""

def obtener_especialidades_info():
    """
    Obtiene información real de especialidades de la landing para el chatbot.
    """
    try:
        from landing.models import Especialidad
        especialidades = Especialidad.objects.filter(activo=True)
        
        info = ""
        for esp in especialidades:
            info += f"- {esp.nombre}: {esp.descripcion}\n"
        
        return info if info else ""
    except:
        return ""


def construir_respuesta_especialidades():
    """
    Construye una respuesta dinámica sobre especialidades.
    """
    esp_info = obtener_especialidades_info()
    
    if esp_info:
        return f"""Nuestras especialidades principales son:

{esp_info}

Todos nuestros especialistas tienen amplia experiencia en atención de calidad. ¿Cuál especialidad te interesa?"""
    else:
        return """Nuestras especialidades principales incluyen: Obstetricia y Ginecología, Medicina Materno-Fetal especializada, Nutrición Gestacional, Enfermería Obstétrica, Ecografía con equipos de última tecnología, y evaluación de riesgo mediante sistemas de IA. Todos nuestros especialistas tienen amplia experiencia en atención prenatal de alto nivel."""


# ---------------------------------------------------------------------------
# Metadatos de categorías (para construir el menú principal del chatbot)
# ---------------------------------------------------------------------------
CATEGORIAS_CHATBOT = [
    {
        "slug": "centro_medico",
        "nombre": "Centro Médico",
        "emoji": "🏥",
        "descripcion": "Información general sobre Zumedical",
    },
    {
        "slug": "citas_medicas",
        "nombre": "Citas Médicas",
        "emoji": "📅",
        "descripcion": "Agendar, cancelar o cambiar citas",
    },
    {
        "slug": "controles_prenatales",
        "nombre": "Controles Prenatales",
        "emoji": "🤰",
        "descripcion": "Todo sobre el seguimiento del embarazo",
    },
    {
        "slug": "sintomas_alarmas",
        "nombre": "Síntomas y Alarmas",
        "emoji": "⚠️",
        "descripcion": "Señales normales y signos de riesgo",
    },
    {
        "slug": "nutricion",
        "nombre": "Nutrición y Vida Sana",
        "emoji": "🥗",
        "descripcion": "Alimentación y hábitos durante el embarazo",
    },
    {
        "slug": "uso_sistema",
        "nombre": "Uso del Sistema",
        "emoji": "💻",
        "descripcion": "Cómo utilizar la plataforma Zumedical",
    },
    {
        "slug": "posparto_lactancia",
        "nombre": "Posparto y Lactancia",
        "emoji": "👶",
        "descripcion": "Cuidados después del parto y lactancia",
    },
]


# ---------------------------------------------------------------------------
# CATEGORÍA 1: Centro Médico (10 preguntas) - DATOS REALES DEL LANDING
# ---------------------------------------------------------------------------
_CENTRO_MEDICO = [
    {
        "categoria": "centro_medico",
        "pregunta": "¿Quiénes son Zumedical?",
        "respuesta": "Zumedical es un centro médico especializado en salud de la mujer y atención prenatal. Contamos con un equipo de obstetras, ginecólogos, nutricionistas y enfermeras especializadas para acompañarte en cada etapa de tu embarazo. Nuestro lema es: 'Cuidando tu salud con prioridad'.",
        "palabras_clave": "quienes somos, zumedical, centro médico, nosotros",
    },
    {
        "categoria": "centro_medico",
        "pregunta": "¿Qué servicios ofrece Zumedical?",
        "respuesta": construir_respuesta_especialidades(),
        "palabras_clave": "servicios, que ofrecen, atención, especialidades, programas",
    },
    {
        "categoria": "centro_medico",
        "pregunta": "¿Dónde están ubicados?",
        "respuesta": "Zumedical cuenta con una ubicación accesible con fácil estacionamiento y todas las comodidades. Puedes encontrarnos buscando 'Zumedical Centro Médico' en Google Maps. Para indicaciones específicas o consultas sobre cómo llegar, llámanos al +593 99 000 0000.",
        "palabras_clave": "ubicación, dirección, dónde, lugar, cómo llegar",
    },
    {
        "categoria": "centro_medico",
        "pregunta": "¿Cuál es el horario de atención?",
        "respuesta": "Nuestro horario de atención es: Lunes a Viernes de 08:30 a 17:00 (horario corrido con pausa breve para almuerzo). Sábados de 08:00 a 13:00. Para emergencias obstétricas disponemos de atención las 24 horas, 365 días del año. Llama al +593 99 000 0000 en caso de emergencia.",
        "palabras_clave": "horario, cuando abren, atienden, horas, días, atención",
    },
    {
        "categoria": "centro_medico",
        "pregunta": "¿Atienden los sábados?",
        "respuesta": "Sí, atendemos los sábados de 08:00 a 13:00. Te recomendamos agendar tu cita con al menos 3 días de anticipación ya que la disponibilidad es limitada los fines de semana. Llama al +593 99 000 0000 para reservar.",
        "palabras_clave": "sábado, fin de semana, atienden sábados, horario",
    },
    {
        "categoria": "centro_medico",
        "pregunta": "¿Atienden los domingos?",
        "respuesta": "Los domingos no tenemos atención programada en horario regular. Sin embargo, para emergencias obstétricas estamos disponibles las 24 horas. Si presentas algún signo de alarma el domingo, no dudes en llamar al +593 99 000 0000 inmediatamente.",
        "palabras_clave": "domingo, fin de semana, atienden domingos, emergencias",
    },
    {
        "categoria": "centro_medico",
        "pregunta": "¿Cómo puedo contactarlos?",
        "respuesta": "Puedes contactarnos de varias formas: Teléfono/WhatsApp: +593 99 000 0000 | Correo electrónico: contacto@zumedical.ec | A través de la plataforma en la sección 'Mensajes' si ya tienes cuenta registrada. Nuestro equipo de atención al cliente responde en horario laboral dentro de máximo 2 horas.",
        "palabras_clave": "contactar, teléfono, whatsapp, correo, comunicarse, llamar",
    },
    {
        "categoria": "centro_medico",
        "pregunta": "¿Qué especialidades tienen?",
        "respuesta": construir_respuesta_especialidades(),
        "palabras_clave": "especialidades, médicos, especialistas, obstetra, ginecólogo, servicios",
    },
    {
        "categoria": "centro_medico",
        "pregunta": "¿Atienden emergencias obstétricas?",
        "respuesta": "Sí, contamos con un servicio de emergencias obstétricas disponible las 24 horas con equipamiento de última tecnología. Si presentas sangrado vaginal, dolor abdominal intenso, pérdida de líquido amniótico, ausencia de movimientos fetales o cualquier signo de alarma, comunícate de inmediato al +593 99 000 0000.",
        "palabras_clave": "emergencias, urgencia, 24 horas, obstétrica, urgencias, señales",
    },
    {
        "categoria": "centro_medico",
        "pregunta": "¿Aceptan seguros médicos?",
        "respuesta": "Trabajamos con los principales seguros médicos del país incluyendo IESS. Para verificar si tu seguro específico tiene cobertura en Zumedical, te recomendamos contactar directamente con nuestro personal administrativo al +593 99 000 0000 o enviar un correo a contacto@zumedical.ec.",
        "palabras_clave": "seguro, seguro médico, cobertura, IESS, privado, pago",
    },
]


# ---------------------------------------------------------------------------
# CATEGORÍA 2: Citas Médicas (12 preguntas)
# ---------------------------------------------------------------------------
_CITAS_MEDICAS = [
    {
        "categoria": "citas_medicas",
        "pregunta": "¿Cómo agendar una cita?",
        "respuesta": "Para agendar una cita: 1) Inicia sesión en tu cuenta Zumedical. 2) Ve al menú 'Citas' → 'Nueva Cita'. 3) Selecciona especialidad, médico, fecha y hora disponible. 4) Confirma la reserva. Recibirás una notificación de confirmación.",
        "palabras_clave": "agendar, cita, reservar, programar, nueva cita",
    },
    {
        "categoria": "citas_medicas",
        "pregunta": "¿Cómo cancelar una cita?",
        "respuesta": "Para cancelar: 1) Inicia sesión. 2) Ve a 'Mis Citas'. 3) Selecciona la cita que deseas cancelar. 4) Haz clic en 'Cancelar cita' y confirma. Te pedimos cancelar con al menos 24 horas de anticipación.",
        "palabras_clave": "cancelar, cita, eliminar, quitar cita",
    },
    {
        "categoria": "citas_medicas",
        "pregunta": "¿Cómo cambiar o reagendar una cita?",
        "respuesta": "Para reagendar: 1) Ve a 'Mis Citas'. 2) Selecciona la cita. 3) Haz clic en 'Reagendar'. 4) Elige la nueva fecha y hora disponible. 5) Confirma el cambio.",
        "palabras_clave": "cambiar, reagendar, modificar, reprogramar, cita",
    },
    {
        "categoria": "citas_medicas",
        "pregunta": "¿Cómo ver mis citas programadas?",
        "respuesta": "Ve a tu panel de paciente → sección 'Mis Citas'. Verás todas tus citas programadas, pasadas y pendientes con fecha, hora y médico asignado.",
        "palabras_clave": "ver citas, mis citas, citas programadas, próximas citas",
    },
    {
        "categoria": "citas_medicas",
        "pregunta": "¿Qué hago si llego tarde a mi cita?",
        "respuesta": "Si vas a llegar tarde, comunícate al +593 98 123 4567 lo antes posible. Dependiendo del tiempo de retraso y la disponibilidad del médico, se evaluará si puedes ser atendida o se reagendará tu cita.",
        "palabras_clave": "tarde, llegar tarde, retraso, puntualidad",
    },
    {
        "categoria": "citas_medicas",
        "pregunta": "¿Qué documentos debo llevar?",
        "respuesta": "Para tu primera cita lleva: cédula de identidad, carnet de seguro médico (si aplica), resultados de exámenes previos, ecografías anteriores y cualquier documentación médica relevante. En controles siguientes lleva tu carnet prenatal.",
        "palabras_clave": "documentos, llevar, cédula, carnet, papeles",
    },
    {
        "categoria": "citas_medicas",
        "pregunta": "¿Cuánto dura una consulta prenatal?",
        "respuesta": "Una consulta prenatal estándar dura entre 20 y 30 minutos. La primera consulta puede extenderse a 45-60 minutos ya que incluye la historia clínica completa y evaluación inicial.",
        "palabras_clave": "duración, cuánto tiempo, dura, consulta",
    },
    {
        "categoria": "citas_medicas",
        "pregunta": "¿Cómo sé que mi cita quedó confirmada?",
        "respuesta": "Recibirás una notificación en el sistema y/o un mensaje al número registrado en tu perfil. También puedes verificarlo en 'Mis Citas' donde aparecerá el estado 'Confirmada'.",
        "palabras_clave": "confirmar, confirmación, cita confirmada, verificar",
    },
    {
        "categoria": "citas_medicas",
        "pregunta": "¿Qué pasa si no asisto a mi cita?",
        "respuesta": "Si no asistes sin cancelar previamente, la cita quedará registrada como 'No asistió'. Te recomendamos siempre cancelar con anticipación para liberar el espacio para otras pacientes.",
        "palabras_clave": "no asistir, falta, ausencia, inasistencia",
    },
    {
        "categoria": "citas_medicas",
        "pregunta": "¿Puedo elegir a mi médico?",
        "respuesta": "Sí, al agendar tu cita puedes seleccionar el médico de tu preferencia según su disponibilidad. Si el médico que prefieres no tiene horarios disponibles, puedes anotarte en lista de espera.",
        "palabras_clave": "elegir médico, escoger doctor, seleccionar médico",
    },
    {
        "categoria": "citas_medicas",
        "pregunta": "¿Con qué anticipación debo agendar?",
        "respuesta": "Recomendamos agendar con al menos 2-3 días de anticipación para garantizar disponibilidad. Para la primera consulta, lo antes posible al confirmar el embarazo.",
        "palabras_clave": "anticipación, cuándo agendar, tiempo, con cuánto",
    },
    {
        "categoria": "citas_medicas",
        "pregunta": "¿Puedo agendar citas para familiar o acompañante?",
        "respuesta": "Cada paciente debe tener su propia cuenta y citas. Sin embargo, puedes registrar el nombre de tu acompañante al agendar la cita para que sea autorizado a ingresar contigo.",
        "palabras_clave": "familiar, acompañante, esposo, acompañar, autorizar",
    },
]


# ---------------------------------------------------------------------------
# CATEGORÍA 3: Controles Prenatales (20 preguntas)
# ---------------------------------------------------------------------------
_CONTROLES_PRENATALES = [
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué es un control prenatal?",
        "respuesta": "El control prenatal es un conjunto de consultas periódicas y exámenes médicos para monitorear la salud de la madre y el bebé durante el embarazo. Su objetivo es detectar riesgos a tiempo, orientar a la madre y garantizar un parto seguro.",
        "palabras_clave": "control prenatal, que es, consulta prenatal",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Cuándo debo iniciar los controles?",
        "respuesta": "Debes iniciar los controles prenatales lo antes posible, idealmente entre las semanas 6 y 10 del embarazo. El primer control es fundamental para establecer la edad gestacional, detectar embarazos múltiples y evaluar factores de riesgo.",
        "palabras_clave": "cuándo iniciar, primer control, inicio, semana",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Cada cuánto debo asistir a controles?",
        "respuesta": "La frecuencia recomendada es: cada 4 semanas hasta la semana 28, cada 2 semanas de la semana 28 a la 36, y semanalmente de la semana 36 al parto. Tu médico puede ajustar esta frecuencia según tu caso.",
        "palabras_clave": "frecuencia, cada cuánto, controles, semanas, veces",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué exámenes me realizan en los controles?",
        "respuesta": "Los exámenes incluyen: hemograma, grupo sanguíneo, glucosa, orina, VDRL (sífilis), VIH, toxoplasmosis, rubéola, hepatitis B, tiroides y pruebas según cada trimestre. Tu médico indicará cuáles corresponden en cada etapa.",
        "palabras_clave": "exámenes, análisis, laboratorio, pruebas, sangre",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué ocurre en la semana 8?",
        "respuesta": "En la semana 8: el bebé mide ~1.6 cm, el corazón late aproximadamente 150 veces por minuto, se forman los brazos y piernas. Es ideal para la primera ecografía que confirma la vitalidad y fecha probable de parto.",
        "palabras_clave": "semana 8, octava semana, desarrollo bebé",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué ocurre en la semana 12?",
        "respuesta": "En la semana 12 (fin del primer trimestre): el bebé mide ~6 cm y ya tiene todos los órganos formados. Se realiza el screening del primer trimestre: ecografía de translucencia nucal + análisis de sangre para detectar cromosompatías.",
        "palabras_clave": "semana 12, primer trimestre, translucencia nucal, screening",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué ocurre en la semana 16?",
        "respuesta": "En la semana 16: el bebé mide ~12 cm, puede escuchar sonidos, se distinguen sus rasgos faciales. Es posible conocer el sexo por ecografía. Se realizan controles rutinarios y se evalúa el crecimiento.",
        "palabras_clave": "semana 16, sexo bebé, rasgos, crecimiento",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué ocurre en la semana 20?",
        "respuesta": "La semana 20 es la mitad del embarazo. Se realiza la ecografía morfológica (estructural), que es la más importante: evalúa todos los órganos del bebé, placenta, líquido amniótico y confirma el sexo.",
        "palabras_clave": "semana 20, ecografía morfológica, estructural, mitad",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué ocurre en la semana 24?",
        "respuesta": "Semana 24: el bebé mide ~30 cm y pesa ~600 g. Se realizan controles de glucosa (test de O'Sullivan) para detectar diabetes gestacional. La madre suele sentir los movimientos con más regularidad.",
        "palabras_clave": "semana 24, glucosa, diabetes gestacional, O'Sullivan",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué ocurre en la semana 28?",
        "respuesta": "Semana 28: inicio del tercer trimestre. El bebé mide ~35 cm y pesa ~1 kg. Los controles se vuelven más frecuentes (cada 2 semanas). Se evalúa la posición fetal y se controlan signos de preeclampsia.",
        "palabras_clave": "semana 28, tercer trimestre, preeclampsia, posición fetal",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué ocurre en la semana 32?",
        "respuesta": "Semana 32: el bebé pesa ~1.8 kg y ocupa la mayor parte del útero. Se evalúa la posición (cefálica o podálica) y se realizan controles de bienestar fetal. Se inicia la planificación del tipo de parto.",
        "palabras_clave": "semana 32, posición, cefálica, podálica, parto",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué ocurre en la semana 36?",
        "respuesta": "Semana 36: el bebé pesa ~2.7 kg y está casi completamente desarrollado. Los controles pasan a ser semanales. Se evalúa la madurez pulmonar, la posición fetal definitiva y se finaliza el plan de parto.",
        "palabras_clave": "semana 36, plan de parto, semanales, madurez",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué ocurre en la semana 38?",
        "respuesta": "Semana 38: el bebé está a término. Se monitorea el bienestar fetal, el cuello uterino y los signos de inicio de trabajo de parto. Tu médico te indicará las señales a las que debes estar atenta.",
        "palabras_clave": "semana 38, término, trabajo de parto, cuello uterino",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué ocurre en la semana 40?",
        "respuesta": "Semana 40: fecha probable de parto. Si no hay inicio espontáneo, el médico evaluará la inducción del parto o cesárea programada según cada caso clínico. El bebé pesa entre 3 y 3.5 kg en promedio.",
        "palabras_clave": "semana 40, fecha de parto, inducción, cesárea",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué ecografías necesito durante el embarazo?",
        "respuesta": "Las ecografías principales son: Semana 8-10 (primera, confirma embarazo), Semana 11-13 (translucencia nucal), Semana 20-22 (morfológica), Semana 30-34 (crecimiento fetal), Semana 36-38 (posición y bienestar final).",
        "palabras_clave": "ecografías, cuántas, ultrasonido, morfológica",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué vitaminas debo tomar?",
        "respuesta": "Las más importantes son: Ácido fólico (desde antes del embarazo hasta semana 12), Hierro (desde semana 16), Calcio, Vitamina D, Omega-3 y Yodo. Tu médico te recetará las vitaminas prenatales adecuadas para tu caso.",
        "palabras_clave": "vitaminas, ácido fólico, hierro, calcio, suplementos",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué controles son obligatorios?",
        "respuesta": "Los controles mínimos recomendados por la OMS son 8 consultas durante el embarazo. En Ecuador, el MSP establece un mínimo de 5 controles. En Zumedical te recomendamos el esquema completo para un seguimiento óptimo.",
        "palabras_clave": "obligatorio, mínimo, cuántos controles, OMS, MSP",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué debo llevar a cada control prenatal?",
        "respuesta": "Lleva siempre: tu carnet o libreta prenatal, resultados de exámenes previos, ecografías anteriores, lista de medicamentos que tomas y cualquier duda o síntoma que hayas tenido desde el último control.",
        "palabras_clave": "llevar, carnet prenatal, documentos, libreta",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué hace el obstetra en cada control?",
        "respuesta": "El obstetra realiza: revisión de presión arterial, peso y talla, altura uterina, latidos cardíacos fetales, movimientos fetales, revisión de resultados de laboratorio, evaluación de síntomas y orientación para el próximo período.",
        "palabras_clave": "obstetra, qué hace, médico, revisión, control",
    },
    {
        "categoria": "controles_prenatales",
        "pregunta": "¿Qué hace la enfermera en el control prenatal?",
        "respuesta": "La enfermera obstétrica realiza: toma de signos vitales (presión, temperatura, pulso), peso, medición del abdomen, orientación sobre lactancia, planificación familiar postparto y educación sobre los cuidados del embarazo.",
        "palabras_clave": "enfermera, enfermería, signos vitales, educación",
    },
]


# ---------------------------------------------------------------------------
# CATEGORÍA 4: Síntomas y Alarmas (20 preguntas)
# IMPORTANTE: El asistente nunca diagnostica. Siempre orienta a consultar.
# ---------------------------------------------------------------------------
_SINTOMAS_ALARMAS = [
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué síntomas son normales en el embarazo?",
        "respuesta": "Son normales: náuseas y vómitos (especialmente en el primer trimestre), cansancio, aumento de la frecuencia urinaria, sensibilidad en los senos, acidez, leve hinchazón en pies al final del día y movimientos fetales regulares.",
        "palabras_clave": "síntomas normales, náuseas, cansancio, molestias",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Cuándo debo acudir al médico urgente?",
        "respuesta": "Acude inmediatamente si tienes: sangrado vaginal, dolor abdominal intenso, fiebre mayor a 38°C, visión borrosa, dolor de cabeza severo, hinchazón repentina en cara o manos, pérdida de líquido amniótico o ausencia de movimientos del bebé.",
        "palabras_clave": "urgente, emergencia, cuándo ir, médico inmediato",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué hago si tengo fiebre?",
        "respuesta": "Si tienes fiebre mayor a 38°C durante el embarazo, comunícate con tu médico de inmediato. Mientras tanto, puedes tomar paracetamol (nunca ibuprofeno ni aspirina sin indicación médica) y mantente bien hidratada.",
        "palabras_clave": "fiebre, temperatura, calentura",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué hago si tengo sangrado vaginal?",
        "respuesta": "Cualquier sangrado vaginal durante el embarazo requiere evaluación médica. Llama inmediatamente al +593 98 123 4567 o acude a urgencias. No uses tampones. El sangrado puede tener varias causas, algunas graves y otras no, pero siempre debe ser evaluado.",
        "palabras_clave": "sangrado, hemorragia, mancha, sangre",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué hago si tengo dolor abdominal?",
        "respuesta": "El dolor leve o tipo cólico ocasional puede ser normal (ligamentos en estiramiento). Sin embargo, si el dolor es intenso, persistente, acompañado de sangrado o contracciones regulares, acude a urgencias de inmediato.",
        "palabras_clave": "dolor abdominal, dolor barriga, cólico, dolor pélvico",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué hago si no siento movimientos del bebé?",
        "respuesta": "A partir de la semana 20-22 debes sentir movimientos regulares. Si notas ausencia o reducción significativa de movimientos por más de 2 horas, acude a urgencias. Puedes estimular al bebé tomando algo dulce y en reposo antes de concluir que no se mueve.",
        "palabras_clave": "movimientos bebé, no se mueve, patadas, ausencia movimientos",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué hago si tengo presión arterial alta?",
        "respuesta": "Si tu presión es ≥ 140/90 mmHg, es una señal de alarma. Reposa, evita el estrés y comunícate de inmediato con tu médico. La hipertensión en el embarazo puede evolucionar a preeclampsia, que es una emergencia médica.",
        "palabras_clave": "presión alta, hipertensión, presión arterial, PA",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué hago si tengo visión borrosa?",
        "respuesta": "La visión borrosa, ver destellos o manchas oscuras durante el embarazo puede ser un signo de preeclampsia. Es una emergencia. Ve a urgencias inmediatamente o llama al +593 98 123 4567.",
        "palabras_clave": "visión borrosa, ver mal, manchas, destellos, ojos",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué hago si tengo dolor de cabeza intenso?",
        "respuesta": "Un dolor de cabeza severo que no cede con paracetamol y está acompañado de presión alta, visión borrosa o hinchazón puede ser signo de preeclampsia. Acude a urgencias de inmediato.",
        "palabras_clave": "dolor cabeza, cefalea, migraña, jaqueca",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué hago si pierdo líquido por la vagina?",
        "respuesta": "Si pierdes un chorro súbito de líquido transparente o sientes humedad constante, puede ser ruptura de membranas (bolsa de aguas). Acude inmediatamente a urgencias sin importar la semana de gestación.",
        "palabras_clave": "líquido, bolsa de aguas, ruptura membranas, pierde líquido",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué es la preeclampsia?",
        "respuesta": "La preeclampsia es una complicación grave caracterizada por presión alta (≥140/90) y daño orgánico (riñones, hígado, cerebro) después de la semana 20. Sus síntomas incluyen hinchazón, dolor de cabeza, visión borrosa y proteinuria. Requiere atención médica urgente.",
        "palabras_clave": "preeclampsia, presión alta embarazo, complicación",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué es la diabetes gestacional?",
        "respuesta": "Es un tipo de diabetes que aparece durante el embarazo debido a cambios hormonales. Se detecta entre las semanas 24-28 con el test de O'Sullivan. Con control médico y dieta adecuada se puede manejar bien, pero requiere seguimiento.",
        "palabras_clave": "diabetes gestacional, glucosa, azúcar, O'Sullivan",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué es una amenaza de aborto?",
        "respuesta": "Es sangrado vaginal con o sin dolor en las primeras 20 semanas que puede indicar riesgo de pérdida del embarazo. Requiere reposo y evaluación médica urgente. No todas las amenazas de aborto terminan en pérdida si se tratan a tiempo.",
        "palabras_clave": "amenaza aborto, sangrado, primer trimestre, riesgo",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué es un parto prematuro?",
        "respuesta": "El parto prematuro ocurre antes de la semana 37. Sus señales son: contracciones regulares dolorosas, presión pélvica intensa, pérdida de líquido o sangrado antes de las 37 semanas. Es una emergencia obstétrica.",
        "palabras_clave": "parto prematuro, antes de tiempo, contracciones, prematuridad",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Cuándo debo llamar a emergencias?",
        "respuesta": "Llama al +593 98 123 4567 o acude a urgencias si tienes: sangrado abundante, pérdida de líquido, contracciones antes de semana 37, ausencia de movimientos fetales, dolor intenso, presión mayor a 140/90, visión borrosa o fiebre mayor a 38°C.",
        "palabras_clave": "emergencias, llamar, urgencias, cuándo ir",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Cuándo debo ir al hospital?",
        "respuesta": "Ve al hospital cuando tengas contracciones regulares (cada 5 min por 1 hora en semana 37+), pérdida de líquido, sangrado, o cualquier signo de alarma. No esperes si tienes dudas — es mejor consultar y estar segura.",
        "palabras_clave": "ir hospital, maternidad, parto, contracciones regulares",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué signos indican riesgo alto?",
        "respuesta": "Signos de riesgo alto: presión ≥140/90, proteinuria (proteína en orina), hinchazón repentina en cara/manos, visión borrosa, dolor abdominal en barra (debajo del pecho), fiebre, sangrado o ausencia de movimientos fetales.",
        "palabras_clave": "riesgo alto, riesgo, signos riesgo, alarma",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué hacer ante contracciones?",
        "respuesta": "Toma el tiempo entre contracciones (del inicio de una al inicio de la siguiente). Si son regulares (cada 5 min, duran 1 min, por 1 hora) después de la semana 37, ve al hospital. Antes de la semana 37, acude de inmediato.",
        "palabras_clave": "contracciones, trabajo de parto, tiempo contracciones",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué hacer ante vómitos persistentes?",
        "respuesta": "Los vómitos leves en el primer trimestre son normales. Si son tan intensos que no puedes comer ni hidratarte (hiperemesis gravídica), consulta al médico. Puede que necesites hidratación intravenosa y medicación.",
        "palabras_clave": "vómitos, náuseas intensas, hiperemesis, no puede comer",
    },
    {
        "categoria": "sintomas_alarmas",
        "pregunta": "¿Qué hacer si tengo dificultad para respirar?",
        "respuesta": "Algo de dificultad al final del embarazo es normal por el peso del útero. Sin embargo, si tienes dificultad súbita, dolor en el pecho, ritmo cardíaco acelerado o te falta el aire en reposo, acude a urgencias inmediatamente.",
        "palabras_clave": "respirar, falta aire, dificultad respirar, asfixia",
    },
]


# ---------------------------------------------------------------------------
# CATEGORÍA 5: Nutrición y Estilo de Vida (15 preguntas)
# ---------------------------------------------------------------------------
_NUTRICION = [
    {
        "categoria": "nutricion",
        "pregunta": "¿Qué alimentos debo consumir en el embarazo?",
        "respuesta": "Prioriza: frutas y verduras frescas, proteínas magras (pollo, pescado, legumbres), lácteos pasteurizados, cereales integrales y grasas saludables (aguacate, nueces). Una dieta variada y equilibrada es la base de un embarazo sano.",
        "palabras_clave": "alimentos, comer, dieta, nutrición, qué comer",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Qué alimentos debo evitar?",
        "respuesta": "Evita: carnes crudas o poco cocidas, pescados con alto mercurio (atún rojo, pez espada), huevos crudos, quesos blandos no pasteurizados (brie, camembert), alcohol, bebidas energizantes y embutidos de origen incierto.",
        "palabras_clave": "evitar, prohibido, no comer, alimentos riesgo",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Cuánta agua debo tomar al día?",
        "respuesta": "Se recomienda beber entre 8 y 10 vasos de agua al día (2 a 2.5 litros). La hidratación es fundamental para la formación del líquido amniótico, la circulación y prevenir infecciones urinarias.",
        "palabras_clave": "agua, hidratación, cuánta agua, litros",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Puedo hacer ejercicio durante el embarazo?",
        "respuesta": "Sí, el ejercicio moderado es beneficioso. Se recomiendan caminatas de 30 min diarias, yoga prenatal y natación. Evita deportes de contacto, actividades con riesgo de caída y ejercicio intenso de alta intensidad. Consulta a tu médico antes de iniciar cualquier rutina.",
        "palabras_clave": "ejercicio, deporte, actividad física, yoga, caminar",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Puedo viajar durante el embarazo?",
        "respuesta": "El segundo trimestre es el más seguro para viajar. Evita viajes en el tercer trimestre, especialmente después de la semana 36. En avión, levántate cada 2 horas. Siempre consulta con tu médico antes de cualquier viaje largo.",
        "palabras_clave": "viajar, viaje, avión, carro, transporte",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Puedo tomar café?",
        "respuesta": "Puedes consumir hasta 200 mg de cafeína al día (equivale a 1-2 tazas de café pequeño). El exceso de cafeína se asocia a bajo peso al nacer. Recuerda que el té, el chocolate y las bebidas cola también contienen cafeína.",
        "palabras_clave": "café, cafeína, té, bebidas",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Puedo comer pescado?",
        "respuesta": "Sí, pero elige bien. Son seguros: salmón, sardinas, trucha, tilapia (2-3 porciones/semana). Evita: atún rojo, pez espada, tiburón y caballa (alto mercurio). El pescado bien cocido y seguro es excelente por su omega-3.",
        "palabras_clave": "pescado, mariscos, atún, salmón, mercurio",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Debo tomar ácido fólico?",
        "respuesta": "Sí, es fundamental. El ácido fólico previene defectos del tubo neural (espina bífida). Se recomienda desde 3 meses antes del embarazo y durante todo el primer trimestre. La dosis estándar es 400-800 mcg/día.",
        "palabras_clave": "ácido fólico, folato, vitamina B9, tubo neural",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Debo tomar suplementos de hierro?",
        "respuesta": "El hierro previene la anemia gestacional. Tu médico lo recetará generalmente desde la semana 16. Tómalo con jugo de naranja (vitamina C mejora la absorción) y sepáralo del calcio y leche.",
        "palabras_clave": "hierro, anemia, suplemento, ferritina",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Cuánto peso debo subir durante el embarazo?",
        "respuesta": "El aumento recomendado depende de tu IMC previo: Bajo peso: 12.5-18 kg | Normal: 11.5-16 kg | Sobrepeso: 7-11.5 kg | Obesidad: 5-9 kg. Tu médico y nutricionista harán el seguimiento personalizado.",
        "palabras_clave": "peso, cuánto subir, kilos, IMC, ganancia peso",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Puedo dormir boca arriba?",
        "respuesta": "A partir del segundo trimestre se recomienda dormir de lado (preferiblemente izquierdo) para evitar comprimir la vena cava y garantizar buena circulación al bebé. Usa almohadas entre las piernas y debajo del abdomen para mayor comodidad.",
        "palabras_clave": "dormir, posición dormir, boca arriba, lado, almohada",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Puedo tener relaciones sexuales?",
        "respuesta": "En un embarazo sin complicaciones, las relaciones sexuales son seguras durante todo el embarazo. Se recomienda evitarlas si hay amenaza de aborto, placenta previa, ruptura de membranas o indicación médica específica.",
        "palabras_clave": "relaciones sexuales, intimidad, sexo, pareja",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Cómo controlar el estrés durante el embarazo?",
        "respuesta": "Recomendaciones: yoga o meditación prenatal, caminatas diarias, hablar con tu pareja o familia, grupos de apoyo para embarazadas, técnicas de respiración y descanso adecuado. El estrés crónico puede afectar el desarrollo del bebé.",
        "palabras_clave": "estrés, ansiedad, calmar, tranquilidad, meditación",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Cómo mejorar el descanso y el sueño?",
        "respuesta": "Consejos: duerme de lado izquierdo con almohada entre piernas, reduce líquidos por las noches para evitar levantarte seguido, evita pantallas antes de dormir, crea una rutina de relajación y considera almohadas de embarazo.",
        "palabras_clave": "dormir, descanso, insomnio, sueño, cansancio",
    },
    {
        "categoria": "nutricion",
        "pregunta": "¿Qué hábitos debo evitar durante el embarazo?",
        "respuesta": "Evita absolutamente: alcohol (no hay cantidad segura), tabaco y cigarrillo, drogas, automedicación, contacto con químicos tóxicos, cambiar arena de gato (toxoplasmosis) y exponerte a radiaciones innecesarias.",
        "palabras_clave": "hábitos, evitar, alcohol, tabaco, fumar, drogas",
    },
]


# ---------------------------------------------------------------------------
# CATEGORÍA 6: Uso del Sistema (10 preguntas)
# ---------------------------------------------------------------------------
_USO_SISTEMA = [
    {
        "categoria": "uso_sistema",
        "pregunta": "¿Cómo crear una cuenta en Zumedical?",
        "respuesta": "Para crear tu cuenta: 1) Ve a la página principal de Zumedical. 2) Haz clic en 'Registrarse'. 3) Completa tus datos personales (nombre, cédula, correo, teléfono). 4) Crea una contraseña segura. 5) Confirma tu cuenta por correo electrónico.",
        "palabras_clave": "crear cuenta, registrarse, registro, nueva cuenta",
    },
    {
        "categoria": "uso_sistema",
        "pregunta": "¿Cómo iniciar sesión?",
        "respuesta": "Para iniciar sesión: 1) Ve a zumedical.ec. 2) Haz clic en 'Iniciar Sesión' (esquina superior derecha). 3) Ingresa tu correo y contraseña. 4) Haz clic en 'Entrar'. Si olvidaste tu contraseña, usa la opción 'Olvidé mi contraseña'.",
        "palabras_clave": "iniciar sesión, login, entrar, acceder, ingresar",
    },
    {
        "categoria": "uso_sistema",
        "pregunta": "¿Cómo recuperar mi contraseña?",
        "respuesta": "Para recuperar tu contraseña: 1) En la pantalla de login, haz clic en '¿Olvidaste tu contraseña?'. 2) Ingresa tu correo registrado. 3) Recibirás un enlace de recuperación en tu correo. 4) Sigue las instrucciones para crear una nueva contraseña.",
        "palabras_clave": "contraseña, olvidé, recuperar, cambiar contraseña, password",
    },
    {
        "categoria": "uso_sistema",
        "pregunta": "¿Cómo editar o actualizar mis datos?",
        "respuesta": "Para actualizar tus datos: 1) Inicia sesión. 2) Ve a tu perfil (ícono de usuario arriba a la derecha). 3) Selecciona 'Editar Perfil'. 4) Modifica los campos que necesites. 5) Guarda los cambios.",
        "palabras_clave": "editar perfil, actualizar datos, cambiar información, perfil",
    },
    {
        "categoria": "uso_sistema",
        "pregunta": "¿Cómo ver mis citas en el sistema?",
        "respuesta": "Para ver tus citas: Inicia sesión → Panel de Paciente → 'Mis Citas'. Verás todas tus citas con fecha, hora, médico y estado (confirmada, pendiente, completada o cancelada).",
        "palabras_clave": "ver citas, mis citas, historial citas, citas programadas",
    },
    {
        "categoria": "uso_sistema",
        "pregunta": "¿Cómo ver mis controles y resultados prenatales?",
        "respuesta": "Para ver tus controles: Inicia sesión → 'Controles Prenatales' en el menú lateral. Podrás ver el historial de tus controles, resultados de laboratorio y las observaciones de cada consulta.",
        "palabras_clave": "ver resultados, controles, historial médico, laboratorio",
    },
    {
        "categoria": "uso_sistema",
        "pregunta": "¿Cómo descargar mis resultados?",
        "respuesta": "En la sección 'Controles Prenatales' o 'Resultados de Laboratorio', selecciona el examen o control que deseas y haz clic en el ícono de descarga (PDF). Los resultados se guardan en tu dispositivo.",
        "palabras_clave": "descargar, PDF, resultados, imprimir",
    },
    {
        "categoria": "uso_sistema",
        "pregunta": "¿Cómo cerrar sesión de forma segura?",
        "respuesta": "Para cerrar sesión: Haz clic en tu nombre o ícono de usuario en la parte superior → Selecciona 'Cerrar Sesión'. Siempre cierra sesión cuando uses un dispositivo compartido o público.",
        "palabras_clave": "cerrar sesión, logout, salir, seguridad",
    },
    {
        "categoria": "uso_sistema",
        "pregunta": "¿Qué hago si el sistema presenta un error?",
        "respuesta": "Si el sistema falla: 1) Refresca la página. 2) Limpia el caché del navegador. 3) Intenta con otro navegador. 4) Si persiste, comunícate al soporte técnico: +593 98 123 4567 o escribe a soporte@zumedical.ec.",
        "palabras_clave": "error, sistema, falla, problema técnico, no carga",
    },
    {
        "categoria": "uso_sistema",
        "pregunta": "¿Cómo contactar al soporte técnico?",
        "respuesta": "Puedes contactar al soporte técnico de Zumedical por: Teléfono/WhatsApp: +593 98 123 4567 | Correo: soporte@zumedical.ec | Horario de soporte: Lunes a Viernes de 08:00 a 17:00.",
        "palabras_clave": "soporte, ayuda técnica, contacto, soporte técnico",
    },
]


# ---------------------------------------------------------------------------
# CATEGORÍA 7: Posparto y Lactancia (15 preguntas)
# ---------------------------------------------------------------------------
_POSPARTO_LACTANCIA = [
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Qué es el puerperio?",
        "respuesta": "El puerperio es el período que comienza después del parto y dura aproximadamente 6 semanas. En esta etapa, el cuerpo de la madre regresa gradualmente a su estado previo al embarazo. Requiere cuidados especiales y controles médicos.",
        "palabras_clave": "puerperio, después del parto, postparto, recuperación",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Cómo cuidar la herida de la cesárea?",
        "respuesta": "Cuidados de la herida: mantén la zona limpia y seca, lava suavemente con agua y jabón, seca con gasa limpia, no expongas al sol durante 6 meses, usa ropa holgada, evita esfuerzos físicos las primeras 6 semanas y acude al médico si ves enrojecimiento, secreción o fiebre.",
        "palabras_clave": "cesárea, cicatriz, herida, cuidados operación",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Cómo cuidar la episiotomía?",
        "respuesta": "Para la episiotomía (corte perineal): lava la zona con agua tibia después de cada visita al baño, sécala bien, usa compresas de hielo las primeras 24 horas, evita estar sentada por mucho tiempo y toma los analgésicos indicados por tu médico.",
        "palabras_clave": "episiotomía, periné, puntos, sutura, parto vaginal",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Cuándo debo iniciar la lactancia?",
        "respuesta": "Lo ideal es iniciar la lactancia en la primera hora después del parto (el calostro es fundamental). El contacto piel a piel inmediato favorece la producción de leche y el vínculo madre-bebé. Tu enfermera te guiará en la posición correcta.",
        "palabras_clave": "lactancia, amamantar, calostro, primera hora, pecho",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Cada cuánto debo alimentar al bebé?",
        "respuesta": "Los recién nacidos deben alimentarse cada 2-3 horas (8-12 veces al día). A demanda libre en los primeros meses. La leche materna se digiere rápido. Si el bebé llora entre tomas, puede que tenga hambre o necesite consuelo.",
        "palabras_clave": "cada cuánto, horario lactancia, tomas, frecuencia, alimentar",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Qué hacer si el bebé no se prende al pecho?",
        "respuesta": "Si el bebé tiene dificultad para prenderse: asegura una postura correcta (cuerpo frente a cuerpo), ofrece el pezón tocando su labio superior, busca que la boca abarque gran parte de la areola. Si persiste, solicita apoyo a una consultora de lactancia.",
        "palabras_clave": "no se prende, prendida, agarre, dificultad lactancia",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Cómo extraer leche materna?",
        "respuesta": "Puedes extraer leche manualmente o con sacaleches eléctrico/manual. Lo ideal: extrae 15-20 min por pecho, en un ambiente tranquilo, con el bebé o su foto cerca para estimular la bajada de leche. Lava bien el equipo antes y después.",
        "palabras_clave": "extraer leche, sacaleches, extracción, bomba leche",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Cómo conservar la leche materna?",
        "respuesta": "La leche materna se conserva: Temperatura ambiente: 4-6 horas | Refrigerador (4°C): hasta 72 horas | Congelador: hasta 3 meses. Usa recipientes limpios y etiqueta con fecha y hora. Descongela en refrigerador o agua tibia, nunca en microondas.",
        "palabras_clave": "conservar leche, guardar leche, refrigerar, congelar, almacenar",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Qué alimentos favorecen la producción de leche?",
        "respuesta": "Alimentos galactogénicos: avena, hinojo, galega, cebada, alfalfa, nueces, almendras, papaya verde y una adecuada hidratación (mínimo 2 litros de agua/día). La clave principal es amamantar con frecuencia: a más succión, más producción.",
        "palabras_clave": "producción leche, alimentos lactancia, galactagogos, aumentar leche",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Qué medicamentos debo evitar durante la lactancia?",
        "respuesta": "Evita: aspirina, ibuprofeno en dosis altas, antibióticos sin indicación médica, antihistamínicos sedantes y algunos anticonceptivos hormonales. Siempre consulta a tu médico antes de tomar cualquier medicamento durante la lactancia.",
        "palabras_clave": "medicamentos lactancia, evitar, contraindicado, pastillas",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Cuándo debo acudir al control posparto?",
        "respuesta": "El control posparto se realiza a los 7-10 días del parto para revisar la herida (cesárea o episiotomía), signos vitales, estado emocional y inicio de la lactancia. El segundo control se programa a las 6 semanas.",
        "palabras_clave": "control posparto, cuándo ir, revisión, semanas posparto",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Qué síntomas posparto requieren atención urgente?",
        "respuesta": "Busca atención urgente si tienes: fiebre mayor a 38°C, sangrado muy abundante (más de una toalla/hora), dolor pélvico intenso, signos de infección en la herida, dificultad para respirar, o síntomas de depresión posparto severa.",
        "palabras_clave": "síntomas posparto, signos alarma posparto, urgencia, fiebre posparto",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Cómo prevenir la mastitis?",
        "respuesta": "Para prevenir mastitis (infección del pecho): amamanta frecuentemente vaciando bien el pecho, asegura una postura correcta, evita ropa interior muy ajustada, cuida la higiene del pezón y trata a tiempo cualquier grieta o inflamación.",
        "palabras_clave": "mastitis, infección pecho, seno inflamado, prevenir mastitis",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Cuándo puedo retomar la actividad física?",
        "respuesta": "Después de un parto vaginal sin complicaciones puedes iniciar caminatas suaves a los 7-10 días. Tras cesárea, espera al menos 6 semanas. Consulta con tu médico antes de retomar ejercicio intenso o de alto impacto.",
        "palabras_clave": "ejercicio posparto, retomar deporte, actividad física, cesárea ejercicio",
    },
    {
        "categoria": "posparto_lactancia",
        "pregunta": "¿Cuándo puedo planificar un nuevo embarazo?",
        "respuesta": "Se recomienda esperar al menos 18-24 meses entre partos para permitir la recuperación completa del cuerpo. En caso de cesárea, mínimo 24 meses. Consulta a tu médico sobre métodos anticonceptivos seguros durante la lactancia.",
        "palabras_clave": "nuevo embarazo, planificar, anticonceptivos, esperar",
    },
]



# ---------------------------------------------------------------------------
# Lista unificada (usada por populate_faqs y el backend)
# ---------------------------------------------------------------------------
FAQ_CHATBOT = (
    _CENTRO_MEDICO
    + _CITAS_MEDICAS
    + _CONTROLES_PRENATALES
    + _SINTOMAS_ALARMAS
    + _NUTRICION
    + _USO_SISTEMA
    + _POSPARTO_LACTANCIA
)

# Alias de compatibilidad con código existente que aún importe PRENATAL_FAQS
PRENATAL_FAQS = FAQ_CHATBOT


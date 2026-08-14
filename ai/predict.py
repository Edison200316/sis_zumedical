"""
predict.py — Zumedical Prenatal AI v2
=======================================
Motor de predicción de riesgo prenatal.
El modelo se carga UNA SOLA VEZ al importar (singleton).

IMPORTANTE — Unidades de entrada:
    glucose: debe estar en mmol/L
             Convertir: mg/dL ÷ 18.0 = mmol/L

Uso desde Django:
    from ai.predict import engine
    resultado = engine.predict(datos_clinicos)
"""

import pickle
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

MODEL_DIR     = Path(__file__).resolve().parent / "model"
MODEL_PATH    = MODEL_DIR / "modelo_riesgo.pkl"
SCALER_PATH   = MODEL_DIR / "scaler.pkl"
FEATURES_PATH = MODEL_DIR / "feature_names.pkl"

LABEL_DECODE = {0: "Bajo", 1: "Medio", 2: "Alto"}
LABEL_COLORS = {"Bajo": "success", "Medio": "warning", "Alto": "danger"}
LABEL_ICONS  = {"Bajo": "🟢", "Medio": "🟡", "Alto": "🔴"}


# ─────────────────────────────────────────────────────────────────────────────
# Banco clínico de complicaciones por factor de riesgo
# ─────────────────────────────────────────────────────────────────────────────
COMPLICACIONES_POR_FACTOR = {
    "hipertension_critica": [
        "Eclampsia (convulsiones hipertensivas)",
        "Síndrome HELLP (hemólisis + daño hepático y plaquetas)",
        "Accidente cerebrovascular materno",
        "Restricción severa del crecimiento fetal",
        "Desprendimiento de placenta",
        "Preeclampsia severa",
    ],
    "hipertension": [
        "Preeclampsia",
        "Restricción del crecimiento intrauterino (RCIU)",
        "Parto prematuro iatrogénico",
        "Oligohidramnios",
    ],
    "diabetes_critica": [
        "Cetoacidosis diabética",
        "Macrosomía fetal (bebé > 4 kg)",
        "Hipoglucemia neonatal grave",
        "Polihidramnios",
        "Distocia de hombros en el parto",
    ],
    "diabetes": [
        "Diabetes Gestacional confirmada",
        "Macrosomía fetal",
        "Hipoglucemia neonatal",
        "Parto prematuro por descompensación metabólica",
    ],
    "obesidad": [
        "Parto por cesárea (riesgo incrementado)",
        "Trombosis venosa profunda",
        "Apnea del sueño gestacional",
    ],
    "edad_muy_avanzada": [
        "Alteraciones cromosómicas (Síndrome de Down, Trisomías)",
        "Placenta previa",
        "Muerte fetal intrauterina (riesgo incrementado)",
    ],
    "edad_avanzada": [
        "Alteraciones cromosómicas (riesgo incrementado)",
        "Hipertensión gestacional",
    ],
    "complicaciones_previas": [
        "Recurrencia de complicaciones obstétricas",
        "Restricción del crecimiento fetal",
    ],
    "general_alto": [
        "Parto prematuro",
        "Restricción del crecimiento fetal",
        "Oligohidramnios",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# Recomendaciones base por nivel (agrupadas por categoría)
# ─────────────────────────────────────────────────────────────────────────────
RECOMENDACIONES_BASE: Dict[str, Dict[str, List[str]]] = {
    "Alto": {
        "urgencia": [
            "🚨 Acude a consulta con tu obstetra de forma INMEDIATA (dentro de las próximas 24 horas).",
            "📅 Programa control prenatal SEMANAL hasta nueva indicación médica.",
            "💉 Solicita perfil completo de preeclampsia: proteinuria, función renal y hepática.",
            "🩺 Monitorea tu presión arterial dos veces al día y registra los valores.",
        ],
        "nutricion": [],
        "habitos": [
            "🛌 Guarda reposo relativo; evita esfuerzo físico y situaciones de estrés.",
            "🚫 No modifiques ni suspendas medicamentos sin indicación médica.",
        ],
    },
    "Medio": {
        "urgencia": [
            "📅 Consulta a tu médico en los próximos 3 días.",
            "📏 Realiza control prenatal cada 15 días.",
        ],
        "nutricion": [],
        "habitos": [
            "📊 Lleva un registro diario de tu presión arterial y peso.",
            "🚶 Evita actividad física intensa; puedes hacer caminatas suaves.",
            "💧 Mantén una hidratación adecuada (mínimo 2 litros de agua al día).",
            "😴 Duerme entre 7 y 8 horas; el descanso es fundamental para el bebé.",
        ],
    },
    "Bajo": {
        "urgencia": [
            "✅ Continúa tus controles prenatales según el calendario establecido.",
            "💊 Toma tus vitaminas prenatales (ácido fólico, hierro, calcio) sin interrupción.",
        ],
        "nutricion": [
            "🥗 Mantén una alimentación variada y equilibrada: frutas, verduras, proteínas y cereales integrales.",
        ],
        "habitos": [
            "🤸 Realiza actividad física moderada autorizada (caminatas, yoga prenatal).",
            "😴 Descansa adecuadamente; el sueño es esencial para el desarrollo fetal.",
        ],
    },
}

# Recomendaciones adicionales por factor detectado
RECOMENDACIONES_FACTOR: Dict[str, Dict[str, List[str]]] = {
    "hipertension": {
        "urgencia": [],
        "nutricion": [
            "🧂 Reduce el consumo de sal (máximo 5 g/día) y evita embutidos y procesados.",
        ],
        "habitos": [
            "📝 Lleva un registro de presión arterial y muéstralo a tu médico en cada consulta.",
            "🚰 Mantente hidratada pero evita sobrecarga de líquidos sin indicación médica.",
        ],
    },
    "diabetes": {
        "urgencia": [],
        "nutricion": [
            "🍬 Controla el consumo de azúcares simples, harinas refinadas y bebidas azucaradas.",
            "🍎 Prefiere frutas con bajo índice glucémico (manzana, pera, naranja, frutos rojos).",
            "🥗 Distribuye las comidas en 5-6 porciones pequeñas al día para estabilizar la glucosa.",
        ],
        "habitos": [
            "🧪 Solicita la prueba de tolerancia a la glucosa si aún no la has realizado.",
        ],
    },
    "obesidad": {
        "urgencia": [],
        "nutricion": [
            "⚖️ Sigue la guía de ganancia de peso recomendada por tu obstetra para tu IMC.",
            "🥤 Elimina bebidas azucaradas, jugos industriales y alimentos fritos.",
        ],
        "habitos": [
            "🚶 Realiza 20-30 minutos de caminata diaria si tu médico lo autoriza.",
        ],
    },
    "edad_avanzada": {
        "urgencia": [
            "🧬 Consulta sobre estudios genéticos prenatales no invasivos (ADN fetal en sangre materna).",
            "📅 Mantén controles más frecuentes dado el perfil de edad materna avanzada.",
        ],
        "nutricion": [],
        "habitos": [],
    },
    "complicaciones_previas": {
        "urgencia": [
            "📋 Comparte todo tu historial clínico completo con tu obstetra actual.",
            "⚠️ Informa de inmediato ante cualquier síntoma inusual, por leve que parezca.",
        ],
        "nutricion": [],
        "habitos": [],
    },
}


@dataclass
class ResultadoPrediccion:
    """Resultado completo de la predicción de riesgo prenatal."""
    nivel_riesgo:           str
    probabilidades:         Dict[str, float]
    probabilidad_nivel:     float
    puntuacion:             int
    color:                  str
    icono:                  str
    factores_detectados:    List[str]
    complicaciones:         List[str]
    recomendaciones:        List[str]                 # lista plana (compatibilidad)
    recomendaciones_grupos: Dict[str, List[str]]      # agrupadas por categoría
    explicacion:            str
    datos_clinicos:         Dict
    alerta_critica:         Optional[str] = None
    nota_antecedente:       Optional[str] = None
    ajuste_seguridad:       Optional[str] = None


class PrenatalMLEngine:
    """
    Motor de predicción ML para riesgo prenatal.
    Carga el modelo entrenado una única vez (singleton).
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._model    = None
        self._scaler   = None
        self._features = None
        self._loaded   = False
        self._load_model()
        self._initialized = True

    def _load_model(self):
        if MODEL_PATH.exists() and SCALER_PATH.exists() and FEATURES_PATH.exists():
            try:
                with open(MODEL_PATH, "rb") as f:
                    self._model = pickle.load(f)
                with open(SCALER_PATH, "rb") as f:
                    self._scaler = pickle.load(f)
                with open(FEATURES_PATH, "rb") as f:
                    self._features = pickle.load(f)
                self._loaded = True
                print("[Zumedical AI] Modelo de riesgo prenatal cargado correctamente.")
            except Exception as e:
                print(f"[Zumedical AI] Error al cargar modelo: {e}")
                self._loaded = False
        else:
            print("[Zumedical AI] Modelo no encontrado. Ejecuta ai/training/train_model.py")
            self._loaded = False

    @property
    def modelo_disponible(self) -> bool:
        return self._loaded

    def _build_feature_vector(self, datos: dict):
        from ai.training.feature_engineering import prepare_single_record
        row = prepare_single_record(datos)
        return row[self._features]

    def _detectar_factores(self, datos: dict) -> Dict[str, List[str]]:
        """
        Detecta factores clínicos con umbrales validados.
        Solo marca edad avanzada si realmente aplica (≥35 años).
        """
        factores = {}
        edad       = datos.get("age", 25)
        sistolica  = datos.get("systolic_bp", 110)
        diastolica = datos.get("diastolic_bp", 70)
        glucosa    = datos.get("glucose", 6.5)    # mmol/L
        bmi        = datos.get("bmi", 23.0)
        prev_comp  = datos.get("prev_complications", 0)
        diab_pre   = datos.get("diabetes_preexisting", 0)
        diab_gest  = datos.get("diabetes_gestacional", 0)

        # ── Presión arterial ──────────────────────────────────────────────
        if sistolica >= 160 or diastolica >= 110:
            factores["hipertension_critica"] = [
                f"⚠️ Presión arterial CRÍTICA ({sistolica}/{diastolica} mmHg) — "
                f"hipertensión severa, riesgo inmediato de eclampsia"
            ]
        elif sistolica >= 140 or diastolica >= 90:
            factores["hipertension"] = [
                f"Presión arterial elevada ({sistolica}/{diastolica} mmHg) — "
                f"hipertensión gestacional (umbral ≥140/90)"
            ]
        elif sistolica >= 130 or diastolica >= 85:
            factores["hipertension"] = [
                f"Presión arterial en límite alto ({sistolica}/{diastolica} mmHg) — "
                f"vigilancia recomendada"
            ]

        # ── Glucosa (mmol/L) ──────────────────────────────────────────────
        glucosa_mgdl = round(glucosa * 18, 1)
        if glucosa > 11.1:
            factores["diabetes_critica"] = [
                f"Glucosa muy elevada ({glucosa:.2f} mmol/L = {glucosa_mgdl} mg/dL) — "
                f"criterio diagnóstico de diabetes (>200 mg/dL)"
            ]
        elif glucosa > 7.8:
            factores["diabetes"] = [
                f"Glucosa elevada ({glucosa:.2f} mmol/L = {glucosa_mgdl} mg/dL) — "
                f"hiperglucemia (>140 mg/dL)"
            ]
        elif glucosa > 5.6 and (diab_pre or diab_gest):
            factores["diabetes"] = [
                f"Glucosa normal ({glucosa_mgdl} mg/dL) con antecedente diabético registrado — "
                f"factor considerado por diagnóstico previo en historia clínica"
            ]
        elif diab_pre:
            factores["diabetes"] = [
                "Diabetes preexistente registrada en historia clínica — "
                "riesgo de descontrol glucémico en el embarazo"
            ]
        elif diab_gest:
            factores["diabetes"] = [
                "Diabetes gestacional diagnosticada — "
                "requiere manejo nutricional y posiblemente insulina"
            ]

        # ── IMC / Obesidad ────────────────────────────────────────────────
        if bmi >= 35:
            factores["obesidad"] = [
                f"Obesidad grado II-III (IMC: {bmi:.1f}) — riesgo elevado de complicaciones materno-fetales"
            ]
        elif bmi >= 30:
            factores["obesidad"] = [
                f"Obesidad grado I (IMC: {bmi:.1f}) — factor de riesgo independiente"
            ]
        elif bmi >= 25:
            factores["obesidad"] = [
                f"Sobrepeso (IMC: {bmi:.1f}) — vigilancia de ganancia de peso recomendada"
            ]

        # ── Edad materna ──────────────────────────────────────────────────
        if edad >= 40:
            factores["edad_muy_avanzada"] = [
                f"Edad materna muy avanzada ({edad} años) — riesgo incrementado de aneuploidías"
            ]
        elif edad >= 35:
            factores["edad_avanzada"] = [
                f"Edad materna avanzada ({edad} años) — umbral de mayor vigilancia (≥35 años)"
            ]

        # ── Complicaciones previas ────────────────────────────────────────
        if prev_comp:
            factores["complicaciones_previas"] = [
                "Antecedentes de complicaciones obstétricas — riesgo de recurrencia"
            ]

        return factores

    def _normalizar_probabilidades(self, probs: Dict[str, float]) -> Dict[str, float]:
        total = sum(float(probs.get(k, 0.0)) for k in LABEL_COLORS) or 1.0
        normalizadas = {
            k: round((float(probs.get(k, 0.0)) / total) * 100.0, 1)
            for k in LABEL_COLORS
        }
        diferencia = round(100.0 - sum(normalizadas.values()), 1)
        if diferencia:
            mayor = max(normalizadas, key=normalizadas.get)
            normalizadas[mayor] = round(normalizadas[mayor] + diferencia, 1)
        return normalizadas

    def _aplicar_piso_clinico(
        self,
        datos_clinicos: dict,
        nivel: str,
        probs: Dict[str, float],
    ):
        """Aplica reglas conservadoras para que factores clinicos confirmados no queden como bajo riesgo."""
        orden = {"Bajo": 0, "Medio": 1, "Alto": 2}
        sistolica = datos_clinicos.get("systolic_bp", 0)
        diastolica = datos_clinicos.get("diastolic_bp", 0)
        glucosa = datos_clinicos.get("glucose", 0)
        bmi = datos_clinicos.get("bmi", 0)
        edad = datos_clinicos.get("age", 0)
        prev_comp = int(datos_clinicos.get("prev_complications", 0))
        diab_pre = int(datos_clinicos.get("diabetes_preexisting", 0))
        diab_gest = int(datos_clinicos.get("diabetes_gestacional", 0))

        objetivo = nivel
        minimo = 0.0
        razones = []

        if sistolica >= 160 or diastolica >= 110:
            objetivo = "Alto"
            minimo = max(minimo, 90.0)
            razones.append("presion arterial severa")
        if glucosa > 11.1:
            objetivo = "Alto"
            minimo = max(minimo, 90.0)
            razones.append("glucosa en rango critico")

        requiere_medio = []
        if sistolica >= 140 or diastolica >= 90:
            requiere_medio.append("presion arterial elevada")
        if glucosa > 7.8:
            requiere_medio.append("hiperglucemia")
        if diab_pre:
            requiere_medio.append("diabetes preexistente registrada")
        if diab_gest:
            requiere_medio.append("diabetes gestacional registrada")
        if prev_comp:
            requiere_medio.append("complicaciones obstetricas previas")
        if bmi >= 35:
            requiere_medio.append("obesidad grado II-III")
        if edad >= 40:
            requiere_medio.append("edad materna muy avanzada")

        if requiere_medio and orden[objetivo] < orden["Medio"]:
            objetivo = "Medio"
            minimo = max(minimo, 65.0)
            razones.extend(requiere_medio)

        if orden[objetivo] <= orden[nivel]:
            return nivel, probs, float(probs.get(nivel, 0.0)), None

        ajustadas = dict(probs)
        if objetivo == "Medio":
            ajustadas["Medio"] = max(float(ajustadas.get("Medio", 0.0)), minimo or 65.0)
            ajustadas["Bajo"] = min(float(ajustadas.get("Bajo", 0.0)), 30.0)
            ajustadas["Alto"] = max(float(ajustadas.get("Alto", 0.0)), 5.0)
        else:
            ajustadas["Alto"] = max(float(ajustadas.get("Alto", 0.0)), minimo or 90.0)
            ajustadas["Medio"] = min(max(float(ajustadas.get("Medio", 0.0)), 5.0), 5.0)
            ajustadas["Bajo"] = min(float(ajustadas.get("Bajo", 0.0)), 5.0)

        ajustadas = self._normalizar_probabilidades(ajustadas)
        nota = (
            "Ajuste clinico de seguridad: el modelo sugirio riesgo "
            f"{nivel}, pero se elevo a {objetivo} por "
            f"{'; '.join(dict.fromkeys(razones))}."
        )
        return objetivo, ajustadas, float(ajustadas[objetivo]), nota

    def _resultado_clinico(
        self,
        datos_clinicos: dict,
        nivel: str,
        probs: Dict[str, float],
        prob_nivel: float,
        ajuste_seguridad: Optional[str] = None,
    ) -> ResultadoPrediccion:
        """Construye la respuesta completa a partir de un nivel ya calculado."""
        factores_dict = self._detectar_factores(datos_clinicos)
        factores_texto = [t for textos in factores_dict.values() for t in textos]

        alerta_critica = None
        sistolica = datos_clinicos.get("systolic_bp", 0)
        diastolica = datos_clinicos.get("diastolic_bp", 0)
        if sistolica >= 160 or diastolica >= 110:
            alerta_critica = (
                f"🚨 ALERTA — Paciente con posible crisis hipertensiva "
                f"({sistolica}/{diastolica} mmHg). "
                f"Se recomienda valoración médica INMEDIATA y descartar eclampsia."
            )

        nota_antecedente = None
        diab_pre = datos_clinicos.get("diabetes_preexisting", 0)
        diab_gest = datos_clinicos.get("diabetes_gestacional", 0)
        glucosa = datos_clinicos.get("glucose", 0)
        if (diab_pre or diab_gest) and glucosa < 7.8:
            tipo = "preexistente" if diab_pre else "gestacional"
            nota_antecedente = (
                f"ℹ️ La diabetes {tipo} fue considerada porque está registrada en la historia clínica "
                f"del paciente, no porque los niveles de glucosa actuales sean diagnósticos. "
                f"La IA no realiza diagnósticos — incorpora datos ya confirmados por el médico."
            )

        complicaciones = []
        seen_comp = set()
        for key in factores_dict:
            for comp in COMPLICACIONES_POR_FACTOR.get(key, []):
                base = comp.split("(")[0].strip().lower()
                if base not in seen_comp:
                    seen_comp.add(base)
                    complicaciones.append(comp)
        if nivel == "Alto" and not complicaciones:
            for comp in COMPLICACIONES_POR_FACTOR["general_alto"]:
                base = comp.split("(")[0].strip().lower()
                if base not in seen_comp:
                    complicaciones.append(comp)

        factor_rec_map = {
            "hipertension_critica": "hipertension",
            "hipertension": "hipertension",
            "diabetes_critica": "diabetes",
            "diabetes": "diabetes",
            "obesidad": "obesidad",
            "edad_muy_avanzada": "edad_avanzada",
            "edad_avanzada": "edad_avanzada",
            "complicaciones_previas": "complicaciones_previas",
        }

        base_grupos = RECOMENDACIONES_BASE.get(nivel, {"urgencia": [], "nutricion": [], "habitos": []})
        grupos: Dict[str, List[str]] = {
            "urgencia": list(base_grupos.get("urgencia", [])),
            "nutricion": list(base_grupos.get("nutricion", [])),
            "habitos": list(base_grupos.get("habitos", [])),
        }
        added_recs = set()
        for key in factores_dict:
            rec_key = factor_rec_map.get(key)
            if rec_key and rec_key not in added_recs:
                factor_grupos = RECOMENDACIONES_FACTOR.get(rec_key, {})
                for cat in ("urgencia", "nutricion", "habitos"):
                    for rec in factor_grupos.get(cat, []):
                        if rec not in grupos[cat]:
                            grupos[cat].append(rec)
                added_recs.add(rec_key)

        disclaimer = (
            "⚕️ Este resultado es una herramienta de apoyo basada en inteligencia artificial "
            "y no reemplaza la valoración clínica de tu médico tratante."
        )
        recomendaciones_plana = grupos["urgencia"] + grupos["nutricion"] + grupos["habitos"] + [disclaimer]
        grupos["disclaimer"] = [disclaimer]

        factores_cortos = [
            t.split(" — ")[0].strip().lstrip("⚠️ ").strip()
            for textos in factores_dict.values()
            for t in textos
        ]
        if factores_cortos:
            causas_str = "; ".join(factores_cortos[:3])
            explicacion = (
                f"La clasificación '{nivel}' fue determinada principalmente por: {causas_str}. "
                f"Probabilidad estimada para esta clase: {prob_nivel:.1f}%."
            )
            if not self._loaded:
                explicacion += " Se usó el respaldo clínico por reglas porque el modelo ML no está disponible."
        else:
            explicacion = (
                f"Los parámetros clínicos analizados corresponden a un perfil de riesgo '{nivel}'. "
                f"No se detectaron factores de riesgo individuales destacados. "
                f"Probabilidad estimada: {prob_nivel:.1f}%."
            )
            if not self._loaded:
                explicacion += " Se usó el respaldo clínico por reglas porque el modelo ML no está disponible."
        if ajuste_seguridad:
            explicacion += " " + ajuste_seguridad

        return ResultadoPrediccion(
            nivel_riesgo=nivel,
            probabilidades=probs,
            probabilidad_nivel=prob_nivel,
            puntuacion=int(prob_nivel),
            color=LABEL_COLORS[nivel],
            icono=LABEL_ICONS[nivel],
            factores_detectados=factores_texto,
            complicaciones=complicaciones,
            recomendaciones=recomendaciones_plana,
            recomendaciones_grupos=grupos,
            explicacion=explicacion,
            datos_clinicos=datos_clinicos,
            alerta_critica=alerta_critica,
            nota_antecedente=nota_antecedente,
            ajuste_seguridad=ajuste_seguridad,
        )

    def _predict_rule_based(self, datos_clinicos: dict) -> ResultadoPrediccion:
        """Respaldo determinístico si el modelo entrenado no está disponible."""
        sistolica = datos_clinicos.get("systolic_bp", 110)
        diastolica = datos_clinicos.get("diastolic_bp", 70)
        glucosa = datos_clinicos.get("glucose", 5.0)
        bmi = datos_clinicos.get("bmi", 23.0)
        edad = datos_clinicos.get("age", 25)
        prev_comp = int(datos_clinicos.get("prev_complications", 0))
        diab_pre = int(datos_clinicos.get("diabetes_preexisting", 0))
        diab_gest = int(datos_clinicos.get("diabetes_gestacional", 0))

        puntos = 0
        if sistolica >= 160 or diastolica >= 110:
            puntos += 5
        elif sistolica >= 140 or diastolica >= 90:
            puntos += 3
        elif sistolica >= 130 or diastolica >= 85:
            puntos += 1
        if glucosa > 11.1:
            puntos += 4
        elif glucosa > 7.8:
            puntos += 3
        elif glucosa > 5.6 and (diab_pre or diab_gest):
            puntos += 2
        if bmi >= 35:
            puntos += 3
        elif bmi >= 30:
            puntos += 2
        elif bmi >= 25:
            puntos += 1
        if edad >= 40:
            puntos += 2
        elif edad >= 35:
            puntos += 1
        puntos += 2 if prev_comp else 0
        puntos += 2 if diab_pre else 0
        puntos += 2 if diab_gest else 0

        if puntos >= 6:
            nivel = "Alto"
            prob_nivel = min(95, 68 + puntos * 4)
            probs = {"Bajo": 5.0, "Medio": max(0.0, 95.0 - prob_nivel), "Alto": float(prob_nivel)}
        elif puntos >= 3:
            nivel = "Medio"
            prob_nivel = min(85, 55 + puntos * 5)
            probs = {"Bajo": max(5.0, 100.0 - prob_nivel - 15.0), "Medio": float(prob_nivel), "Alto": 15.0}
        else:
            nivel = "Bajo"
            prob_nivel = max(60, 82 - puntos * 7)
            probs = {"Bajo": float(prob_nivel), "Medio": max(5.0, 100.0 - prob_nivel - 5.0), "Alto": 5.0}

        nivel, probs, prob_nivel, ajuste = self._aplicar_piso_clinico(datos_clinicos, nivel, probs)
        return self._resultado_clinico(datos_clinicos, nivel, probs, float(prob_nivel), ajuste)

    def predict(self, datos_clinicos: dict) -> ResultadoPrediccion:
        """
        Realiza la predicción de riesgo prenatal.

        IMPORTANTE: glucose debe estar en mmol/L.
        Conversión: glucose_mgdl / 18.0 = mmol/L
        """
        if not self._loaded:
            return self._predict_rule_based(datos_clinicos)

        # ── Construir vector y predecir ────────────────────────────────────
        try:
            X_df = self._build_feature_vector(datos_clinicos)
            X_sc = self._scaler.transform(X_df)

            clase_pred         = int(self._model.predict(X_sc)[0])
            probabilidades_arr = self._model.predict_proba(X_sc)[0]
        except Exception as exc:
            print(f"[Zumedical AI] Error al predecir con ML. Usando respaldo clinico: {exc}")
            return self._predict_rule_based(datos_clinicos)

        probs = {
            LABEL_DECODE[i]: round(float(p) * 100, 1)
            for i, p in enumerate(probabilidades_arr)
        }
        nivel      = LABEL_DECODE[clase_pred]
        nivel, probs, prob_nivel, ajuste = self._aplicar_piso_clinico(datos_clinicos, nivel, probs)
        puntuacion = int(prob_nivel)

        resultado = self._resultado_clinico(datos_clinicos, nivel, probs, prob_nivel, ajuste)
        if resultado.factores_detectados:
            resultado.explicacion += (
                f" El modelo analizó {len(self._features)} variables clínicas "
                f"(clase {nivel} según Random Forest)."
            )
        return resultado


# Instancia global — se carga al importar el módulo
engine = PrenatalMLEngine()

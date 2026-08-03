"""
models.py — prediccion_ia
============================
Modelo que almacena cada predicción de riesgo prenatal generada por la IA.
Incluye todos los campos clínicos de entrada y los resultados completos.
"""

import json
from django.db import models
from pacientes.models import Paciente


class PrediccionIA(models.Model):

    NIVEL_CHOICES = [
        ("Bajo",  "🟢 Bajo"),
        ("Medio", "🟡 Medio"),
        ("Alto",  "🔴 Alto"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="predicciones",
        verbose_name="Paciente",
    )
    control = models.ForeignKey(
        "control_prenatal.ControlPrenatal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="predicciones_ia",
        verbose_name="Control prenatal asociado",
    )

    # ── Datos clínicos de entrada ──────────────────────────────────────────
    edad                  = models.IntegerField(verbose_name="Edad (años)")
    semanas_gestacion     = models.IntegerField(verbose_name="Semanas de gestación", default=0)
    presion_arterial      = models.CharField(max_length=20, verbose_name="Presión arterial")
    presion_sistolica     = models.IntegerField(default=0, verbose_name="Presión sistólica")
    presion_diastolica    = models.IntegerField(default=0, verbose_name="Presión diastólica")
    peso                  = models.FloatField(verbose_name="Peso (kg)")
    altura                = models.FloatField(default=1.60, verbose_name="Altura (m)")
    imc                   = models.FloatField(default=0.0, verbose_name="IMC")
    glucosa               = models.FloatField(verbose_name="Glucosa (mg/dL)")
    frecuencia_cardiaca   = models.IntegerField(default=75, verbose_name="Frecuencia cardíaca")
    temperatura           = models.FloatField(default=98.0, verbose_name="Temperatura (°F)")
    embarazos_previos     = models.IntegerField(default=0, verbose_name="Embarazos previos")
    complicaciones_previas= models.BooleanField(default=False, verbose_name="Complicaciones previas")
    diabetes_preexistente = models.BooleanField(default=False, verbose_name="Diabetes preexistente")
    diabetes_gestacional  = models.BooleanField(default=False, verbose_name="Diabetes gestacional")

    # ── Resultados de la IA ────────────────────────────────────────────────
    nivel_riesgo      = models.CharField(
        max_length=10,
        choices=NIVEL_CHOICES,
        verbose_name="Nivel de riesgo",
    )
    puntuacion_riesgo = models.IntegerField(
        default=0,
        verbose_name="Probabilidad (%)",
    )
    resultado         = models.TextField(
        verbose_name="Resultado completo (JSON)",
    )

    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de evaluación")

    class Meta:
        verbose_name        = "Predicción IA"
        verbose_name_plural = "Predicciones IA"
        ordering            = ["-fecha"]

    def __str__(self):
        return (
            f"{self.paciente} — {self.nivel_riesgo} "
            f"({self.puntuacion_riesgo}%) — {self.fecha.strftime('%d/%m/%Y')}"
        )

    @property
    def datos_resultado(self) -> dict:
        """Devuelve el JSON del resultado como diccionario Python."""
        try:
            return json.loads(self.resultado)
        except (json.JSONDecodeError, TypeError):
            return {
                "factores":         [],
                "complicaciones":   [],
                "recomendaciones":  [],
                "probabilidades":   {},
                "explicacion":      "",
            }

    @property
    def color_bootstrap(self) -> str:
        """Color Bootstrap para badges y alertas."""
        return {"Bajo": "success", "Medio": "warning", "Alto": "danger"}.get(
            self.nivel_riesgo, "secondary"
        )

    @property
    def icono(self) -> str:
        return {"Bajo": "🟢", "Medio": "🟡", "Alto": "🔴"}.get(self.nivel_riesgo, "⚪")

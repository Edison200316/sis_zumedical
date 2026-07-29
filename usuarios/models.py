from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
import secrets
from django.utils import timezone
from datetime import timedelta

class Usuario(AbstractUser):

    ROLES = (
        ('admin', 'Administrador'),
        ('medico', 'Medico'),
        ('enfermera', 'Enfermera'),
        ('secretaria', 'Secretaria'),
        ('paciente', 'Paciente'),
    )

    GENERO_CHOICES = (
        ('femenino', 'Femenino'),
        ('masculino', 'Masculino'),
        ('otro', 'Otro / Prefiero no indicar'),
    )

    rol = models.CharField(max_length=20, choices=ROLES)

    genero = models.CharField(
        max_length=20,
        choices=GENERO_CHOICES,
        null=True,
        blank=True,
        help_text="Género de la paciente — solo pacientes femeninas pueden activar módulo prenatal"
    )

    def __str__(self):
        return self.username

    @property
    def puede_prenatal(self):
        """
        True si esta cuenta tiene acceso al módulo prenatal.
        """
        if self.rol != 'paciente':
            return False
        try:
            return self.paciente.estado_embarazo == 'ACTIVO'
        except Exception:
            return False

    @property
    def tiene_solo_general(self):
        """True si solo tiene acceso general (sin módulo prenatal activo)."""
        return self.rol == 'paciente' and not self.puede_prenatal


class CodigoRecuperacionPassword(models.Model):
    """Modelo para almacenar códigos de recuperación de contraseña"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='codigo_recuperacion')
    codigo = models.CharField(max_length=6, unique=True)  # Código de 6 dígitos
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    intentos_fallidos = models.IntegerField(default=0)
    max_intentos = 5
    validado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Código de Recuperación"
        verbose_name_plural = "Códigos de Recuperación"

    def __str__(self):
        return f"Código para {self.usuario.username}"

    @staticmethod
    def generar_codigo():
        """Genera un código único de 6 dígitos"""
        while True:
            codigo = str(int(secrets.token_hex(3), 16))[:6].zfill(6)
            if not CodigoRecuperacionPassword.objects.filter(codigo=codigo).exists():
                return codigo

    def es_valido(self):
        """Verifica si el código aún es válido"""
        ahora = timezone.now()
        return (
            ahora < self.expira_en and 
            self.intentos_fallidos < self.max_intentos
        )

    def es_expirado(self):
        """Verifica si el código ha expirado"""
        return timezone.now() > self.expira_en

    @classmethod
    def crear_para_usuario(cls, usuario):
        """Crea o actualiza el código de recuperación para un usuario"""
        ahora = timezone.now()
        codigo = cls.generar_codigo()
        expira_en = ahora + timedelta(minutes=15)  # Válido por 15 minutos
        
        codigo_obj, created = cls.objects.update_or_create(
            usuario=usuario,
            defaults={
                'codigo': codigo,
                'creado_en': ahora,
                'expira_en': expira_en,
                'intentos_fallidos': 0,
                'validado': False,
            }
        )
        return codigo_obj


@receiver(post_save, sender=Usuario)
def crear_perfil_paciente(sender, instance, created, **kwargs):
    if created and instance.rol == 'paciente':
        from pacientes.models import Paciente
        Paciente.objects.get_or_create(usuario=instance)


class LogAuditoria(models.Model):
    ACCIONES = [
        ('LOGIN',        'Inicio de sesión'),
        ('LOGOUT',       'Cierre de sesión'),
        ('CREATE',       'Creación'),
        ('UPDATE',       'Actualización'),
        ('DELETE',       'Eliminación'),
        ('CANCELACION',  'Cancelación'),
        ('VIEW',         'Visualización'),
        ('ERROR',        'Error'),
    ]
    SEVERIDADES = [
        ('INFO',     'Información'),
        ('WARNING',  'Advertencia'),
        ('CRITICAL', 'Crítico'),
    ]

    usuario     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs_auditoria')
    accion      = models.CharField(max_length=20, choices=ACCIONES)
    modulo      = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField(blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    severidad   = models.CharField(max_length=10, choices=SEVERIDADES, default='INFO')
    fecha       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        indexes = [
            models.Index(fields=['-fecha']),
            models.Index(fields=['usuario', '-fecha']),
            models.Index(fields=['accion', '-fecha']),
        ]

    def __str__(self):
        return f"[{self.severidad}] {self.accion} — {self.usuario} — {self.fecha:%d/%m/%Y %H:%M}"
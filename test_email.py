#!/usr/bin/env python
"""
Script para probar la configuración de correo SMTP en Django.

Uso:
    python manage.py shell < test_email.py
    
O directamente:
    python test_email.py
"""

from django.core.mail import send_mail
from django.conf import settings

def test_smtp_connection():
    """Prueba la conexión SMTP enviando un correo de prueba."""
    
    print("=" * 60)
    print("PRUEBA DE CONFIGURACIÓN SMTP - ZUMedical")
    print("=" * 60)
    
    # Mostrar configuración actual
    print(f"\n📧 EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"🌐 EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"🔌 EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"🔐 EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"👤 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"📧 DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Validar que la configuración esté completa
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("\n❌ ERROR: EMAIL_HOST_USER o EMAIL_HOST_PASSWORD no están configurados.")
        print("   Por favor, verifica tu archivo .env")
        return False
    
    print("\n" + "-" * 60)
    print("Intentando enviar correo de prueba...")
    print("-" * 60)
    
    try:
        # Enviar correo de prueba
        subject = "🧪 Correo de Prueba - ZUMedical SMTP"
        message = """
¡Hola!

Este es un correo de prueba para verificar que la configuración SMTP 
de tu proyecto Django ZUMedical funciona correctamente.

Si recibes este correo, significa que:
✅ La conexión SMTP es exitosa
✅ Las credenciales son correctas
✅ El servidor de correo responde correctamente

Próximos pasos:
- Ya puedes usar Django para enviar correos en tu aplicación
- La recuperación de contraseña funcionará automáticamente
- Los correos de notificación se enviarán exitosamente

¡Felicidades! Tu sistema de correo está listo para producción.

---
ZUMedical - Sistema Prenatal
        """
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.EMAIL_HOST_USER]  # Enviar a la misma cuenta para prueba
        
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        print(f"\n✅ ÉXITO: Correo enviado correctamente.")
        print(f"   Para: {recipient_list[0]}")
        print(f"   Asunto: {subject}")
        print(f"\n💡 Verifica tu bandeja de entrada (y spam) para confirmar.")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR al enviar el correo:")
        print(f"   {type(e).__name__}: {str(e)}")
        print(f"\n🔧 Posibles soluciones:")
        print(f"   1. Verifica que EMAIL_HOST_USER y EMAIL_HOST_PASSWORD sean correctos")
        print(f"   2. Para Gmail, debes usar una contraseña de aplicación, no tu contraseña regular")
        print(f"   3. Verifica que la cuenta de Gmail tenga habilitada la autenticación de dos factores")
        print(f"   4. Comprueba que tienes conexión a internet")
        return False

if __name__ == "__main__":
    import os
    import django
    
    # Configurar Django si se ejecuta directamente
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_prenatal.settings')
    django.setup()
    
    success = test_smtp_connection()
    exit(0 if success else 1)

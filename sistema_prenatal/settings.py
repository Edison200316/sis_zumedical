"""
Django settings for sistema_prenatal project.
"""

import os
from pathlib import Path

import dj_database_url
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SEGURIDAD
# ============================================================

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Vercel inyecta el host público en estas variables durante despliegues.
VERCEL_URL = os.environ.get('VERCEL_URL', '')
VERCEL_BRANCH_URL = os.environ.get('VERCEL_BRANCH_URL', '')
for vercel_domain in [VERCEL_URL, VERCEL_BRANCH_URL]:
    vercel_domain = vercel_domain.replace('https://', '').replace('http://', '').split('/')[0]
    if vercel_domain and vercel_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(vercel_domain)
if not DEBUG and '.vercel.app' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('.vercel.app')

# Railway inyecta la URL pública del servicio en esta variable
RAILWAY_PUBLIC_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
if RAILWAY_PUBLIC_DOMAIN and RAILWAY_PUBLIC_DOMAIN not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)

# También agregar el dominio completo si viene en RAILWAY_STATIC_URL
RAILWAY_STATIC_URL = os.environ.get('RAILWAY_STATIC_URL', '')
if RAILWAY_STATIC_URL:
    # Extraer dominio limpio sin https://
    domain_clean = RAILWAY_STATIC_URL.replace('https://', '').replace('http://', '').split('/')[0]
    if domain_clean and domain_clean not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(domain_clean)

# Asegurar que el dominio específico de producción esté incluido
if 'zumedicalsis-production.up.railway.app' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('zumedicalsis-production.up.railway.app')

# CSRF — dominios de confianza para requests POST en producción
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost,http://127.0.0.1',
    cast=Csv()
)

# Agregar automáticamente el dominio de Railway
if RAILWAY_PUBLIC_DOMAIN:
    railway_origin = f'https://{RAILWAY_PUBLIC_DOMAIN}'
    if railway_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(railway_origin)

# Agregar también dominios alternativos de Railway
RAILWAY_STATIC_URL = os.environ.get('RAILWAY_STATIC_URL', '')
if RAILWAY_STATIC_URL:
    if RAILWAY_STATIC_URL.startswith('https://'):
        if RAILWAY_STATIC_URL not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(RAILWAY_STATIC_URL)
    else:
        full_url = f'https://{RAILWAY_STATIC_URL}'
        if full_url not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(full_url)

for vercel_domain in [VERCEL_URL, VERCEL_BRANCH_URL]:
    vercel_domain = vercel_domain.replace('https://', '').replace('http://', '').split('/')[0]
    if vercel_domain:
        vercel_origin = f'https://{vercel_domain}'
        if vercel_origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(vercel_origin)
if 'https://*.vercel.app' not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append('https://*.vercel.app')


# ============================================================
# APLICACIONES
# ============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'usuarios',
    'pacientes',
    'medicos',
    'citas',
    'control_prenatal',
    'prediccion_ia',
    'chatbot',
    'landing',
    'paciente_general',
]

AUTH_USER_MODEL = 'usuarios.Usuario'


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    'sistema_prenatal.middleware.HealthCheckMiddleware',  # responde /health/ sin tocar BD
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoiseMiddleware desactivado en Vercel: usa su propio sistema de static files
    # 'whitenoise.middleware.WhiteNoiseMiddleware',  # sirve estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'usuarios.middleware.AuditoriaMiddleware',  # Auditoría automática en tiempo real
]

ROOT_URLCONF = 'sistema_prenatal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'usuarios.context_processors.medico_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'sistema_prenatal.wsgi.application'

LOGIN_URL = '/login/'


# ============================================================
# BASE DE DATOS — PostgreSQL (Neon) via .env
# ============================================================

DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True,
    )
}


# ============================================================
# VALIDACIÓN DE CONTRASEÑAS
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================================
# INTERNACIONALIZACIÓN
# ============================================================

LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True


# ============================================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ============================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    path for path in [
        BASE_DIR / 'static',
        BASE_DIR / 'sistema_prenatal' / 'static',
    ]
    if path.exists()
]
# StaticFilesStorage básico: entrega CSS sin transformaciones en Vercel
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# WHITENOISE: Desactivar compresión de CSS en Vercel
WHITENOISE_SKIP_COMPRESS_OFFLINE = True
WHITENOISE_MIMETYPES = {
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ============================================================
# CORREO ELECTRÓNICO (SMTP - Gmail)
# ============================================================

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@zumedical.com')


# ============================================================
# OTROS
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

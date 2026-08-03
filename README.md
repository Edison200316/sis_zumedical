# Zumedical

Sistema médico Django preparado para despliegue en Vercel.

## Despliegue en Vercel

Configura estas variables de entorno en Vercel:

- `SECRET_KEY`
- `DEBUG=False`
- `DATABASE_URL`
- `ALLOWED_HOSTS=.vercel.app,localhost,127.0.0.1`
- `CSRF_TRUSTED_ORIGINS=https://*.vercel.app`
- Variables SMTP si se usará recuperación de contraseña.

Vercel ejecuta:

```bash
python manage.py collectstatic --noinput --clear
```

El entrypoint serverless está en `api/index.py`.

def validar_cedula_ecuatoriana(cedula):
    """Valida una cedula ecuatoriana de persona natural."""
    cedula = (cedula or '').strip()

    if len(cedula) != 10 or not cedula.isdigit():
        return False
    if cedula == cedula[0] * 10:
        return False

    codigo_provincia = int(cedula[:2])
    codigo_valido = 1 <= codigo_provincia <= 24
    if not codigo_valido:
        return False

    if int(cedula[2]) >= 6:
        return False

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    for digito, coeficiente in zip(cedula[:9], coeficientes):
        resultado = int(digito) * coeficiente
        if resultado >= 10:
            resultado -= 9
        suma += resultado

    residuo = suma % 10
    verificador = 0 if residuo == 0 else 10 - residuo
    return verificador == int(cedula[9])


MENSAJE_CEDULA_INVALIDA = (
    'Ingresa una cedula ecuatoriana real de 10 digitos.'
)


DOMINIOS_EMAIL_PERMITIDOS = {
    'gmail.com', 'googlemail.com', 'outlook.com', 'hotmail.com', 'live.com',
    'msn.com', 'yahoo.com', 'yahoo.es', 'icloud.com', 'me.com', 'mac.com',
    'proton.me', 'protonmail.com', 'aol.com', 'zoho.com', 'gmx.com',
    'gmx.net', 'mail.com', 'yandex.com', 'yandex.ru', 'fastmail.com',
    'tutanota.com', 'tuta.com', 'hey.com', 'inbox.com',
}

MENSAJE_EMAIL_INVALIDO = (
    'Ingresa un correo real con un dominio permitido.'
)


def validar_email_permitido(email):
    email = (email or '').strip()
    if not email:
        return True

    if email.count('@') != 1:
        return False

    local, dominio = email.rsplit('@', 1)
    dominio = dominio.lower()
    if not local or not dominio or '..' in email:
        return False

    return dominio in DOMINIOS_EMAIL_PERMITIDOS

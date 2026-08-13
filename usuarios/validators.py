def validar_cedula_ecuatoriana(cedula):
    """Valida una cedula ecuatoriana de persona natural."""
    cedula = (cedula or '').strip()

    if len(cedula) != 10 or not cedula.isdigit():
        return False

    provincia = int(cedula[:2])
    if provincia < 1 or provincia > 24:
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

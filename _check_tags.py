with open('templates/medico/historial.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

problemas = []
for i, line in enumerate(lines, 1):
    open_var = line.count('{{')
    close_var = line.count('}}')
    open_tag = line.count('{%')
    close_tag = line.count('%}')
    if (open_var > close_var) or (open_tag > close_tag):
        problemas.append((i, 'ABIERTO', line.rstrip()))
    elif (close_var > open_var) or (close_tag > open_tag):
        problemas.append((i, 'CERRADO', line.rstrip()))
        
if problemas:
    print('WARNING: Posibles tags en multiples lineas:')
    for num, tipo, txt in problemas:
        print('  Linea', num, tipo, txt[:100])
else:
    print('OK: No se encontraron tags aparentemente partidos')

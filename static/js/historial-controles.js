/**
 * Historial de Controles Prenatales
 * Manejo de eventos para editar/eliminar controles con AJAX
 */

console.log('🟢 historial-controles.js cargando...');

let currentControlId = null;
let currentControlData = null;

console.log('🟢 Variables globales inicializadas');

// ══════════════════════════════════════════════════════════════════════════════
// FUNCIONES PARA ABRIR/CERRAR MODALS
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Abre el modal de edición y carga los datos del control
 */
function abrirEditarControl(controlId) {
    console.log('🔵 abrirEditarControl llamada con ID:', controlId);
    currentControlId = controlId;
    
    // Fetch datos del control desde la API
    fetch(`/control-prenatal/api/control/${controlId}/editar/`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            preFillEditForm(data.data);
            abrirModalEditar();
        } else {
            mostrarToast('Error al cargar datos del control', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarToast('Error al conectar con el servidor', 'error');
    });
}

/**
 * Pre-llena el formulario con datos del control
 */
function preFillEditForm(data) {
    document.getElementById('me-control-id').value = data.id;
    document.getElementById('me-fecha').value = data.fecha;
    document.getElementById('me-semanas').value = data.semanas_gestacion;
    document.getElementById('me-presion').value = data.presion_arterial;
    document.getElementById('me-peso').value = data.peso;
    document.getElementById('me-altura').value = data.altura || '';
    document.getElementById('me-glucosa').value = data.glucosa || '';
    document.getElementById('me-fc').value = data.frecuencia_cardiaca || '';
    document.getElementById('me-temp').value = data.temperatura || '';
    document.getElementById('me-proteinuria').value = data.proteinuria || 'Negativa';
    document.getElementById('me-obs').value = data.observaciones || '';
    
    // Obtener nombre del paciente desde el botón clickeado
    const btns = document.querySelectorAll(`[data-control-id="${currentControlId}"]`);
    let card = null, row = null;
    btns.forEach(b => {
        if (b.closest('.cc-card')) card = b.closest('.cc-card');
        if (b.closest('tr')) row = b.closest('tr');
    });

    if (card) {
        const nombreEl = card.querySelector('.cc-name');
        const inicialesEl = card.querySelector('.cc-av');
        if (nombreEl) document.getElementById('me-nombre').textContent = nombreEl.textContent;
        if (inicialesEl) document.getElementById('me-av').textContent = inicialesEl.textContent;
    } else if (row) {
        const pacienteCell = row.querySelector('.pac-name');
        const inicialesCell = row.querySelector('.pac-av');
        if (pacienteCell) document.getElementById('me-nombre').textContent = pacienteCell.textContent;
        if (inicialesCell) document.getElementById('me-av').textContent = inicialesCell.textContent;
    }
    
    // Limpiar errores previos
    document.getElementById('me-errors').style.display = 'none';
    document.getElementById('me-errors-list').innerHTML = '';
}

/**
 * Abre el modal de edición
 */
function abrirModalEditar() {
    const overlay = document.getElementById('modal-editar-overlay');
    if (overlay) {
        overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
}

/**
 * Cierra el modal de edición
 */
function cerrarEditarModal(event) {
    // Si se clickea en el overlay, solo cerrar si es el fondo
    if (event && event.target.id !== 'modal-editar-overlay') {
        return;
    }
    
    const overlay = document.getElementById('modal-editar-overlay');
    if (overlay) {
        overlay.classList.remove('open');
        document.body.style.overflow = '';
    }
    currentControlId = null;
}

/**
 * Abre el modal de confirmación de eliminación
 */
function abrirConfirmarEliminar(controlId) {
    console.log('🔵 abrirConfirmarEliminar llamada con ID:', controlId);
    currentControlId = controlId;
    const btns = document.querySelectorAll(`[data-control-id="${currentControlId}"]`);
    let card = null, row = null;
    btns.forEach(b => {
        if (b.closest('.cc-card')) card = b.closest('.cc-card');
        if (b.closest('tr')) row = b.closest('tr');
    });

    if (row) {
        const celdaPaciente = row.querySelector('.pac-name');
        const celdaFecha = row.querySelector('td:nth-child(2)');
        const celdaSemanas = row.querySelector('td:nth-child(3)');
        const celdaPresion = row.querySelector('td:nth-child(4)');
        
        if (celdaPaciente && celdaFecha && celdaSemanas && celdaPresion) {
            document.getElementById('me-del-nombre').textContent = celdaPaciente.textContent.trim();
            document.getElementById('me-del-fecha').textContent = celdaFecha.textContent.trim();
            document.getElementById('me-del-semanas').textContent = celdaSemanas.textContent.trim();
            document.getElementById('me-del-presion').textContent = celdaPresion.textContent.trim();
        }
    } else if (card) {
        const nombreEl = card.querySelector('.cc-name');
        const dateEl = card.querySelector('.cc-date');
        const semanasEl = card.querySelector('.cc-badge');
        const presionEl = card.querySelector('[class*="presion"]');
        
        if (nombreEl) document.getElementById('me-del-nombre').textContent = nombreEl.textContent;
        if (dateEl) document.getElementById('me-del-fecha').textContent = dateEl.textContent;
        if (semanasEl) document.getElementById('me-del-semanas').textContent = semanasEl.textContent;
        if (presionEl) document.getElementById('me-del-presion').textContent = presionEl.textContent;
    }
    
    abrirModalEliminar();
}

/**
 * Abre el modal de eliminación
 */
function abrirModalEliminar() {
    const overlay = document.getElementById('modal-eliminar-overlay');
    if (overlay) {
        overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
}

/**
 * Cierra el modal de eliminación
 */
function cerrarEliminarModal(event) {
    // Si se clickea en el overlay, solo cerrar si es el fondo
    if (event && event.target.id !== 'modal-eliminar-overlay') {
        return;
    }
    
    const overlay = document.getElementById('modal-eliminar-overlay');
    if (overlay) {
        overlay.classList.remove('open');
        document.body.style.overflow = '';
    }
    currentControlId = null;
}

// ══════════════════════════════════════════════════════════════════════════════
// FUNCIONES PARA GUARDAR Y ELIMINAR
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Guarda los cambios del control
 */
function guardarControl(event) {
    event.preventDefault();
    
    if (!currentControlId) {
        mostrarToast('Error: ID del control no disponible', 'error');
        return;
    }
    
    // Obtener datos del formulario
    const form = document.getElementById('form-editar-control');
    const formData = new FormData(form);
    const data = {
        fecha: formData.get('fecha'),
        semanas_gestacion: parseInt(formData.get('semanas_gestacion')),
        presion_arterial: formData.get('presion_arterial'),
        peso: parseFloat(formData.get('peso')),
        altura: parseFloat(formData.get('altura')) || null,
        glucosa: parseFloat(formData.get('glucosa')) || null,
        frecuencia_cardiaca: parseInt(formData.get('frecuencia_cardiaca')) || null,
        temperatura: parseFloat(formData.get('temperatura')) || null,
        proteinuria: formData.get('proteinuria'),
        observaciones: formData.get('observaciones')
    };
    
    // Validaciones básicas en cliente
    if (!validarDatos(data)) {
        return;
    }
    
    // Mostrar estado de carga
    const btnGuardar = form.querySelector('button[type="submit"]');
    const textOriginal = btnGuardar.textContent;
    btnGuardar.disabled = true;
    btnGuardar.textContent = 'Guardando...';
    
    // POST a la API
    fetch(`/control-prenatal/api/control/${currentControlId}/editar/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        btnGuardar.disabled = false;
        btnGuardar.textContent = textOriginal;
        
        if (result.success) {
            mostrarToast('✓ Control actualizado correctamente', 'success');
            cerrarEditarModal();
            
            // Recargar la tabla sin recargar la página
            setTimeout(() => {
                location.reload();
            }, 500);
        } else {
            if (result.errors) {
                mostrarErrores(result.errors);
            } else {
                mostrarToast(result.error || 'Error al guardar', 'error');
            }
        }
    })
    .catch(error => {
        btnGuardar.disabled = false;
        btnGuardar.textContent = textOriginal;
        console.error('Error:', error);
        mostrarToast('Error al conectar con el servidor', 'error');
    });
}

/**
 * Confirma y ejecuta la eliminación del control
 */
function confirmarEliminar() {
    if (!currentControlId) {
        mostrarToast('Error: ID del control no disponible', 'error');
        return;
    }
    
    // POST a la API para eliminar
    fetch(`/control-prenatal/api/control/${currentControlId}/eliminar/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            mostrarToast('✓ Control eliminado correctamente', 'success');
            cerrarEliminarModal();
            
            // Eliminar la fila/card de la tabla
            const row = document.querySelector(`[data-control-id="${currentControlId}"]`).closest('tr') || 
                       document.querySelector(`[data-control-id="${currentControlId}"]`).closest('.control-card');
            if (row) {
                row.style.animation = 'fadeOut 0.3s ease forwards';
                setTimeout(() => {
                    row.remove();
                    location.reload();
                }, 300);
            }
        } else {
            mostrarToast(result.error || 'Error al eliminar', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarToast('Error al conectar con el servidor', 'error');
    });
}

// ══════════════════════════════════════════════════════════════════════════════
// FUNCIONES AUXILIARES
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Obtiene el token CSRF del documento
 */
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Valida los datos del formulario
 */
function validarDatos(data) {
    const errores = [];
    
    // Validar fecha (no puede ser futura)
    const fecha = new Date(data.fecha);
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    if (fecha > hoy) {
        errores.push('La fecha del control no puede ser futura');
    }
    
    // Validar presión arterial formato
    const presionRegex = /^\d+\/\d+$/;
    if (!presionRegex.test(data.presion_arterial)) {
        errores.push('Presión arterial debe estar en formato: 120/80');
    }
    
    // Validar peso
    if (data.peso <= 0 || isNaN(data.peso)) {
        errores.push('El peso debe ser un número positivo');
    }
    
    // Validar semanas
    if (data.semanas_gestacion < 1 || data.semanas_gestacion > 42) {
        errores.push('Las semanas de gestación deben estar entre 1 y 42');
    }
    
    if (errores.length > 0) {
        mostrarErrores(errores);
        return false;
    }
    
    return true;
}

/**
 * Muestra errores de validación en el formulario
 */
function mostrarErrores(errores) {
    const erroresDiv = document.getElementById('me-errors');
    const erroresList = document.getElementById('me-errors-list');
    
    erroresList.innerHTML = '';
    
    // Si errores es un objeto (de Django), convertir a array
    if (typeof errores === 'object' && !Array.isArray(errores)) {
        Object.keys(errores).forEach(campo => {
            const mensajes = errores[campo];
            if (Array.isArray(mensajes)) {
                mensajes.forEach(msg => {
                    const li = document.createElement('li');
                    li.textContent = `${campo}: ${msg}`;
                    erroresList.appendChild(li);
                });
            }
        });
    } else if (Array.isArray(errores)) {
        errores.forEach(msg => {
            const li = document.createElement('li');
            li.textContent = msg;
            erroresList.appendChild(li);
        });
    }
    
    erroresDiv.style.display = 'block';
    erroresDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ══════════════════════════════════════════════════════════════════════════════
// EVENT LISTENERS
// ══════════════════════════════════════════════════════════════════════════════

// Cerrar modals al presionar Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const editModal = document.getElementById('modal-editar-overlay');
        const deleteModal = document.getElementById('modal-eliminar-overlay');
        
        if (editModal && editModal.classList.contains('open')) {
            cerrarEditarModal();
        }
        if (deleteModal && deleteModal.classList.contains('open')) {
            cerrarEliminarModal();
        }
    }
});

// Agregar animación CSS para fadeOut
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(-10px); }
    }
    
    .btn-action:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .btn-action:active {
        transform: translateY(0);
    }
`;
document.head.appendChild(style);

console.log('✓ Historial controles JS cargado');

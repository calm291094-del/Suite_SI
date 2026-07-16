/**
 * ════════════════════════════════════════════════════════════
 * JS DEL INVENTARIO DE EQUIPOS
 * Funcionalidades:
 * - Agregar componentes vía AJAX POST
 * - Editar componentes vía modal + AJAX POST
 * - Eliminar componentes vía AJAX POST
 * - Detección de cambios y alertas automáticas
 * ════════════════════════════════════════════════════════════
 */

// ═══ Agregar un nuevo componente a un equipo ═══
function agregarComponente(event, equipoId) {
    event.preventDefault();

    // Recoger datos del formulario
    const form = event.target;
    const formData = new FormData(form);
    // Remover el csrf token del FormData porque getCSRF() lo añade en el header
    formData.delete('csrfmiddlewaretoken');

    // Convertir FormData a objeto plano
    const data = Object.fromEntries(formData.entries());

    fetch(`/api/componente/agregar/${equipoId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRF(),
        },
        body: JSON.stringify(data),
    })
    .then(r => r.json())
    .then(response => {
        if (response.ok) {
            // Crear el nuevo elemento en la lista del DOM
            agregarComponenteAlDOM(response);

            // Limpiar formulario
            form.reset();

            showNotification('Componente agregado correctamente', 'success');
        } else {
            // Mostrar errores de validación
            if (typeof response.error === 'object') {
                const errores = Object.values(response.error).join('. ');
                showNotification(errores, 'error');
            } else {
                showNotification(response.error || 'Error al agregar componente', 'error');
            }
        }
    })
    .catch(() => {
        showNotification('Error de conexión con el servidor', 'error');
    });
}

// ═══ Agregar un componente al DOM sin recargar la página ═══
function agregarComponenteAlDOM(comp) {
    const compList = document.querySelector('.comp-list');
    if (!compList) {
        // Si no existe la lista, crearla
        const emptyMsg = document.querySelector('.empty-text');
        if (emptyMsg) {
            const list = document.createElement('div');
            list.className = 'comp-list';
            emptyMsg.parentNode.replaceChild(list, emptyMsg);
            agregarComponenteAlDOM(comp);
            return;
        }
        return;
    }

    const div = document.createElement('div');
    div.className = 'comp-item';
    div.id = `comp-${comp.id}`;
    div.innerHTML = `
        <div class="comp-info">
            <span class="comp-type-badge">${escapeHtml(comp.tipo)}</span>
            <span class="comp-detail"><strong>Marca:</strong> ${escapeHtml(comp.marca) || '—'}</span>
            <span class="comp-detail"><strong>Modelo:</strong> ${escapeHtml(comp.modelo) || '—'}</span>
            <span class="comp-detail"><strong>Capacidad:</strong> ${escapeHtml(comp.capacidad) || '—'}</span>
            <span class="comp-detail"><strong>N.Serie:</strong> ${escapeHtml(comp.numero_serie) || '—'}</span>
            ${comp.especificaciones ? `<span class="comp-detail comp-specs">${escapeHtml(comp.especificaciones)}</span>` : ''}
            <span class="comp-state badge badge-green">${escapeHtml(comp.estado)}</span>
        </div>
        <div class="comp-actions">
            <button onclick="editarComponente(${comp.id})" class="btn-sm btn-primary" title="Editar">
                <i class="fas fa-pen"></i>
            </button>
            <button onclick="eliminarComponente(${comp.id}, '${escapeHtml(comp.tipo)}')" 
                    class="btn-sm btn-danger" title="Eliminar">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;

    compList.appendChild(div);

    // Actualizar el contador de componentes en la página
    actualizarContadorComponentes(1);
}

// ═══ Abrir modal de edición con los datos actuales del componente ═══
function editarComponente(compId) {
    // Buscar el elemento del componente en el DOM para extraer sus datos
    const compItem = document.getElementById(`comp-${compId}`);
    if (!compItem) {
        showNotification('No se encontró el componente', 'error');
        return;
    }

    // Extraer datos del DOM (método simple: leer los spans)
    const detalles = compItem.querySelectorAll('.comp-detail');
    let marca = '', modelo = '', capacidad = '', nserie = '';
    let especificaciones = '';

    detalles.forEach(d => {
        const texto = d.textContent;
        if (texto.startsWith('Marca:')) marca = texto.replace('Marca:', '').trim();
        if (texto.startsWith('Modelo:')) modelo = texto.replace('Modelo:', '').trim();
        if (texto.startsWith('Capacidad:')) capacidad = texto.replace('Capacidad:', '').trim();
        if (texto.startsWith('N.Serie:')) nserie = texto.replace('N.Serie:', '').trim();
    });

    const specEl = compItem.querySelector('.comp-specs');
    if (specEl) especificaciones = specEl.textContent.trim();

    // Rellenar el modal con los datos actuales
    document.getElementById('editCompId').value = compId;
    document.getElementById('editMarca').value = marca;
    document.getElementById('editModelo').value = modelo;
    document.getElementById('editCapacidad').value = capacidad;
    document.getElementById('editNS').value = nserie;
    document.getElementById('editSpecs').value = especificaciones;

    // Abrir el modal
    document.getElementById('modalEditComp').classList.remove('hidden');
}

// ═══ Guardar la edición del componente vía AJAX ═══
// IMPORTANTE: Al editar, el servidor compara el estado anterior con el nuevo.
// Si detecta diferencias, genera automáticamente una notificación de alerta
// para todos los administradores (cambio de hardware detectado).
function guardarEdicionComponente(event) {
    event.preventDefault();

    const compId = document.getElementById('editCompId').value;
    if (!compId) return;

    const data = {
        tipo: document.getElementById('editTipo').value,
        marca: document.getElementById('editMarca').value,
        modelo: document.getElementById('editModelo').value,
        capacidad: document.getElementById('editCapacidad').value,
        numero_serie: document.getElementById('editNS').value,
        estado: document.getElementById('editEstado').value,
        especificaciones: document.getElementById('editSpecs').value,
    };

    fetch(`/api/componente/editar/${compId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRF(),
        },
        body: JSON.stringify(data),
    })
    .then(r => r.json())
    .then(response => {
        if (response.ok) {
            // Actualizar el componente en el DOM
            actualizarComponenteEnDOM(compId, response);

            // Cerrar el modal
            cerrarModalComp();

            showNotification('Componente actualizado. Si hubo cambios, se notificó a los administradores.', 'success');
        } else {
            if (typeof response.error === 'object') {
                const errores = Object.values(response.error).join('. ');
                showNotification(errores, 'error');
            } else {
                showNotification(response.error || 'Error al editar', 'error');
            }
        }
    })
    .catch(() => {
        showNotification('Error de conexión', 'error');
    });
}

// ═══ Actualizar un componente en el DOM después de editar ═══
function actualizarComponenteEnDOM(compId, comp) {
    const compItem = document.getElementById(`comp-${compId}`);
    if (!compItem) return;

    const estadoClass = comp.estado === 'activo' ? 'badge-green' : 'badge-yellow';

    compItem.innerHTML = `
        <div class="comp-info">
            <span class="comp-type-badge">${escapeHtml(comp.tipo)}</span>
            <span class="comp-detail"><strong>Marca:</strong> ${escapeHtml(comp.marca) || '—'}</span>
            <span class="comp-detail"><strong>Modelo:</strong> ${escapeHtml(comp.modelo) || '—'}</span>
            <span class="comp-detail"><strong>Capacidad:</strong> ${escapeHtml(comp.capacidad) || '—'}</span>
            <span class="comp-detail"><strong>N.Serie:</strong> ${escapeHtml(comp.numero_serie) || '—'}</span>
            ${comp.especificaciones ? `<span class="comp-detail comp-specs">${escapeHtml(comp.especificaciones)}</span>` : ''}
            <span class="comp-state badge ${estadoClass}">${escapeHtml(comp.estado)}</span>
        </div>
        <div class="comp-actions">
            <button onclick="editarComponente(${compId})" class="btn-sm btn-primary" title="Editar">
                <i class="fas fa-pen"></i>
            </button>
            <button onclick="eliminarComponente(${compId}, '${escapeHtml(comp.tipo)}')" 
                    class="btn-sm btn-danger" title="Eliminar">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
}

// ═══ Eliminar un componente vía AJAX POST ═══
function eliminarComponente(compId, tipoNombre) {
    if (!confirm(`¿Eliminar el componente "${tipoNombre}"?\n\nSe registrará en el historial de cambios.`)) {
        return;
    }

    fetch(`/api/componente/eliminar/${compId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRF() },
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            // Eliminar del DOM con animación
            const compItem = document.getElementById(`comp-${compId}`);
            if (compItem) {
                compItem.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                compItem.style.opacity = '0';
                compItem.style.transform = 'translateX(-20px)';
                setTimeout(() => compItem.remove(), 300);
            }

            // Actualizar contador
            actualizarContadorComponentes(-1);

            showNotification(data.mensaje, 'success');
        } else {
            showNotification(data.error || 'Error al eliminar', 'error');
        }
    })
    .catch(() => {
        showNotification('Error de conexión', 'error');
    });
}

// ═══ Cerrar modal de edición de componente ═══
function cerrarModalComp() {
    document.getElementById('modalEditComp').classList.add('hidden');
}

// ═══ Actualizar el badge de contador de componentes ═══
function actualizarContadorComponentes(delta) {
    const badge = document.querySelector('.badge-blue');
    if (badge && badge.textContent.includes('registrados')) {
        // Extraer el número actual
        const match = badge.textContent.match(/(\d+)/);
        if (match) {
            const nuevo = Math.max(0, parseInt(match[1]) + delta);
            badge.textContent = `${nuevo} registrados`;
        }
    }
}

// ═══ Utilidad: escapar HTML ═══
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
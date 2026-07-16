/**
 * ════════════════════════════════════════════════════════════
 * JS DEL CHAT INTERNO
 * Funcionalidades:
 * - Polling para recibir mensajes nuevos cada 3 segundos
 * - Envío de mensajes vía AJAX POST
 * - Soporte para canal general y chats privados (1 a 1)
 * - Auto-scroll al último mensaje
 * - Detección de si el usuario está al final del chat
 * ════════════════════════════════════════════════════════════
 */

// ═══ Estado del chat ═══
let canalActual = 'general';          // Canal activo (general o privado_X_Y)
let tituloCanal = 'Canal General';    // Título mostrado en el header
let ultimoTimestamp = '';             // Último timestamp recibido (para polling incremental)
let pollingInterval = null;           // Referencia al intervalo de polling
let miUsername = '';                  // Nombre del usuario actual

// ═══ Inicialización al cargar la página ═══
document.addEventListener('DOMContentLoaded', function() {
    // Obtener el nombre de usuario del DOM (inyectado por el template)
    miUsername = document.body.dataset.username || '';

    // Cargar mensajes iniciales del canal general
    cargarMensajes();

    // Iniciar polling cada 3 segundos
    pollingInterval = setInterval(cargarMensajes, 3000);

    // Enter para enviar mensaje
    const input = document.getElementById('chatInput');
    if (input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                enviarMensaje(new Event('submit'));
            }
        });
    }
});

// ═══ Cambiar a un canal ═══
function cambiarCanal(canal, element, titulo) {
    canalActual = canal;
    tituloCanal = titulo;
    ultimoTimestamp = ''; // Reset para cargar todos los mensajes del nuevo canal

    // Actualizar UI
    document.getElementById('chatTitle').textContent = titulo;
    document.querySelectorAll('.contact-item').forEach(el => el.classList.remove('active'));
    if (element) element.classList.add('active');

    // Limpiar y recargar mensajes
    const container = document.getElementById('chatMessages');
    container.innerHTML = '<div class="chat-loading"><i class="fas fa-spinner fa-spin"></i> Cargando...</div>';
    cargarMensajes();

    // Cerrar sidebar en móvil
    const contacts = document.getElementById('chatContacts');
    if (contacts) contacts.classList.remove('open');
}

// ═══ Abrir chat privado con un usuario ═══
function abrirPrivado(userId, element, nombre) {
    // Construir el canal privado: IDs ordenados (menor primero)
    // Se necesita el ID del usuario actual del DOM
    const miIdElement = document.body.dataset.userid;
    if (!miIdElement) {
        showNotification('Error: no se pudo identificar al usuario actual', 'error');
        return;
    }
    const miId = parseInt(miIdElement);
    const otroId = parseInt(userId);
    const ids = [miId, otroId].sort((a, b) => a - b);
    const canal = `privado_${ids[0]}_${ids[1]}`;

    cambiarCanal(canal, element, nombre);
}

// ═══ Cargar mensajes vía AJAX (polling incremental) ═══
function cargarMensajes() {
    let url = `/api/chat/mensajes/?canal=${encodeURIComponent(canalActual)}`;
    if (ultimoTimestamp) {
        url += `&after=${encodeURIComponent(ultimoTimestamp)}`;
    }

    fetch(url)
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('chatMessages');
            if (!container) return;

            const mensajes = data.mensajes;

            if (!mensajes || mensajes.length === 0) {
                // Si es la primera carga y no hay mensajes
                if (!ultimoTimestamp) {
                    container.innerHTML = '<p class="empty-text">No hay mensajes en este canal. Sea el primero en escribir.</p>';
                }
                return;
            }

            // Si es la primera carga, limpiar el loading
            if (!ultimoTimestamp) {
                container.innerHTML = '';
            }

            // Renderizar cada mensaje nuevo
            const estabaAlFinal = estaAlFinal(container);

            mensajes.forEach(msg => {
                const bubble = crearBubble(msg);
                container.appendChild(bubble);

                // Actualizar timestamp al más reciente
                if (!ultimoTimestamp || msg.fecha > ultimoTimestamp) {
                    ultimoTimestamp = msg.fecha;
                }
            });

            // Auto-scroll solo si el usuario estaba al final
            if (estabaAlFinal || !ultimoTimestamp) {
                container.scrollTop = container.scrollHeight;
            }
        })
        .catch(err => {
            console.error('Error cargando mensajes:', err);
        });
}

// ═══ Crear un elemento HTML de bubble de mensaje ═══
function crearBubble(msg) {
    const div = document.createElement('div');
    div.className = `chat-bubble ${msg.es_mio ? 'chat-bubble-mine' : 'chat-bubble-other'}`;

    // Formatear la hora
    const fecha = new Date(msg.fecha);
    const hora = fecha.toLocaleTimeString('es-CU', { hour: '2-digit', minute: '2-digit' });

    let html = '';

    // Nombre del remitente (solo en mensajes de otros)
    if (!msg.es_mio) {
        html += `<span class="chat-bubble-name">${escapeHtml(msg.nombre)}</span>`;
    }

    // Contenido del mensaje (permitir saltos de línea)
    html += `<span class="chat-bubble-content">${escapeHtml(msg.contenido).replace(/\n/g, '<br>')}</span>`;

    // Hora
    html += `<span class="chat-bubble-time">${hora}</span>`;

    div.innerHTML = html;
    return div;
}

// ═══ Enviar mensaje vía AJAX POST ═══
function enviarMensaje(e) {
    e.preventDefault();

    const input = document.getElementById('chatInput');
    if (!input) return;

    const mensaje = input.value.trim();
    if (!mensaje) return;

    // Deshabilitar input mientras se envía
    input.disabled = true;

    fetch('/api/chat/enviar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRF(),
        },
        body: JSON.stringify({
            mensaje: mensaje,
            canal: canalActual,
        }),
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            showNotification(data.error, 'error');
        } else {
            // Agregar el mensaje inmediatamente a la UI
            const container = document.getElementById('chatMessages');
            // Eliminar mensaje de "no hay mensajes" si existe
            const emptyMsg = container.querySelector('.empty-text');
            if (emptyMsg) emptyMsg.remove();

            const bubble = crearBubble(data);
            container.appendChild(bubble);
            container.scrollTop = container.scrollHeight;

            // Limpiar input
            input.value = '';
            input.focus();
        }
    })
    .catch(err => {
        showNotification('Error al enviar el mensaje', 'error');
    })
    .finally(() => {
        input.disabled = false;
        input.focus();
    });
}

// ═══ Verificar si el usuario está al final del scroll ═══
function estaAlFinal(container) {
    // Con tolerancia de 100px para no ser tan estricto
    return (container.scrollHeight - container.scrollTop - container.clientHeight) < 100;
}

// ═══ Escapar HTML para prevenir XSS en el chat ═══
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
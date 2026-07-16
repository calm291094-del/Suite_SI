/*
  JS PRINCIPAL - Suite de Seguridad Informática
*/

// ═══ Estado global del sidebar ═══
let sidebarOpen = false;

function toggleSidebar(e) {
    if (e) e.preventDefault();
    sidebarOpen ? closeSidebar() : openSidebar();
}

function openSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (!sidebar || !overlay) return;
    
    sidebarOpen = true;
    sidebar.classList.add('open');
    overlay.classList.add('visible');
    document.body.style.overflow = 'hidden';
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (!sidebar || !overlay) return;

    sidebarOpen = false;
    sidebar.classList.remove('open');
    overlay.classList.remove('visible');
    document.body.style.overflow = '';
}

// ═══ Cerrar con Escape ═══
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        if (sidebarOpen) closeSidebar();
        const panel = document.getElementById('notifPanel');
        if (panel && !panel.classList.contains('hidden')) {
            panel.classList.add('hidden');
        }
    }
});

// ═══ Cerrar sidebar al hacer click en enlace interno (móvil) ═══
document.addEventListener('click', function(e) {
    // Cerrar sidebar si se hace click en un enlace
    if (sidebarOpen && e.target.closest('.sidebar-link')) {
        closeSidebar();
    }
    
    // Cerrar sidebar si se hace click en el overlay
    if (sidebarOpen && e.target.closest('#sidebarOverlay')) {
        closeSidebar();
    }

    // Cerrar notificaciones si se hace click fuera
    const wrapper = document.querySelector('.notif-wrapper');
    const panel = document.getElementById('notifPanel');
    if (wrapper && panel && !wrapper.contains(e.target) && !e.target.closest('.notif-btn')) {
        panel.classList.add('hidden');
    }
});

// ═══ Scroll-to-top button ═══
window.addEventListener('scroll', function() {
    const scrollTopBtn = document.getElementById('scrollTopBtn');
    if (!scrollTopBtn) return;
    
    if (window.scrollY > 300) {
        scrollTopBtn.classList.add('visible');
    } else {
        scrollTopBtn.classList.remove('visible');
    }
}, { passive: true });

// ═══ Panel de notificaciones ═══
function toggleNotifPanel() {
    const panel = document.getElementById('notifPanel');
    if (panel) panel.classList.toggle('hidden');
}

// ═══ Marcar todas las notificaciones ═══
function marcarTodasLeidas() {
    fetch('/api/notificaciones/todas-leidas/', {
        headers: { 'X-CSRFToken': getCSRF() },
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            const badge = document.getElementById('notifBadge');
            if (badge) {
                badge.classList.add('hidden');
                badge.textContent = '0';
            }
            document.querySelectorAll('.notif-mini.unread').forEach(el => el.classList.remove('unread'));
            showNotification('Todas las notificaciones marcadas como leídas', 'success');
        }
    });
}

// ═══ Cargar notificaciones en el panel desplegable ═══
function cargarNotifsPanel() {
    const list = document.getElementById('notifList');
    if (!list) return;
    list.innerHTML = '<p class="notif-empty">Haga clic en "Ver todas" para más detalles.</p>';
}

// ═══ Toast Notifications ═══
function showNotification(message, type) {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = 'toast toast-' + (type || 'info');
    const icons = { success: 'fa-circle-check', error: 'fa-circle-xmark', info: 'fa-circle-info' };
    toast.innerHTML = '<i class="fas ' + (icons[type] || icons.info) + '"></i><span>' + message + '</span>';
    container.appendChild(toast);
    setTimeout(() => { if (toast.parentNode) toast.remove(); }, 3000);
}

// ═══ getCSRF ═══
function getCSRF() {
    const el = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return el ? el.value : '';
}

// ═══ Auto-cerrar mensajes de Django ═══
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.message').forEach((msg, i) => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(-20px)';
            setTimeout(() => msg.remove(), 300);
        }, 5000 + (i * 400));
    });
});
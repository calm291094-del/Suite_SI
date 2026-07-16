/**
 * JS DE AUTENTICACIÓN - Universal
 * Detecta si está en Login, Registro o Cambiar Contraseña
 * y aplica la lógica correspondiente.
 */

// ═══ Toggle de visibilidad de contraseña (Ojito) ═══
function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon = btn.querySelector('i');
    if (!input) return;
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// ═══ Cálculo de fortaleza de contraseña ═══
function calcularFortaleza(password) {
    if (!password) return 0;
    let s = 0;
    if (password.length >= 8) s += Math.min(password.length * 2.5, 20);
    if (/[A-Z]/.test(password)) s += 15;
    if (/[a-z]/.test(password)) s += 10;
    if (/[0-9]/.test(password)) s += 15;
    if (/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) s += 20;
    if (password.length > 12) s += 10;
    if (password.length > 16) s += 10;
    // Penalizar caracteres repetidos
    if (/(.)\1{3,}/.test(password)) s -= 15;
    return Math.max(0, Math.min(100, Math.round(s)));
}

// ═══ Lógica que se ejecuta al cargar la página ═══
document.addEventListener('DOMContentLoaded', function() {
    
    // --- CASO 1: ESTAMOS EN CAMBIAR CONTRASEÑA ---
    // Busca el input de nueva contraseña por el ID que le pusimos en forms.py
    const pwdNueva = document.getElementById('pwd_nueva');
    const pwdConfirmar = document.getElementById('pwd_confirmar');
    
    if (pwdNueva) {
        pwdNueva.addEventListener('input', function() {
            const val = this.value;
            let score = calcularFortaleza(val);
            const colors = ['#ff3860', '#ff9500', '#fee440', '#00f5a0', '#00f5d4'];
            const labels = ['Muy débil', 'Débil', 'Aceptable', 'Buena', 'Excelente'];
            const idx = Math.min(4, Math.floor(score / 25));
            
            const bar = document.getElementById('strengthBar');
            const text = document.getElementById('strengthText');
            if (bar) {
                bar.style.width = score + '%';
                bar.style.background = colors[idx];
            }
            if (text) {
                text.innerHTML = '<span style="color:' + colors[idx] + '">' + score + '%</span> — ' + labels[idx];
            }
            verificarCoincidencia(pwdNueva, pwdConfirmar);
        });

        if (pwdConfirmar) {
            pwdConfirmar.addEventListener('input', function() {
                verificarCoincidencia(pwdNueva, pwdConfirmar);
            });
        }
        return; // Salir para no ejecutar la lógica del registro
    }

    // --- CASO 2: ESTAMOS EN REGISTRO ---
    // Django por defecto usa id="id_password1" y id="id_password2"
    const pwd1 = document.getElementById('id_password1');
    const pwd2 = document.getElementById('id_password2');
    
    if (pwd1) {
        pwd1.addEventListener('input', function() {
            const val = this.value;
            let score = calcularFortaleza(val);
            const colors = ['#ff3860', '#ff9500', '#fee440', '#00f5a0', '#00f5d4'];
            const labels = ['Muy débil', 'Débil', 'Aceptable', 'Buena', 'Excelente'];
            const idx = Math.min(4, Math.floor(score / 25));
            
            const bar = document.getElementById('strengthBar');
            const text = document.getElementById('strengthText');
            if (bar) {
                bar.style.width = score + '%';
                bar.style.background = colors[idx];
            }
            if (text) {
                text.innerHTML = '<span style="color:' + colors[idx] + '">' + score + '%</span> — ' + labels[idx];
            }
            verificarCoincidencia(pwd1, pwd2);
        });

        if (pwd2) {
            pwd2.addEventListener('input', function() {
                verificarCoincidencia(pwd1, pwd2);
            });
        }
    }
});

// ═══ Verificación de coincidencia genérica ═══
function verificarCoincidencia(input1, input2) {
    // Busca el div donde se muestra el mensaje (puede tener id="matchText" o class="match-text")
    const matchText = document.getElementById('matchText') || document.querySelector('.match-text');
    if (!input1 || !input2 || !matchText) return;

    const val1 = input1.value;
    const val2 = input2.value;
    
    if (!val2) {
        matchText.innerHTML = '';
        return;
    }
    
    if (val1 === val2) {
        matchText.innerHTML = '<i class="fas fa-check-circle" style="color:#00f5a0"></i> Las contraseñas coinciden';
    } else {
        matchText.innerHTML = '<i class="fas fa-times-circle" style="color:#ff3860"></i> Las contraseñas no coinciden';
    }
}
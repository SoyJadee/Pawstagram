
// Función para mostrar/ocultar contraseña (robusta con IDs de Django)
function togglePassword(inputId = 'id_password1', iconId = 'toggleIcon1') {
    let passwordInput = document.getElementById(inputId);
    const toggleIcon = document.getElementById(iconId);
    if (!passwordInput) {
        // fallback común: primer input password
        passwordInput = document.querySelector('input[type="password"]');
    }
    if (!passwordInput) return;

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        if (toggleIcon) toggleIcon.className = 'fas fa-eye-slash text-sm';
    } else {
        passwordInput.type = 'password';
        if (toggleIcon) toggleIcon.className = 'fas fa-eye text-sm';
    }
}


// Función para mostrar/ocultar contraseña (robusta con IDs de Django)
function togglePassword(inputId = 'id_password2', iconId = 'toggleIcon2') {
    let passwordInput = document.getElementById(inputId);
    const toggleIcon = document.getElementById(iconId);
    if (!passwordInput) {
        // fallback común: primer input password
        passwordInput = document.querySelector('input[type="password"]');
    }
    if (!passwordInput) return;

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        if (toggleIcon) toggleIcon.className = 'fas fa-eye-slash text-sm';
    } else {
        passwordInput.type = 'password';
        if (toggleIcon) toggleIcon.className = 'fas fa-eye text-sm';
    }
}
// Validador de fortaleza de contraseña
function checkPasswordStrength(password) {
    let strength = 0;
    let feedback = [];
    
    if (password.length >= 8) strength += 20;
    else feedback.push('Mínimo 8 caracteres');
    
    if (/[a-z]/.test(password)) strength += 20;
    else feedback.push('Una minúscula');
    
    if (/[A-Z]/.test(password)) strength += 20;
    else feedback.push('Una mayúscula');
    
    if (/[0-9]/.test(password)) strength += 20;
    else feedback.push('Un número');
    
    if (/[^A-Za-z0-9]/.test(password)) strength += 20;
    else feedback.push('Un símbolo');
    
    return { strength, feedback };
}

// Actualizar indicador de fortaleza
function updatePasswordStrength() {
    const passwordInput = document.getElementById('id_password1');
    const strengthBar = document.getElementById('passwordStrength');
    const strengthText = document.getElementById('strengthText');
    
    if (!passwordInput || !strengthBar) return;
    
    const password = passwordInput.value;
    const { strength, feedback } = checkPasswordStrength(password);
    
    // Actualizar barra
    strengthBar.style.width = `${strength}%`;
    
    // Cambiar color según fortaleza
    if (strength < 40) {
        strengthBar.className = 'h-full bg-red-400 rounded-full transition-all duration-300';
        strengthText.textContent = 'Débil';
        strengthText.className = 'text-xs text-red-500 mt-1';
    } else if (strength < 80) {
        strengthBar.className = 'h-full bg-yellow-400 rounded-full transition-all duration-300';
        strengthText.textContent = 'Media';
        strengthText.className = 'text-xs text-yellow-600 mt-1';
    } else {
        strengthBar.className = 'h-full bg-green-400 rounded-full transition-all duration-300';
        strengthText.textContent = 'Fuerte';
        strengthText.className = 'text-xs text-green-600 mt-1';
    }
}

// Validar username
function validateUsername(username) {
    const regex = /^[a-zA-Z0-9_]+$/;
    return regex.test(username) && username.length >= 3;
}

// Mostrar notificación
function showNotification(message, type = 'success') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full ${
        type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
    }`;
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} mr-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.style.transform = 'translateX(full)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Event Listeners cuando el DOM carga
document.addEventListener('DOMContentLoaded', function() {
    
    // LOGIN FORM
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Validaciones básicas
            if (!email || !password) {
                showNotification('Por favor completa todos los campos', 'error');
                return;
            }
            
            // Simular login
            const loginBtn = loginForm.querySelector('button[type="submit"]');
            const originalText = loginBtn.innerHTML;
            
            loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Iniciando sesión...';
            loginBtn.disabled = true;
            
            setTimeout(() => {
                // Simular éxito
                showNotification('¡Bienvenido de vuelta!');
                // Aquí irá la ruta de la página principal
                
                loginBtn.innerHTML = originalText;
                loginBtn.disabled = false;
            }, 2000);
        });
    }
    
    // REGISTER FORM
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        // Listener para fortaleza de contraseña
        const passwordInput = document.getElementById('id_password1');
        if (passwordInput) {
            passwordInput.addEventListener('input', updatePasswordStrength);
        }
        
        // Validar username en tiempo real (usar ID de Django)
        const usernameInput = document.getElementById('id_username');
        if (usernameInput) {
            usernameInput.addEventListener('input', function() {
                const username = this.value;
                // Evitar estilos inline: alternar clases de Tailwind
                this.classList.toggle('border-red-400', username.length > 0 && !validateUsername(username));
                this.classList.toggle('border-gray-200', !(username.length > 0 && !validateUsername(username)));
            });
        }
        // Permitir que el form haga submit al backend de Django
    }
    
    // RECOVERY FORM
    const recoveryForm = document.getElementById('recoveryForm');
    if (recoveryForm) {
        recoveryForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('recoveryEmail').value;
            
            if (!email) {
                showNotification('Por favor ingresa tu email', 'error');
                return;
            }
            
            // Simular envío
            const recoveryBtn = recoveryForm.querySelector('button[type="submit"]');
            const originalText = recoveryBtn.innerHTML;
            
            recoveryBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Enviando...';
            recoveryBtn.disabled = true;
            
            setTimeout(() => {
                showStep2(email);
                recoveryBtn.innerHTML = originalText;
                recoveryBtn.disabled = false;
            }, 2000);
        });
    }
});

// Funciones para recovery
function showStep2(email) {
    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.remove('hidden');
    document.getElementById('sentEmail').textContent = email;
    
    startCountdown();
}

function showStep1() {
    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step1').classList.remove('hidden');
}

function startCountdown() {
    let timeLeft = 60;
    const countdownEl = document.getElementById('countdown');
    const resendBtn = document.getElementById('resendBtn');
    const resendText = document.getElementById('resendText');
    
    const timer = setInterval(() => {
        timeLeft--;
        countdownEl.textContent = timeLeft;
        
        if (timeLeft <= 0) {
            clearInterval(timer);
            resendBtn.disabled = false;
            resendBtn.className = 'w-full bg-gradient-to-r from-paw-teal to-paw-green text-white font-semibold py-3 rounded-xl hover:from-paw-green hover:to-paw-teal transition-colors mb-4';
            resendText.innerHTML = '<i class="fas fa-redo mr-2"></i>Reenviar email';
        }
    }, 1000);
}

function resendEmail() {
    const resendBtn = document.getElementById('resendBtn');
    const originalText = resendBtn.innerHTML;
    
    resendBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Reenviando...';
    resendBtn.disabled = true;
    
    setTimeout(() => {
        showNotification('Email reenviado exitosamente');
        startCountdown();
        resendBtn.className = 'w-full bg-gray-100 text-gray-700 font-semibold py-3 rounded-xl hover:bg-gray-200 transition-colors mb-4';
    }, 1500);
}

// Funciones de utilidad
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function sanitizeInput(input) {
    return input.trim().replace(/[<>]/g, '');
}

// Prevenir ataques XSS básicos
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
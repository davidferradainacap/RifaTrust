/**
 * ============================================================================
 * SISTEMA DE LOADING PROFESIONAL - RifaTrust
 * ============================================================================
 * Maneja spinners, overlays y estados de carga en toda la aplicación
 */

// Objeto global para manejar el loading
const LoadingManager = {
    overlay: null,

    /**
     * Inicializa el sistema de loading
     */
    init() {
        // Crear overlay si no existe
        if (!this.overlay) {
            this.createOverlay();
        }

        // Interceptar envío de formularios
        this.setupFormInterceptors();

        // Interceptar clicks en botones de submit
        this.setupButtonInterceptors();
    },

    /**
     * Crea el overlay de loading
     */
    createOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'globalLoadingOverlay';
        overlay.innerHTML = `
            <div class="spinner-container">
                <div class="spinner">
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                </div>
                <div class="loading-text" id="loadingText">Procesando...</div>
                <div class="loading-subtext" id="loadingSubtext">Por favor espera</div>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
        this.overlay = overlay;
    },

    /**
     * Muestra el overlay de loading
     */
    show(text = 'Procesando...', subtext = 'Por favor espera') {
        if (!this.overlay) {
            this.createOverlay();
        }

        const loadingText = document.getElementById('loadingText');
        const loadingSubtext = document.getElementById('loadingSubtext');

        if (loadingText) loadingText.textContent = text;
        if (loadingSubtext) loadingSubtext.textContent = subtext;

        this.overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    },

    /**
     * Oculta el overlay de loading
     */
    hide() {
        if (this.overlay) {
            this.overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    },

    /**
     * Configura interceptores para formularios
     */
    setupFormInterceptors() {
        // Formulario de login
        const loginForm = document.querySelector('form[action*="login"]');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                this.show('Iniciando sesión...', 'Verificando credenciales');
                this.addButtonLoading(loginForm.querySelector('button[type="submit"]'));
            });
        }

        // Formulario de registro
        const registerForm = document.querySelector('form[action*="register"]');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => {
                this.show('Creando cuenta...', 'Esto puede tomar unos segundos');
                this.addButtonLoading(registerForm.querySelector('button[type="submit"]'));
            });
        }

        // Formulario de recuperación de contraseña
        const passwordResetForm = document.querySelector('form[action*="password-reset"]');
        if (passwordResetForm) {
            passwordResetForm.addEventListener('submit', (e) => {
                this.show('Enviando email...', 'Generando enlace de recuperación');
                this.addButtonLoading(passwordResetForm.querySelector('button[type="submit"]'));
            });
        }

        // Formulario de confirmación de contraseña
        const confirmPasswordForm = document.getElementById('resetForm');
        if (confirmPasswordForm) {
            confirmPasswordForm.addEventListener('submit', (e) => {
                this.show('Actualizando contraseña...', 'Guardando cambios');
                this.addButtonLoading(confirmPasswordForm.querySelector('button[type="submit"]'));
            });
        }

        // Formulario de perfil
        const profileForm = document.querySelector('form[action*="profile"]');
        if (profileForm) {
            profileForm.addEventListener('submit', (e) => {
                this.show('Guardando cambios...', 'Actualizando perfil');
                this.addButtonLoading(profileForm.querySelector('button[type="submit"]'));
            });
        }
    },

    /**
     * Configura interceptores para botones
     */
    setupButtonInterceptors() {
        // Botones que disparan AJAX
        document.querySelectorAll('[data-loading]').forEach(button => {
            button.addEventListener('click', () => {
                const loadingText = button.dataset.loadingText || 'Procesando...';
                const loadingSubtext = button.dataset.loadingSubtext || 'Por favor espera';
                this.show(loadingText, loadingSubtext);
                this.addButtonLoading(button);
            });
        });
    },

    /**
     * Agrega estado de loading a un botón específico
     */
    addButtonLoading(button) {
        if (button) {
            button.classList.add('loading');
            button.disabled = true;
        }
    },

    /**
     * Remueve estado de loading de un botón específico
     */
    removeButtonLoading(button) {
        if (button) {
            button.classList.remove('loading');
            button.disabled = false;
        }
    },

    /**
     * Remueve loading de todos los botones
     */
    removeAllButtonLoading() {
        document.querySelectorAll('.btn.loading').forEach(button => {
            this.removeButtonLoading(button);
        });
    }
};

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Pequeño delay para que otros scripts se inicialicen primero (como el menú)
        setTimeout(() => LoadingManager.init(), 100);
    });
} else {
    setTimeout(() => LoadingManager.init(), 100);
}

// Ocultar loading cuando la página termina de cargar
window.addEventListener('load', () => {
    setTimeout(() => {
        LoadingManager.hide();
        LoadingManager.removeAllButtonLoading();
    }, 500);
});

// Ocultar loading si hay error
window.addEventListener('error', () => {
    LoadingManager.hide();
    LoadingManager.removeAllButtonLoading();
});

// Exponer globalmente
window.LoadingManager = LoadingManager;

/**
 * ============================================================================
 * UTILIDADES PARA AJAX/FETCH
 * ============================================================================
 */

/**
 * Wrapper para fetch con loading automático
 */
async function fetchWithLoading(url, options = {}, loadingText = 'Cargando...', loadingSubtext = 'Por favor espera') {
    LoadingManager.show(loadingText, loadingSubtext);

    try {
        const response = await fetch(url, options);
        return response;
    } catch (error) {
        console.error('Error en fetch:', error);
        throw error;
    } finally {
        LoadingManager.hide();
    }
}

// Exponer función fetch con loading
window.fetchWithLoading = fetchWithLoading;

/**
 * ============================================================================
 * SKELETON LOADERS
 * ============================================================================
 */

/**
 * Muestra skeleton loaders en un contenedor
 */
function showSkeletonLoaders(container, count = 3) {
    if (typeof container === 'string') {
        container = document.querySelector(container);
    }

    if (!container) return;

    container.innerHTML = '';

    for (let i = 0; i < count; i++) {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton skeleton-card';
        container.appendChild(skeleton);
    }
}

/**
 * Oculta skeleton loaders
 */
function hideSkeletonLoaders(container) {
    if (typeof container === 'string') {
        container = document.querySelector(container);
    }

    if (!container) return;

    const skeletons = container.querySelectorAll('.skeleton');
    skeletons.forEach(skeleton => skeleton.remove());
}

// Exponer funciones de skeleton
window.showSkeletonLoaders = showSkeletonLoaders;
window.hideSkeletonLoaders = hideSkeletonLoaders;

/**
 * ============================================================================
 * MANEJO DE ERRORES Y TIMEOUT
 * ============================================================================
 */

// Si la página tarda mucho en cargar, ocultar loading después de 10 segundos
setTimeout(() => {
    if (LoadingManager.overlay && LoadingManager.overlay.classList.contains('active')) {
        console.warn('Loading timeout - ocultando automáticamente');
        LoadingManager.hide();
        LoadingManager.removeAllButtonLoading();
    }
}, 10000);

console.log('✅ Sistema de Loading inicializado correctamente');

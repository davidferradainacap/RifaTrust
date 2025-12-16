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
        
        // Interceptar links con data-loading
        this.setupLinkInterceptors();
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
        // ==========================================
        // AUTENTICACIÓN Y USUARIOS
        // ==========================================
        
        // Formulario de login
        const loginForm = document.querySelector('form[action*="login"]');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                this.show('Iniciando sesión...', 'Verificando tus credenciales');
                this.addButtonLoading(loginForm.querySelector('button[type="submit"]'));
            });
        }

        // Formulario de registro
        const registerForm = document.querySelector('form[action*="register"]');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => {
                this.show('Creando tu cuenta...', 'Esto tomará solo un momento');
                this.addButtonLoading(registerForm.querySelector('button[type="submit"]'));
            });
        }

        // Formulario de recuperación de contraseña
        const passwordResetForm = document.querySelector('form[action*="password-reset"]');
        if (passwordResetForm) {
            passwordResetForm.addEventListener('submit', (e) => {
                this.show('Enviando correo...', 'Generando enlace de recuperación');
                this.addButtonLoading(passwordResetForm.querySelector('button[type="submit"]'));
            });
        }

        // Formulario de confirmación de contraseña
        const confirmPasswordForm = document.getElementById('resetForm');
        if (confirmPasswordForm) {
            confirmPasswordForm.addEventListener('submit', (e) => {
                this.show('Actualizando contraseña...', 'Guardando tu nueva contraseña');
                this.addButtonLoading(confirmPasswordForm.querySelector('button[type="submit"]'));
            });
        }

        // Formulario de perfil
        const profileForm = document.querySelector('form[action*="profile"]');
        if (profileForm) {
            profileForm.addEventListener('submit', (e) => {
                this.show('Guardando perfil...', 'Actualizando tu información');
                this.addButtonLoading(profileForm.querySelector('button[type="submit"]'));
            });
        }
        
        // ==========================================
        // RIFAS
        // ==========================================
        
        // Crear rifa
        const createRaffleForm = document.querySelector('form[action*="raffles/create"], form[action*="/create/"]');
        if (createRaffleForm || window.location.pathname.includes('/create')) {
            const form = createRaffleForm || document.querySelector('form[enctype="multipart/form-data"]');
            if (form) {
                form.addEventListener('submit', (e) => {
                    this.show('Creando rifa...', 'Subiendo imágenes y configurando');
                    this.addButtonLoading(form.querySelector('button[type="submit"]'));
                });
            }
        }
        
        // Editar rifa
        if (window.location.pathname.includes('/edit/') || window.location.pathname.includes('/editar/')) {
            const editForm = document.querySelector('form[enctype="multipart/form-data"]');
            if (editForm) {
                editForm.addEventListener('submit', (e) => {
                    this.show('Guardando cambios...', 'Actualizando la rifa');
                    this.addButtonLoading(editForm.querySelector('button[type="submit"]'));
                });
            }
        }
        
        // Comprar boleto
        if (window.location.pathname.includes('/buy/') || window.location.pathname.includes('/comprar/')) {
            const buyForm = document.querySelector('form[method="post"]');
            if (buyForm) {
                buyForm.addEventListener('submit', (e) => {
                    this.show('Procesando compra...', 'Preparando tu pago');
                    this.addButtonLoading(buyForm.querySelector('button[type="submit"]'));
                });
            }
        }
        
        // ==========================================
        // PAGOS
        // ==========================================
        
        // Proceso de pago
        if (window.location.pathname.includes('/payments/') || window.location.pathname.includes('/pago/')) {
            const paymentForm = document.querySelector('form[method="post"]');
            if (paymentForm) {
                paymentForm.addEventListener('submit', (e) => {
                    this.show('Procesando pago...', 'Conectando con la pasarela de pago');
                    this.addButtonLoading(paymentForm.querySelector('button[type="submit"]'));
                });
            }
        }
        
        // ==========================================
        // ADMIN PANEL
        // ==========================================
        
        // Formularios del panel admin
        if (window.location.pathname.includes('/admin-panel/')) {
            document.querySelectorAll('form[method="post"]').forEach(form => {
                form.addEventListener('submit', (e) => {
                    this.show('Procesando...', 'Guardando cambios en el sistema');
                    this.addButtonLoading(form.querySelector('button[type="submit"]'));
                });
            });
        }
        
        // ==========================================
        // FORMULARIOS GENÉRICOS (fallback)
        // ==========================================
        
        // Cualquier formulario POST que no tenga interceptor específico
        document.querySelectorAll('form[method="post"]').forEach(form => {
            if (!form.hasAttribute('data-no-loading') && !form.dataset.loadingAttached) {
                form.dataset.loadingAttached = 'true';
                form.addEventListener('submit', (e) => {
                    // Solo mostrar si no hay otro loading activo
                    if (!this.overlay || !this.overlay.classList.contains('active')) {
                        this.show('Procesando...', 'Por favor espera un momento');
                        this.addButtonLoading(form.querySelector('button[type="submit"]'));
                    }
                });
            }
        });
    },

    /**
     * Configura interceptores para botones
     */
    setupButtonInterceptors() {
        // Botones con data-loading attribute
        document.querySelectorAll('[data-loading]').forEach(button => {
            button.addEventListener('click', () => {
                const loadingText = button.dataset.loadingText || 'Procesando...';
                const loadingSubtext = button.dataset.loadingSubtext || 'Por favor espera';
                this.show(loadingText, loadingSubtext);
                this.addButtonLoading(button);
            });
        });
        
        // Botón de eliminar cuenta
        const deleteAccountBtn = document.querySelector('[onclick*="deleteAccount"], #deleteAccountBtn');
        if (deleteAccountBtn) {
            // Se maneja en el modal de confirmación
        }
        
        // Botones de aprobar/rechazar en admin
        document.querySelectorAll('.btn-approve, [data-action="approve"]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.show('Aprobando...', 'Activando la rifa');
            });
        });
        
        document.querySelectorAll('.btn-reject, [data-action="reject"]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.show('Rechazando...', 'Procesando rechazo');
            });
        });
        
        // Botones de ejecutar sorteo
        document.querySelectorAll('[data-action="draw"], .btn-draw, [onclick*="sorteo"]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.show('Ejecutando sorteo...', '¡Eligiendo al ganador!');
            });
        });
    },
    
    /**
     * Configura interceptores para links
     */
    setupLinkInterceptors() {
        // Links con data-loading
        document.querySelectorAll('a[data-loading]').forEach(link => {
            link.addEventListener('click', (e) => {
                const loadingText = link.dataset.loadingText || 'Cargando...';
                const loadingSubtext = link.dataset.loadingSubtext || 'Redirigiendo';
                this.show(loadingText, loadingSubtext);
            });
        });
        
        // Links a comprar boletos
        document.querySelectorAll('a[href*="/buy/"], a[href*="/comprar/"]').forEach(link => {
            link.addEventListener('click', () => {
                this.show('Cargando...', 'Preparando la compra');
            });
        });
        
        // Links a ver detalles de rifa
        document.querySelectorAll('a[href*="/raffles/"][href$="/"]').forEach(link => {
            if (!link.href.includes('/create') && !link.href.includes('/edit') && !link.href.includes('/buy')) {
                link.addEventListener('click', () => {
                    this.show('Cargando rifa...', 'Obteniendo información');
                });
            }
        });
        
        // Links de logout
        document.querySelectorAll('a[href*="logout"]').forEach(link => {
            link.addEventListener('click', () => {
                this.show('Cerrando sesión...', 'Hasta pronto');
            });
        });
        
        // Links al dashboard
        document.querySelectorAll('a[href*="dashboard"]').forEach(link => {
            link.addEventListener('click', () => {
                this.show('Cargando dashboard...', 'Preparando tu panel');
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

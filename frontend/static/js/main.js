// Sistema de Rifas - JavaScript Principal

// Validación de formularios
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 main.js: DOM cargado, inicializando...');

    // Mobile Menu Toggle
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navLinks = document.getElementById('navLinks');
    const mobileMenuOverlay = document.getElementById('mobileMenuOverlay');

    console.log('📱 Elementos menú:', {
        toggle: !!mobileMenuToggle,
        navLinks: !!navLinks,
        overlay: !!mobileMenuOverlay
    });

    if (mobileMenuToggle && navLinks && mobileMenuOverlay) {
        console.log('✅ Todos los elementos del menú encontrados');

        // Toggle menu
        mobileMenuToggle.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('🍔 Click en hamburguesa');

            const isActive = mobileMenuToggle.classList.toggle('active');
            navLinks.classList.toggle('active');
            mobileMenuOverlay.classList.toggle('active');
            document.body.style.overflow = isActive ? 'hidden' : '';

            console.log('📊 Estado menú:', isActive ? 'ABIERTO' : 'CERRADO');
        });

        // Close menu when clicking overlay
        mobileMenuOverlay.addEventListener('click', function (e) {
            e.preventDefault();
            console.log('🖱️ Click en overlay, cerrando menú');

            mobileMenuToggle.classList.remove('active');
            navLinks.classList.remove('active');
            mobileMenuOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });

        // Close menu when clicking a link
        const navLinkItems = navLinks.querySelectorAll('a');
        console.log(`🔗 ${navLinkItems.length} links encontrados en navegación`);

        navLinkItems.forEach(link => {
            link.addEventListener('click', function () {
                console.log('🔗 Click en link, cerrando menú');
                mobileMenuToggle.classList.remove('active');
                navLinks.classList.remove('active');
                mobileMenuOverlay.classList.remove('active');
                document.body.style.overflow = '';
            });
        });

        // Close menu on window resize if open
        window.addEventListener('resize', function () {
            if (window.innerWidth > 768) {
                mobileMenuToggle.classList.remove('active');
                navLinks.classList.remove('active');
                mobileMenuOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        console.log('✅ Event listeners del menú móvil configurados');
    } else {
        console.error('❌ No se encontraron todos los elementos del menú móvil');
    }

    // Auto-ocultar alertas después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Confirmación de acciones destructivas
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // Preview de imágenes
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    let preview = input.parentElement.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.className = 'image-preview';
                        preview.style.maxWidth = '200px';
                        preview.style.marginTop = '10px';
                        preview.style.borderRadius = '8px';
                        input.parentElement.appendChild(preview);
                    }
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    });
});

// Formato de números
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN'
    }).format(amount);
}

// Contador de caracteres para textareas
const textareas = document.querySelectorAll('textarea[maxlength]');
textareas.forEach(textarea => {
    const maxLength = textarea.getAttribute('maxlength');
    const counter = document.createElement('div');
    counter.className = 'form-help';
    counter.style.textAlign = 'right';

    const updateCounter = () => {
        const remaining = maxLength - textarea.value.length;
        counter.textContent = `${remaining} caracteres restantes`;
        counter.style.color = remaining < 20 ? 'var(--warning)' : 'var(--gray-500)';
    };

    textarea.addEventListener('input', updateCounter);
    textarea.parentElement.appendChild(counter);
    updateCounter();
});

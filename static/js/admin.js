// ==================== GLOBAL VARIABLES ====================
let sidebarCollapsed = false;
let currentTheme = localStorage.getItem('theme') || 'light';

// ==================== INIT ON LOAD ====================
document.addEventListener('DOMContentLoaded', function () {
    initTheme();
    initSidebar();
    initTime();
    initTooltips();
    initDataTables();
    initCharts();
    initSearchGlobal();
    initNotifications();
    initQuickActions();
});

// ==================== THEME MANAGEMENT ====================
function initTheme() {
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon();

    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    updateThemeIcon();
    showToast('Tema cambiado', `Modo ${currentTheme === 'dark' ? 'oscuro' : 'claro'} activado`, 'success');
}

function updateThemeIcon() {
    const icon = document.querySelector('#themeToggle i');
    if (icon) {
        icon.className = currentTheme === 'light' ? 'bi bi-moon-stars fs-5' : 'bi bi-sun fs-5';
    }
}

// ==================== SIDEBAR MANAGEMENT ====================
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('collapsed');
            sidebarCollapsed = !sidebarCollapsed;
            localStorage.setItem('sidebarCollapsed', sidebarCollapsed);
        });

        // Restaurar estado del sidebar
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            sidebar.classList.add('collapsed');
            sidebarCollapsed = true;
        }
    }

    // Mobile sidebar
    if (window.innerWidth < 992) {
        sidebar?.classList.add('collapsed');

        sidebarToggle?.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });

        // Close sidebar when clicking outside
        document.addEventListener('click', function (e) {
            if (!sidebar?.contains(e.target) && !sidebarToggle?.contains(e.target)) {
                sidebar?.classList.remove('show');
            }
        });
    }
}

// ==================== CURRENT TIME ====================
function initTime() {
    updateTime();
    setInterval(updateTime, 1000);
}

function updateTime() {
    const timeElement = document.getElementById('currentTime');
    if (timeElement) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
        timeElement.textContent = timeString;
    }
}

// ==================== TOOLTIPS ====================
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ==================== DATATABLES ====================
function initDataTables() {
    if (typeof $.fn.dataTable !== 'undefined') {
        $('.data-table').each(function () {
            if (!$.fn.DataTable.isDataTable(this)) {
                $(this).DataTable({
                    language: {
                        url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json'
                    },
                    pageLength: 25,
                    responsive: true,
                    order: [[0, 'desc']],
                    dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
                        '<"row"<"col-sm-12"tr>>' +
                        '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>'
                });
            }
        });
    }
}

// ==================== CHARTS ====================
function initCharts() {
    // Se inicializarán charts específicos en cada página
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.color = getComputedStyle(document.documentElement)
            .getPropertyValue('--text-secondary').trim();
    }
}

// ==================== GLOBAL SEARCH ====================
function initSearchGlobal() {
    const searchInput = document.getElementById('globalSearchInput');
    let searchTimeout;

    if (searchInput) {
        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            const query = this.value.trim();

            if (query.length >= 3) {
                searchTimeout = setTimeout(() => {
                    performGlobalSearch(query);
                }, 500);
            }
        });

        // Keyboard shortcut: Ctrl+K
        document.addEventListener('keydown', function (e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }
}

function performGlobalSearch(query) {
    // Aquí se implementaría la búsqueda AJAX
    console.log('Buscando:', query);
    // TODO: Implementar endpoint de búsqueda global
}

// ==================== NOTIFICATIONS ====================
function initNotifications() {
    loadNotifications();

    // Actualizar cada 60 segundos
    setInterval(loadNotifications, 60000);
}

function loadNotifications() {
    // TODO: Implementar carga de notificaciones vía AJAX
    const notificationsList = document.getElementById('notificationsList');
    const notificationCount = document.getElementById('notificationCount');

    // Placeholder - reemplazar con llamada AJAX real
    // fetch('/api/notifications/unread/')
    //     .then(response => response.json())
    //     .then(data => {
    //         updateNotifications(data);
    //     });
}

function updateNotifications(notifications) {
    const notificationsList = document.getElementById('notificationsList');
    const notificationCount = document.getElementById('notificationCount');

    if (notifications.length === 0) {
        notificationsList.innerHTML = `
            <div class="text-center py-3 text-muted small">
                No hay notificaciones nuevas
            </div>
        `;
        notificationCount.style.display = 'none';
    } else {
        notificationsList.innerHTML = notifications.map(notif => `
            <a href="${notif.url}" class="notification-item">
                <div class="d-flex">
                    <div class="flex-grow-1">
                        <div class="fw-bold small">${notif.title}</div>
                        <div class="small text-muted">${notif.message}</div>
                    </div>
                    <div class="small text-muted">${notif.time}</div>
                </div>
            </a>
        `).join('');

        notificationCount.textContent = notifications.length;
        notificationCount.style.display = 'inline';
    }
}

// ==================== TOAST NOTIFICATIONS ====================
function showToast(title, message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;

    const toastId = 'toast-' + Date.now();
    const icons = {
        success: 'check-circle',
        danger: 'x-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };

    const toastHTML = `
        <div class="toast align-items-center border-0" role="alert" aria-live="assertive" aria-atomic="true" id="${toastId}">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-${icons[type]} me-2 text-${type}"></i>
                    <strong>${title}</strong>
                    <p class="mb-0 small">${message}</p>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', function () {
        this.remove();
    });
}

// ==================== QUICK ACTIONS ====================
function initQuickActions() {
    const quickUserForm = document.getElementById('quickUserForm');

    if (quickUserForm) {
        quickUserForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = {
                nombre: document.getElementById('quickUserName').value,
                email: document.getElementById('quickUserEmail').value,
                rol: document.getElementById('quickUserRol').value
            };

            createQuickUser(formData);
        });
    }
}

function createQuickUser(data) {
    // TODO: Implementar creación de usuario vía AJAX
    console.log('Creando usuario:', data);

    // Placeholder
    showToast('Usuario creado', `${data.nombre} ha sido creado exitosamente`, 'success');

    // Cerrar modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('quickUserModal'));
    modal?.hide();

    // Limpiar formulario
    document.getElementById('quickUserForm').reset();

    // TODO: Recargar tabla de usuarios si está visible
}

// ==================== FILTERS ====================
function initFilters() {
    const filterForms = document.querySelectorAll('.filter-form');

    filterForms.forEach(form => {
        const inputs = form.querySelectorAll('input, select');

        inputs.forEach(input => {
            input.addEventListener('change', function () {
                form.submit();
            });
        });
    });
}

function clearFilters() {
    const filterForm = document.querySelector('.filter-form');
    if (filterForm) {
        const inputs = filterForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
        filterForm.submit();
    }
}

// ==================== CONFIRMATION DIALOGS ====================
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function confirmDelete(itemName, url) {
    if (confirm(`¿Estás seguro de que deseas eliminar "${itemName}"? Esta acción no se puede deshacer.`)) {
        // TODO: Implementar eliminación vía AJAX
        fetch(url, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Eliminado', `${itemName} ha sido eliminado`, 'success');
                    location.reload();
                } else {
                    showToast('Error', data.message || 'No se pudo eliminar', 'danger');
                }
            })
            .catch(error => {
                showToast('Error', 'Ocurrió un error al eliminar', 'danger');
                console.error('Error:', error);
            });
    }
}

// ==================== BULK ACTIONS ====================
function initBulkActions() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    const bulkActionsBar = document.getElementById('bulkActionsBar');
    const selectedCountElement = document.getElementById('selectedCount');

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function () {
            itemCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateBulkActionsBar();
        });
    }

    itemCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateBulkActionsBar);
    });

    function updateBulkActionsBar() {
        const selectedCount = document.querySelectorAll('.item-checkbox:checked').length;

        if (selectedCount > 0) {
            bulkActionsBar?.classList.remove('d-none');
            if (selectedCountElement) {
                selectedCountElement.textContent = selectedCount;
            }
        } else {
            bulkActionsBar?.classList.add('d-none');
        }
    }
}

function performBulkAction(action) {
    const selectedIds = Array.from(document.querySelectorAll('.item-checkbox:checked'))
        .map(checkbox => checkbox.value);

    if (selectedIds.length === 0) {
        showToast('Advertencia', 'No hay elementos seleccionados', 'warning');
        return;
    }

    // TODO: Implementar acciones masivas vía AJAX
    console.log('Acción masiva:', action, 'IDs:', selectedIds);

    showToast('Procesando', `Aplicando acción a ${selectedIds.length} elementos`, 'info');
}

// ==================== EXPORT FUNCTIONS ====================
function exportToExcel(tableId, filename) {
    // TODO: Implementar exportación a Excel
    showToast('Exportando', 'Generando archivo Excel...', 'info');
}

function exportToPDF(reportType, filename) {
    // TODO: Implementar exportación a PDF
    showToast('Exportando', 'Generando archivo PDF...', 'info');
}

// ==================== UTILITY FUNCTIONS ====================
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP'
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== AJAX HELPERS ====================
function makeAjaxRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('AJAX Error:', error);
            showToast('Error', 'Ocurrió un error en la solicitud', 'danger');
            throw error;
        });
}

// ==================== KEYBOARD SHORTCUTS ====================
document.addEventListener('keydown', function (e) {
    // Ctrl+S o Cmd+S - Guardar
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        const saveButton = document.querySelector('button[type="submit"]');
        saveButton?.click();
    }

    // Esc - Cerrar modales
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            modal?.hide();
        }
    }
});

// ==================== AUTO-REFRESH ====================
let autoRefreshInterval = null;

function startAutoRefresh(seconds = 60) {
    stopAutoRefresh();
    autoRefreshInterval = setInterval(() => {
        location.reload();
    }, seconds * 1000);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// ==================== EXPORT ====================
window.AdminPanel = {
    showToast,
    confirmAction,
    confirmDelete,
    performBulkAction,
    exportToExcel,
    exportToPDF,
    makeAjaxRequest,
    formatCurrency,
    formatDate,
    startAutoRefresh,
    stopAutoRefresh
};

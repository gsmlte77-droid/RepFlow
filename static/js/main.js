/**
 * FixSoftRepair - Main JavaScript File
 * Handles common functionality across the application
 */

// Document Ready
$(document).ready(function() {
    // Initialize all components
    initSidebar();
    initUserMenu();
    initLanguageMenu();
    initMobileMenu();
    initFormValidation();
    initTooltips();
    initNotifications();
});

/**
 * Initialize Sidebar
 */
function initSidebar() {
    // Mobile sidebar toggle
    $('#sidebar-toggle, #mobile-menu-button').on('click', function() {
        $('#mobile-sidebar').toggleClass('hidden');
        $('body').toggleClass('overflow-hidden');
    });
    
    // Close mobile sidebar when clicking outside
    $('#mobile-sidebar').on('click', function(e) {
        if (e.target === this) {
            $(this).addClass('hidden');
            $('body').removeClass('overflow-hidden');
        }
    });
    
    // Active sidebar link
    const currentPath = window.location.pathname;
    $('.nav a').each(function() {
        const href = $(this).attr('href');
        if (currentPath.startsWith(href)) {
            $(this).addClass('bg-primary-50 text-primary-600');
        }
    });
}

/**
 * Initialize User Menu
 */
function initUserMenu() {
    $('#user-menu-toggle').on('click', function(e) {
        e.stopPropagation();
        $('#user-menu').toggleClass('hidden');
    });
    
    // Close user menu when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('#user-menu-toggle').length && !$(e.target).closest('#user-menu').length) {
            $('#user-menu').addClass('hidden');
        }
    });
}

/**
 * Initialize Language Menu
 */
function initLanguageMenu() {
    $('#language-toggle').on('click', function(e) {
        e.stopPropagation();
        $('#language-menu').toggleClass('hidden');
    });
    
    // Close language menu when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('#language-toggle').length && !$(e.target).closest('#language-menu').length) {
            $('#language-menu').addClass('hidden');
        }
    });
    
    // Handle language change
    $('#language-menu a').on('click', function(e) {
        e.preventDefault();
        const lang = $(this).attr('href').split('=')[1];
        setLanguage(lang);
    });
}

/**
 * Set Language
 */
function setLanguage(lang) {
    // Save to localStorage
    localStorage.setItem('language', lang);
    
    // Redirect with language parameter
    const currentUrl = window.location.href.split('?')[0];
    window.location.href = currentUrl + '?language=' + lang;
}

/**
 * Initialize Mobile Menu
 */
function initMobileMenu() {
    // Toggle mobile menu
    $('#mobile-menu-button').on('click', function() {
        $('#mobile-sidebar').toggleClass('hidden');
        $('body').toggleClass('overflow-hidden');
    });
}

/**
 * Initialize Form Validation
 */
function initFormValidation() {
    // Add required field indicators
    $('input[required], textarea[required], select[required]').each(function() {
        const label = $(this).closest('div').find('label');
        if (label.length && !label.find('.required').length) {
            label.append('<span class="required text-red-500 ml-1">*</span>');
        }
    });
    
    // Form submission handling
    $('form').on('submit', function(e) {
        // Validate form
        let isValid = true;
        
        $(this).find('input[required], textarea[required], select[required]').each(function() {
            if (!$(this).val().trim()) {
                isValid = false;
                $(this).addClass('border-red-500');
                $(this).closest('div').find('.error-message').remove();
                $(this).closest('div').append('<p class="error-message text-red-500 text-xs mt-1">{% trans "This field is required" %}</p>');
            } else {
                $(this).removeClass('border-red-500');
                $(this).closest('div').find('.error-message').remove();
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            // Scroll to first error
            const firstError = $(this).find('.border-red-500').first();
            if (firstError.length) {
                $('html, body').animate({
                    scrollTop: firstError.offset().top - 100
                }, 500);
            }
        }
    });
    
    // Clear error on input
    $('input, textarea, select').on('input change', function() {
        $(this).removeClass('border-red-500');
        $(this).closest('div').find('.error-message').remove();
    });
}

/**
 * Initialize Tooltips
 */
function initTooltips() {
    $('[data-tooltip]').each(function() {
        const tooltipText = $(this).attr('data-tooltip');
        $(this).hover(
            function() {
                $(this).append('<div class="tooltip">' + tooltipText + '</div>');
                const tooltip = $(this).find('.tooltip');
                tooltip.css({
                    'position': 'absolute',
                    'background': '#374151',
                    'color': '#fff',
                    'padding': '0.5rem',
                    'border-radius': '0.25rem',
                    'font-size': '0.75rem',
                    'white-space': 'nowrap',
                    'z-index': '50',
                    'top': $(this).offset().top - $(this).outerHeight() - 10,
                    'left': $(this).offset().left
                });
            },
            function() {
                $(this).find('.tooltip').remove();
            }
        );
    });
}

/**
 * Initialize Notifications
 */
function initNotifications() {
    // Request permission for notifications
    if ('Notification' in window) {
        Notification.requestPermission().then(function(permission) {
            if (permission === 'granted') {
                console.log('Notification permission granted');
            }
        });
    }
}

/**
 * Show Notification
 */
function showNotification(title, options = {}) {
    if ('Notification' in window) {
        new Notification(title, {
            body: options.body || '',
            icon: options.icon || '',
            dir: options.dir || 'auto'
        });
    }
}

/**
 * Show Toast Message
 */
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = $('#toast-container');
    
    if (!toastContainer.length) {
        $('body').append('<div id="toast-container" class="fixed top-4 right-4 z-50 space-y-2"></div>');
    }
    
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast p-4 rounded-lg shadow-lg flex items-center space-x-3 animate-fade-in">
            <i class="fas ${type === 'success' ? 'fa-check-circle text-green-500' : type === 'error' ? 'fa-exclamation-circle text-red-500' : type === 'warning' ? 'fa-exclamation-triangle text-yellow-500' : 'fa-info-circle text-blue-500'} text-xl"></i>
            <span class="text-sm">${message}</span>
            <button onclick="$('#${toastId}').remove()" class="text-gray-400 hover:text-gray-600">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    $('#toast-container').append(toastHtml);
    
    // Auto remove after duration
    setTimeout(function() {
        $('#' + toastId).fadeOut(300, function() {
            $(this).remove();
        });
    }, duration);
}

/**
 * Format Currency
 */
function formatCurrency(amount, currency = 'DZD') {
    const symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'DZD': 'د.ج',
        'MAD': 'د.م.',
        'TND': 'د.ت',
        'SAR': 'ر.س',
        'AED': 'د.إ',
        'QAR': 'ر.ق'
    };
    
    const symbol = symbols[currency] || currency;
    return symbol + ' ' + parseFloat(amount).toFixed(2);
}

/**
 * Format Date
 */
function formatDate(dateString, format = 'YYYY-MM-DD') {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    
    switch(format) {
        case 'YYYY-MM-DD':
            return `${year}-${month}-${day}`;
        case 'DD/MM/YYYY':
            return `${day}/${month}/${year}`;
        case 'MM/DD/YYYY':
            return `${month}/${day}/${year}`;
        default:
            return date.toLocaleDateString();
    }
}

/**
 * Format DateTime
 */
function formatDateTime(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleString();
}

/**
 * Truncate Text
 */
function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Debounce Function
 */
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

/**
 * Throttle Function
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Copy to Clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard', 'success');
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
    });
}

/**
 * Print Element
 */
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write('<html><head><title>Print</title></head><body>');
        printWindow.document.write(element.innerHTML);
        printWindow.document.write('</body></html>');
        printWindow.document.close();
        printWindow.print();
    }
}

/**
 * Export to CSV
 */
function exportToCSV(data, filename = 'export.csv') {
    let csv = '';
    
    // Add headers
    if (data.length > 0) {
        csv += Object.keys(data[0]).join(',') + '\n';
    }
    
    // Add rows
    data.forEach(row => {
        csv += Object.values(row).map(value => {
            if (typeof value === 'string' && value.includes(',')) {
                return '"' + value.replace(/"/g, '""') + '"';
            }
            return value;
        }).join(',') + '\n';
    });
    
    // Download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

/**
 * Export to PDF (using jsPDF)
 */
function exportToPDF(elementId, filename = 'export.pdf') {
    if (typeof jsPDF !== 'undefined') {
        const doc = new jsPDF();
        const element = document.getElementById(elementId);
        
        doc.html(element, {
            callback: function(doc) {
                doc.save(filename);
            },
            margin: [10, 10, 10, 10],
            autoPaging: 'text',
            x: 0,
            y: 0,
            width: 190,
            windowWidth: 675
        });
    } else {
        console.error('jsPDF is not loaded');
    }
}

/**
 * Confirm Action
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Show Modal
 */
function showModal(title, content, options = {}) {
    const modalId = 'modal-' + Date.now();
    const modalHtml = `
        <div id="${modalId}" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div class="bg-white rounded-xl shadow-lg max-w-md w-full max-h-screen overflow-y-auto">
                <div class="p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h2 class="text-xl font-semibold text-gray-800">${title}</h2>
                        <button onclick="$('#${modalId}').remove()" class="text-gray-400 hover:text-gray-600">
                            <i class="fas fa-times text-xl"></i>
                        </button>
                    </div>
                    <div class="mb-6">
                        ${content}
                    </div>
                    <div class="flex items-center justify-end space-x-3">
                        ${options.buttons || ''}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    $('#modal-container').append(modalHtml);
    
    // Close on outside click
    $('#' + modalId).on('click', function(e) {
        if (e.target === this) {
            $(this).remove();
        }
    });
    
    return modalId;
}

/**
 * Close Modal
 */
function closeModal(modalId) {
    $('#' + modalId).remove();
}

/**
 * Toggle Theme (Dark/Light)
 */
function toggleTheme() {
    const body = $('body');
    const currentTheme = body.attr('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    body.attr('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    if (newTheme === 'dark') {
        body.addClass('dark');
    } else {
        body.removeClass('dark');
    }
}

/**
 * Initialize Theme
 */
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const body = $('body');
    
    body.attr('data-theme', savedTheme);
    
    if (savedTheme === 'dark') {
        body.addClass('dark');
    }
}

// Initialize theme on load
initTheme();

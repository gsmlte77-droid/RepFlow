/**
 * FixSoftRepair - AJAX JavaScript File
 * Handles all AJAX interactions for the application
 */

// CSRF Token Setup
function getCSRFToken() {
    return $('meta[name="csrf-token"]').attr('content');
}

// AJAX Setup
$.ajaxSetup({
    headers: {
        'X-CSRFToken': getCSRFToken(),
        'X-Requested-With': 'XMLHttpRequest'
    }
});

/**
 * Authentication AJAX Functions
 */

// Login via AJAX
function ajaxLogin(username, password, rememberMe = false, callback) {
    $.ajax({
        url: '/accounts/api/login/',
        type: 'POST',
        data: JSON.stringify({
            username: username,
            password: password,
            remember_me: rememberMe
        }),
        contentType: 'application/json',
        success: function(response) {
            if (response.success) {
                if (typeof callback === 'function') {
                    callback(response);
                } else {
                    window.location.href = response.redirect || '/dashboard/';
                }
            } else {
                showToast(response.error || 'Login failed', 'error');
            }
        },
        error: function(xhr, status, error) {
            showToast('Login failed: ' + error, 'error');
        }
    });
}

// Logout via AJAX
function ajaxLogout(callback) {
    $.ajax({
        url: '/accounts/api/logout/',
        type: 'POST',
        success: function(response) {
            if (response.success && typeof callback === 'function') {
                callback(response);
            } else {
                window.location.href = '/accounts/login/';
            }
        },
        error: function(xhr, status, error) {
            showToast('Logout failed: ' + error, 'error');
        }
    });
}

// Check username availability
function checkUsernameAvailability(username, callback) {
    $.ajax({
        url: '/accounts/api/check-username/',
        type: 'GET',
        data: { username: username },
        success: function(response) {
            callback(response.available);
        },
        error: function() {
            callback(false);
        }
    });
}

/**
 * Client AJAX Functions
 */

// Search clients
function searchClients(query, limit = 10, callback) {
    $.ajax({
        url: '/clients/api/search/',
        type: 'GET',
        data: { search: query, limit: limit },
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Search clients error:', error);
            callback([]);
        }
    });
}

// Get client details
function getClient(clientId, callback) {
    $.ajax({
        url: '/clients/api/' + clientId + '/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get client error:', error);
            callback(null);
        }
    });
}

// Get client balance
function getClientBalance(clientId, callback) {
    $.ajax({
        url: '/clients/api/' + clientId + '/balance/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get client balance error:', error);
            callback(null);
        }
    });
}

// Quick add client
function quickAddClient(clientData, callback) {
    $.ajax({
        url: '/clients/api/quick-add/',
        type: 'POST',
        data: JSON.stringify(clientData),
        contentType: 'application/json',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Quick add client error:', error);
            callback({ success: false, error: error });
        }
    });
}

/**
 * Inventory AJAX Functions
 */

// Search inventory items
function searchInventory(query, limit = 10, callback) {
    $.ajax({
        url: '/inventory/api/search/',
        type: 'GET',
        data: { search: query, limit: limit },
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Search inventory error:', error);
            callback([]);
        }
    });
}

// Get inventory item details
function getInventoryItem(itemId, callback) {
    $.ajax({
        url: '/inventory/api/' + itemId + '/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get inventory item error:', error);
            callback(null);
        }
    });
}

// Update inventory stock
function updateInventoryStock(itemId, quantity, operation = 'add', notes = '', callback) {
    $.ajax({
        url: '/inventory/api/' + itemId + '/stock/',
        type: 'POST',
        data: JSON.stringify({
            quantity: quantity,
            operation: operation,
            notes: notes
        }),
        contentType: 'application/json',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Update inventory stock error:', error);
            callback({ success: false, error: error });
        }
    });
}

// Get low stock items
function getLowStockItems(callback) {
    $.ajax({
        url: '/inventory/api/low-stock/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get low stock items error:', error);
            callback([]);
        }
    });
}

// Get inventory statistics
function getInventoryStats(callback) {
    $.ajax({
        url: '/inventory/api/stats/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get inventory stats error:', error);
            callback(null);
        }
    });
}

/**
 * Repair AJAX Functions
 */

// Search repairs
function searchRepairs(query, limit = 10, callback) {
    $.ajax({
        url: '/repairs/api/search/',
        type: 'GET',
        data: { search: query, limit: limit },
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Search repairs error:', error);
            callback([]);
        }
    });
}

// Get repair ticket details
function getRepairTicket(ticketId, callback) {
    $.ajax({
        url: '/repairs/api/' + ticketId + '/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get repair ticket error:', error);
            callback(null);
        }
    });
}

// Update repair ticket status
function updateRepairStatus(ticketId, status, notes = '', callback) {
    $.ajax({
        url: '/repairs/api/' + ticketId + '/status/',
        type: 'POST',
        data: JSON.stringify({
            status: status,
            notes: notes
        }),
        contentType: 'application/json',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Update repair status error:', error);
            callback({ success: false, error: error });
        }
    });
}

// Get repair statistics
function getRepairStats(callback) {
    $.ajax({
        url: '/repairs/api/stats/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get repair stats error:', error);
            callback(null);
        }
    });
}

// Quick create repair ticket
function quickCreateRepair(repairData, callback) {
    $.ajax({
        url: '/repairs/api/quick-create/',
        type: 'POST',
        data: JSON.stringify(repairData),
        contentType: 'application/json',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Quick create repair error:', error);
            callback({ success: false, error: error });
        }
    });
}

// Get repair history
function getRepairHistory(ticketId, callback) {
    $.ajax({
        url: '/repairs/api/' + ticketId + '/history/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get repair history error:', error);
            callback([]);
        }
    });
}

/**
 * Billing AJAX Functions
 */

// Search invoices
function searchInvoices(query, limit = 10, callback) {
    $.ajax({
        url: '/billing/api/invoices/search/',
        type: 'GET',
        data: { search: query, limit: limit },
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Search invoices error:', error);
            callback([]);
        }
    });
}

// Get invoice details
function getInvoice(invoiceId, callback) {
    $.ajax({
        url: '/billing/api/invoices/' + invoiceId + '/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get invoice error:', error);
            callback(null);
        }
    });
}

// Get invoice statistics
function getInvoiceStats(callback) {
    $.ajax({
        url: '/billing/api/invoices/stats/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get invoice stats error:', error);
            callback(null);
        }
    });
}

// Update invoice status
function updateInvoiceStatus(invoiceId, status, callback) {
    $.ajax({
        url: '/billing/api/invoices/' + invoiceId + '/status/',
        type: 'PATCH',
        data: JSON.stringify({ status: status }),
        contentType: 'application/json',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Update invoice status error:', error);
            callback({ success: false, error: error });
        }
    });
}

// Add payment to invoice
function addPayment(invoiceId, paymentData, callback) {
    paymentData.invoice_id = invoiceId;
    
    $.ajax({
        url: '/billing/api/payments/add/',
        type: 'POST',
        data: JSON.stringify(paymentData),
        contentType: 'application/json',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Add payment error:', error);
            callback({ success: false, error: error });
        }
    });
}

// Get client invoices
function getClientInvoices(clientId, callback) {
    $.ajax({
        url: '/billing/api/clients/' + clientId + '/invoices/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get client invoices error:', error);
            callback([]);
        }
    });
}

// Get client balance
function getClientBillingBalance(clientId, callback) {
    $.ajax({
        url: '/billing/api/clients/' + clientId + '/balance/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get client balance error:', error);
            callback(null);
        }
    });
}

/**
 * Dashboard AJAX Functions
 */

// Get dashboard statistics
function getDashboardStats(callback) {
    $.ajax({
        url: '/dashboard/api/stats/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get dashboard stats error:', error);
            callback(null);
        }
    });
}

// Get dashboard repairs
function getDashboardRepairs(callback) {
    $.ajax({
        url: '/dashboard/api/repairs/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get dashboard repairs error:', error);
            callback([]);
        }
    });
}

// Get dashboard financial data
function getDashboardFinancial(callback) {
    $.ajax({
        url: '/dashboard/api/financial/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get dashboard financial error:', error);
            callback(null);
        }
    });
}

// Get dashboard inventory data
function getDashboardInventory(callback) {
    $.ajax({
        url: '/dashboard/api/inventory/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get dashboard inventory error:', error);
            callback(null);
        }
    });
}

/**
 * Staff AJAX Functions
 */

// Get staff by department
function getStaffByDepartment(department, callback) {
    $.ajax({
        url: '/staff/api/department/' + department + '/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get staff by department error:', error);
            callback([]);
        }
    });
}

// Get staff statistics
function getStaffStats(callback) {
    $.ajax({
        url: '/staff/api/stats/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get staff stats error:', error);
            callback(null);
        }
    });
}

/**
 * Configuration AJAX Functions
 */

// Get configuration
function getConfig(callback) {
    $.ajax({
        url: '/config/api/get/',
        type: 'GET',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Get config error:', error);
            callback(null);
        }
    });
}

// Update configuration
function updateConfig(configData, callback) {
    $.ajax({
        url: '/config/api/update/',
        type: 'POST',
        data: JSON.stringify(configData),
        contentType: 'application/json',
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('Update config error:', error);
            callback({ success: false, error: error });
        }
    });
}

/**
 * Global Search Functionality
 */

// Initialize global search
function initGlobalSearch() {
    const searchInput = $('#global-search');
    const searchResults = $('#search-results');
    
    if (!searchInput.length) return;
    
    // Create results container
    if (!searchResults.length) {
        searchInput.after('<div id="search-results" class="absolute top-full left-0 right-0 bg-white shadow-lg border rounded-lg mt-2 z-50 hidden"></div>');
    }
    
    // Debounced search
    const debouncedSearch = debounce(function(query) {
        if (query.length < 2) {
            searchResults.addClass('hidden');
            return;
        }
        
        // Search across multiple models
        searchClients(query, 5, function(clients) {
            searchRepairs(query, 5, function(repairs) {
                searchInventory(query, 5, function(items) {
                    displaySearchResults(clients, repairs, items, query);
                });
            });
        });
    }, 300);
    
    searchInput.on('input', function() {
        const query = $(this).val().trim();
        debouncedSearch(query);
    });
    
    // Close results when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('#global-search').length && !$(e.target).closest('#search-results').length) {
            searchResults.addClass('hidden');
        }
    });
}

// Display search results
function displaySearchResults(clients, repairs, items, query) {
    const searchResults = $('#search-results');
    
    let html = '<div class="p-4 max-h-96 overflow-y-auto">';
    
    // Clients
    if (clients.length > 0) {
        html += '<div class="mb-4">';
        html += '<h3 class="text-sm font-semibold text-gray-800 mb-2">{% trans "Clients" %}</h3>';
        html += '<div class="space-y-2">';
        clients.forEach(client => {
            html += '<a href="/clients/' + client.id + '/" class="block p-2 rounded-lg hover:bg-gray-50">';
            html += '<div class="font-medium text-gray-800">' + client.name + '</div>';
            html += '<div class="text-sm text-gray-500">' + client.telephone + '</div>';
            html += '</a>';
        });
        html += '</div></div>';
    }
    
    // Repairs
    if (repairs.length > 0) {
        html += '<div class="mb-4">';
        html += '<h3 class="text-sm font-semibold text-gray-800 mb-2">{% trans "Repairs" %}</h3>';
        html += '<div class="space-y-2">';
        repairs.forEach(repair => {
            html += '<a href="/repairs/' + repair.id + '/" class="block p-2 rounded-lg hover:bg-gray-50">';
            html += '<div class="font-medium text-gray-800">' + repair.ticket_number + ' - ' + repair.device + '</div>';
            html += '<div class="text-sm text-gray-500">' + repair.client_name + '</div>';
            html += '</a>';
        });
        html += '</div></div>';
    }
    
    // Inventory
    if (items.length > 0) {
        html += '<div class="mb-4">';
        html += '<h3 class="text-sm font-semibold text-gray-800 mb-2">{% trans "Inventory" %}</h3>';
        html += '<div class="space-y-2">';
        items.forEach(item => {
            html += '<a href="/inventory/' + item.id + '/" class="block p-2 rounded-lg hover:bg-gray-50">';
            html += '<div class="font-medium text-gray-800">' + item.name + '</div>';
            html += '<div class="text-sm text-gray-500">' + item.reference_sku + ' - Stock: ' + item.stock + '</div>';
            html += '</a>';
        });
        html += '</div></div>';
    }
    
    if (clients.length === 0 && repairs.length === 0 && items.length === 0) {
        html += '<div class="p-4 text-center text-gray-500">{% trans "No results found" %}</div>';
    }
    
    html += '</div>';
    
    searchResults.html(html).removeClass('hidden');
}

// Initialize global search on document ready
$(document).ready(function() {
    initGlobalSearch();
});

/**
 * Real-time Updates
 */

// Start real-time updates
function startRealTimeUpdates(interval = 30000) {
    // Update dashboard stats
    setInterval(function() {
        getDashboardStats(function(stats) {
            // Update stats in the UI
            updateDashboardStats(stats);
        });
    }, interval);
    
    // Update notifications
    setInterval(function() {
        // Check for new notifications
        checkNewNotifications();
    }, interval);
}

// Update dashboard stats in UI
function updateDashboardStats(stats) {
    // Update total repairs
    if ($('#total-repairs').length) {
        $('#total-repairs').text(stats.total_repairs);
    }
    
    // Update total clients
    if ($('#total-clients').length) {
        $('#total-clients').text(stats.total_clients);
    }
    
    // Update total revenue
    if ($('#total-revenue').length) {
        $('#total-revenue').text(formatCurrency(stats.total_revenue));
    }
    
    // Update outstanding balance
    if ($('#total-outstanding').length) {
        $('#total-outstanding').text(formatCurrency(stats.total_outstanding));
    }
    
    // Update overdue invoices
    if ($('#overdue-invoices').length) {
        $('#overdue-invoices').text(stats.overdue_invoices);
    }
}

// Check for new notifications
function checkNewNotifications() {
    // Implement notification checking logic
    // This would typically call an API endpoint to check for new notifications
}

/**
 * WebSocket Support (if available)
 */

// Initialize WebSocket connection
function initWebSocket() {
    if (window.WebSocket) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const socketUrl = protocol + '//' + window.location.host + '/ws/notifications/';
        
        try {
            const socket = new WebSocket(socketUrl);
            
            socket.onopen = function(e) {
                console.log('WebSocket connection established');
            };
            
            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };
            
            socket.onclose = function(event) {
                if (event.wasClean) {
                    console.log('WebSocket connection closed cleanly');
                } else {
                    console.log('WebSocket connection closed unexpectedly');
                }
                // Attempt to reconnect
                setTimeout(initWebSocket, 5000);
            };
            
            socket.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
            
            return socket;
        } catch (error) {
            console.error('WebSocket connection error:', error);
            return null;
        }
    }
    return null;
}

// Handle WebSocket message
function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'notification':
            showToast(data.message, data.level || 'info');
            break;
        case 'repair_update':
            // Update repair in UI
            break;
        case 'invoice_update':
            // Update invoice in UI
            break;
        case 'inventory_update':
            // Update inventory in UI
            break;
        default:
            console.log('Unknown WebSocket message type:', data.type);
    }
}

/**
 * Error Handling
 */

// Global AJAX error handler
$(document).ajaxError(function(event, xhr, settings, thrownError) {
    if (xhr.status === 401) {
        // Unauthorized - redirect to login
        window.location.href = '/accounts/login/';
    } else if (xhr.status === 403) {
        // Forbidden - show error
        showToast('You do not have permission to perform this action', 'error');
    } else if (xhr.status === 404) {
        // Not found
        showToast('Resource not found', 'error');
    } else if (xhr.status >= 500) {
        // Server error
        showToast('A server error occurred. Please try again later.', 'error');
    } else {
        // Other errors
        showToast('An error occurred: ' + thrownError, 'error');
    }
});

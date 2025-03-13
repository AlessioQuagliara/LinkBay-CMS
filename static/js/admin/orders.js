// ➕ CREAZIONE ------------------------------------------------------------------------------------------------
    document.getElementById('add-order-btn').addEventListener('click', function () {
        const orderData = {
            order_number: `ORD-${Date.now()}`, // Genera un numero di ordine unico
            total_amount: 0, // Valore iniziale (può essere aggiornato)
            status: 'Draft', // Stato iniziale (1 = Pending)
            customer_id: null // Assicurati che sia null se non specificato
        };
    
        console.log("Sending order data:", orderData); // Log dei dati inviati
    
        Swal.fire({
            title: 'Creating Order...',
            text: 'Please wait while the order is being created.',
            icon: 'info',
            allowOutsideClick: false,
            showConfirmButton: false,
            didOpen: () => Swal.showLoading()
        });
    
        fetch('/api/create_order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData)
        })
            .then(response => response.json())
            .then(data => {
                Swal.close();
                console.log("Response from server:", data); // Log della risposta del server
                if (data.success) {
                    Swal.fire('Success!', 'Order created successfully!', 'success').then(() => {
                        window.location.href = `/admin/cms/pages/order/${data.order_id}`;
                    });
                } else {
                    Swal.fire('Error!', data.message || 'Failed to create order.', 'error');
                }
            })
            .catch(error => {
                console.error("Fetch error:", error); // Log dell'errore di rete
                Swal.fire('Error!', 'A network error occurred.', 'error');
            });
    });

// 🗑️ CANCELLAZIONE ------------------------------------------------------------------------------------------------
        document.querySelector('.delete-selected').addEventListener('click', function () {
            const selectedRows = document.querySelectorAll('.row-checkbox:checked');
            if (selectedRows.length === 0) {
                Swal.fire('No Selection', 'Please select at least one order to delete.', 'warning');
                return;
            }
    
            const orderIds = Array.from(selectedRows).map(row => 
                row.closest('.table-row').getAttribute('data-order-id')
            );
    
            Swal.fire({
                title: 'Are you sure?',
                text: "This action will permanently delete the selected orders.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, delete them!'
            }).then((result) => {
                if (result.isConfirmed) {
                    Swal.fire({
                        title: 'Deleting...',
                        text: 'Please wait while the orders are being deleted.',
                        icon: 'info',
                        allowOutsideClick: false,
                        showConfirmButton: false,
                        didOpen: () => Swal.showLoading()
                    });
    
                    fetch('/api/delete_orders', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ order_ids: orderIds })
                    })
                    .then(response => response.json())
                    .then(data => {
                        Swal.close();
                        if (data.success) {
                            Swal.fire('Deleted!', data.message, 'success').then(() => {
                                orderIds.forEach(id => {
                                    document.querySelector(`.table-row[data-order-id="${id}"]`).remove();
                                });
                            });
                        } else {
                            Swal.fire('Error!', data.message || 'Failed to delete orders.', 'error');
                        }
                    })
                    .catch(error => {
                        Swal.fire('Error!', 'A network error occurred.', 'error');
                        console.error('Error:', error);
                    });
                }
            });
        });

// 🖱️ LOGICA DOPPIO CLICK ------------------------------------------------------------------------------------------------

        document.addEventListener('DOMContentLoaded', function () {
            const tableRows = document.querySelectorAll('.table-row');
            tableRows.forEach(row => {
                row.addEventListener('dblclick', function () {
                    const orderId = this.getAttribute('data-order-id');
                    if (orderId) {
                        window.location.href = `/admin/cms/pages/order/${orderId}`;
                    }
                });
            });
        });


// ☑️ MULTISELEZIONE ------------------------------------------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', function () {
        const tableRows = document.querySelectorAll('.table-row');
        let isMouseDown = false;

        tableRows.forEach(row => {
            row.addEventListener('mousedown', function(event) {
                isMouseDown = true;
                toggleRowSelection(this);
                event.preventDefault();
            });

            row.addEventListener('mouseover', function() {
                if (isMouseDown) {
                    toggleRowSelection(this);
                }
            });
        });

        document.addEventListener('mouseup', function() {
            isMouseDown = false;
        });

        function toggleRowSelection(row) {
            const checkbox = row.querySelector('.row-checkbox');
            checkbox.checked = !checkbox.checked;
            row.classList.toggle('table-active', checkbox.checked);
        }

        document.querySelector('.select-all').addEventListener('click', function() {
            const allChecked = Array.from(tableRows).every(row => row.querySelector('.row-checkbox').checked);
            tableRows.forEach(row => {
                const checkbox = row.querySelector('.row-checkbox');
                checkbox.checked = !allChecked;
                row.classList.toggle('table-active', checkbox.checked);
            });
        });

        document.getElementById('select-all-checkbox').addEventListener('change', function() {
            const isChecked = this.checked;
            tableRows.forEach(row => {
                const checkbox = row.querySelector('.row-checkbox');
                checkbox.checked = isChecked;
                row.classList.toggle('table-active', isChecked);
            });
        });
    });

// 😍 PREFERENZE TABELLA ------------------------------------------------------------------------------------------------

    document.addEventListener('DOMContentLoaded', function () {
        const columnsContainer = document.getElementById('columns-container');
        const tablePreferencesKey = 'ordersTablePreferences'; // Chiave unica per LocalStorage
    
        const columns = [
            { value: 'id', label: '#' },
            { value: 'order_number', label: 'Order Number', default: true },
            { value: 'customer_name', label: 'Customer Name', default: true },
            { value: 'customer_email', label: 'Customer Email', default: true },
            { value: 'total_items', label: 'Total Items', default: true },
            { value: 'total_quantity', label: 'Total Quantity', default: true },
            { value: 'total_amount', label: 'Total Amount', default: true },
            { value: 'status', label: 'Status', default: true },
            { value: 'created_at', label: 'Created At', default: true },
            { value: 'updated_at', label: 'Updated At', default: true }
        ];
    
        function renderColumnOptions(preferences) {
            columnsContainer.innerHTML = '';
            columns.forEach(column => {
                const isChecked = preferences[column.value] ?? column.default;
                columnsContainer.innerHTML += `
                    <div class="form-check">
                        <input class="form-check-input column-toggle" type="checkbox" value="${column.value}" id="column-${column.value}" ${isChecked ? 'checked' : ''}>
                        <label class="form-check-label" for="column-${column.value}">${column.label}</label>
                    </div>`;
            });
        }
    
        function savePreferences() {
            const preferences = {};
            document.querySelectorAll('.column-toggle').forEach(toggle => {
                preferences[toggle.value] = toggle.checked;
            });
            localStorage.setItem(tablePreferencesKey, JSON.stringify(preferences));
            applyPreferences(preferences);
        }
    
        function loadPreferences() {
            const preferences = JSON.parse(localStorage.getItem(tablePreferencesKey)) || {};
            renderColumnOptions(preferences);
            applyPreferences(preferences);
        }
    
        function applyPreferences(preferences) {
            columns.forEach(column => {
                const isChecked = preferences[column.value] ?? column.default;
                const header = document.querySelector(`thead th.${column.value}`);
                if (header) {
                    header.style.display = isChecked ? '' : 'none';
                }
                document.querySelectorAll(`tbody td.${column.value}`).forEach(cell => {
                    cell.style.display = isChecked ? '' : 'none';
                });
            });
        }
    
        // Event Listener per il salvataggio automatico
        columnsContainer.addEventListener('change', function (event) {
            if (event.target.classList.contains('column-toggle')) {
                savePreferences(); // Salva automaticamente al cambio
            }
        });
    
        loadPreferences(); // Carica le preferenze all'avvio
    });
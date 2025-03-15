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
    const columnsContainer = document.getElementById('sortable-columns');
    const tablePreferencesKey = 'ordersTablePreferences'; // Chiave unica per LocalStorage

    const columns = [
        { value: 'id', label: 'ID' },
        { value: 'order_number', label: 'Order Number' },
        { value: 'customer_name', label: 'Customer Name' },
        { value: 'customer_email', label: 'Customer Email' },
        { value: 'total_items', label: 'Total Items' },
        { value: 'total_quantity', label: 'Total Quantity' },
        { value: 'total_amount', label: 'Total Amount' },
        { value: 'status', label: 'Status' },
        { value: 'created_at', label: 'Created At' },
        { value: 'updated_at', label: 'Updated At' }
    ];

    function renderColumnOptions(preferences) {
        columnsContainer.innerHTML = '';

        // Usa l'ordine salvato nelle preferenze, altrimenti l'ordine di default
        const orderedColumns = preferences.order || columns.map(col => col.value);

        orderedColumns.forEach(columnValue => {
            const column = columns.find(col => col.value === columnValue);
            if (!column) return; // Skip se la colonna non esiste

            const isChecked = preferences[column.value] ?? true;
            const columnItem = document.createElement('div');
            columnItem.classList.add('list-group-item', 'd-flex', 'align-items-center');
            columnItem.dataset.column = column.value;
            columnItem.innerHTML = `
                <i class="fa-solid fa-grip-lines me-2"></i>
                <input class="form-check-input column-toggle me-2" type="checkbox" value="${column.value}" ${isChecked ? 'checked' : ''}>
                <label class="form-check-label flex-grow-1">${column.label}</label>
            `;
            columnsContainer.appendChild(columnItem);
        });

        // Aggiunge il listener per aggiornare la vista automaticamente
        document.querySelectorAll('.column-toggle').forEach(toggle => {
            toggle.addEventListener('change', function () {
                savePreferences();
                applyPreferences(loadPreferences());
            });
        });

        // Rendi il contenitore delle colonne ordinabile
        new Sortable(columnsContainer, {
            animation: 150,
            ghostClass: 'sortable-ghost',
            onEnd: function () {
                savePreferences(); // Salva il nuovo ordine
                applyPreferences(loadPreferences());
            }
        });
    }

    function savePreferences() {
        const preferences = { order: [] };
        document.querySelectorAll('#sortable-columns .list-group-item').forEach(item => {
            const columnValue = item.dataset.column;
            const checkbox = item.querySelector('.column-toggle');
            preferences[columnValue] = checkbox.checked;
            preferences.order.push(columnValue);
        });
        localStorage.setItem(tablePreferencesKey, JSON.stringify(preferences));
    }

    function loadPreferences() {
        return JSON.parse(localStorage.getItem(tablePreferencesKey)) || {};
    }

    function applyPreferences(preferences) {
        const orderedColumns = preferences.order || columns.map(col => col.value);

        // Riordina le colonne nella tabella
        const tableHeadRow = document.querySelector('thead tr');
        const tableBodyRows = document.querySelectorAll('tbody tr');

        orderedColumns.forEach(columnValue => {
            const header = tableHeadRow.querySelector(`th.${columnValue}`);
            if (header) tableHeadRow.appendChild(header);

            tableBodyRows.forEach(row => {
                const cell = row.querySelector(`td.${columnValue}`);
                if (cell) row.appendChild(cell);
            });
        });

        // Nasconde/mostra le colonne in base alle preferenze
        columns.forEach(column => {
            const isChecked = preferences[column.value] ?? true;
            const header = document.querySelector(`thead th.${column.value}`);
            if (header) {
                header.style.display = isChecked ? '' : 'none';
            }
            document.querySelectorAll(`tbody td.${column.value}`).forEach(cell => {
                cell.style.display = isChecked ? '' : 'none';
            });
        });
    }

    // Inizializzazione
    const savedPreferences = loadPreferences();
    renderColumnOptions(savedPreferences);
    applyPreferences(savedPreferences);
});
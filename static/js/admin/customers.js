// 😍 PREFERENZE TABELLA ------------------------------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', function () {
    const columnsContainer = document.getElementById('columns-container');
    const tablePreferencesKey = 'customersTablePreferences';

    const columns = [
        { value: 'id', label: '#' },
        { value: 'first_name', label: 'First Name' },
        { value: 'last_name', label: 'Last Name' },
        { value: 'email', label: 'Email' },
        { value: 'phone', label: 'Phone' },
        { value: 'address', label: 'Address' },
        { value: 'city', label: 'City' },
        { value: 'state', label: 'State' },
        { value: 'postal_code', label: 'Postal Code' },
        { value: 'country', label: 'Country' },
        { value: 'created_at', label: 'Created At' },
        { value: 'updated_at', label: 'Updated At' }
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

        // Aggiunge il listener per aggiornare la vista automaticamente
        document.querySelectorAll('.column-toggle').forEach(toggle => {
            toggle.addEventListener('change', function () {
                savePreferences();
                applyPreferences(loadPreferences());
            });
        });
    }

    function savePreferences() {
        const preferences = {};
        document.querySelectorAll('.column-toggle').forEach(toggle => {
            preferences[toggle.value] = toggle.checked;
        });
        localStorage.setItem(tablePreferencesKey, JSON.stringify(preferences));
    }

    function loadPreferences() {
        return JSON.parse(localStorage.getItem(tablePreferencesKey)) || {};
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

    // Carica le preferenze salvate e aggiorna la vista all'avvio
    const savedPreferences = loadPreferences();
    renderColumnOptions(savedPreferences);
    applyPreferences(savedPreferences);
});


// 🖱️ LOGICA DOPPIO CLICK ------------------------------------------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', function () {
        const tableRows = document.querySelectorAll('.table-row');
        tableRows.forEach(row => {
            row.addEventListener('dblclick', function () {
                const customerId = this.getAttribute('data-customer-id');
                if (customerId) {
                    window.location.href = `/admin/cms/pages/customer/${customerId}`;
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



// ➕ CREAZIONE ------------------------------------------------------------------------------------------------
    document.getElementById('add-customer-btn').addEventListener('click', function () {
        Swal.fire({
            title: 'Creating customer...',
            text: 'Please wait while the new customer is being created.',
            icon: 'info',
            allowOutsideClick: false,
            showConfirmButton: false,
            didOpen: () => Swal.showLoading()
        });

        fetch('/api/create_customer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        })
        .then(response => response.json())
        .then(data => {
            Swal.close();
            if (data.success) {
                Swal.fire({
                    title: 'Success!',
                    text: data.message,
                    icon: 'success'
                }).then(() => {
                    window.location.href = `/admin/cms/pages/customer/${data.customer_id}`;
                });
            } else {
                Swal.fire('Error!', data.message, 'error');
            }
        })
        .catch(error => {
            Swal.fire('Error!', 'A network error occurred.', 'error');
            console.error('Error:', error);
        });
    });



// 🗑️ CANCELLAZIONE ------------------------------------------------------------------------------------------------
    document.querySelector('.delete-selected').addEventListener('click', function () {
        const selectedRows = document.querySelectorAll('.row-checkbox:checked');
        if (selectedRows.length === 0) {
            Swal.fire('No Selection', 'Please select at least one customer to delete.', 'warning');
            return;
        }

        const customerIds = Array.from(selectedRows).map(row => 
            row.closest('.table-row').getAttribute('data-customer-id')
        );

        Swal.fire({
            title: 'Are you sure?',
            text: "This action will permanently delete the selected customers.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete them!'
        }).then((result) => {
            if (result.isConfirmed) {
                Swal.fire({
                    title: 'Deleting...',
                    text: 'Please wait while the customers are being deleted.',
                    icon: 'info',
                    allowOutsideClick: false,
                    showConfirmButton: false,
                    didOpen: () => Swal.showLoading()
                });

                fetch('/api/delete_customers', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ customer_ids: customerIds })
                })
                .then(response => response.json())
                .then(data => {
                    Swal.close();
                    if (data.success) {
                        Swal.fire('Deleted!', data.message, 'success').then(() => {
                            customerIds.forEach(id => {
                                document.querySelector(`.table-row[data-customer-id="${id}"]`).remove();
                            });
                        });
                    } else {
                        Swal.fire('Error!', data.message || 'Failed to delete customers.', 'error');
                    }
                })
                .catch(error => {
                    Swal.fire('Error!', 'A network error occurred.', 'error');
                    console.error('Error:', error);
                });
            }
        });
    });


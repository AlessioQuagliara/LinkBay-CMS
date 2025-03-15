document.addEventListener('DOMContentLoaded', function () {
    const searchToggleBtn = document.getElementById('search-toggle-btn');
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const searchResultsList = document.getElementById('search-results-list');

    // Anima la barra di ricerca
    searchToggleBtn.addEventListener('click', function () {
        searchInput.classList.toggle('d-none');
        searchInput.focus();
    });

    searchInput.addEventListener('input', function () {
        const query = searchInput.value.trim();
        if (query.length > 2) {
            fetchOrders(query);
        } else {
            searchResults.style.display = 'none'; // Nasconde il dropdown se non c’è ricerca
        }
    });

    function fetchOrders(searchTerm) {
        fetch(`/api/orders/search?order_number=${encodeURIComponent(searchTerm)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateDropdown(data.orders);
                } else {
                    searchResultsList.innerHTML = `<div class="dropdown-item text-danger">Errore nella ricerca</div>`;
                    searchResults.style.display = 'block';
                }
            })
            .catch(error => {
                searchResultsList.innerHTML = `<div class="dropdown-item text-danger">Errore nella richiesta</div>`;
                searchResults.style.display = 'block';
                console.error("Errore API:", error);
            });
    }

    function updateDropdown(orders) {
        searchResultsList.innerHTML = ''; // Pulisce i risultati precedenti

        if (orders.length === 0) {
            searchResultsList.innerHTML = `<div class="dropdown-item text-muted">Nessun ordine trovato</div>`;
        } else {
            orders.forEach(order => {
                const item = document.createElement('div');
                item.classList.add('dropdown-item', 'cursor-pointer');
                item.innerHTML = `<strong>#${order.order_number}</strong> <br> - ${order.status} <br> (€${order.total_amount.toFixed(2)})`;

                // Evento per selezionare l'ordine e reindirizzare alla pagina dell'ordine
                item.addEventListener('click', function () {
                    window.location.href = `/admin/cms/pages/order/${order.id}`;
                });

                searchResultsList.appendChild(item);
            });
        }

        searchResults.style.display = 'block'; // Mostra il dropdown
    }

    // Nasconde il dropdown se si clicca fuori
    document.addEventListener('click', function (event) {
        if (!searchResults.contains(event.target) && event.target !== searchInput) {
            searchResults.style.display = 'none';
        }
    });
});


document.addEventListener('DOMContentLoaded', function () {
    const filterBtn = document.getElementById('filter-orders-btn');
    const filterForm = document.getElementById('filter-form');

    // Apri il modale quando si clicca sul pulsante del filtro
    filterBtn.addEventListener('click', function () {
        const modal = new bootstrap.Modal(document.getElementById('filter-modal'));
        modal.show();
    });

    // Applica i filtri al submit
    filterForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Evita il reload della pagina

        const status = document.getElementById('status-filter').value;
        const amount = document.getElementById('amount-filter').value;
        const date = document.getElementById('date-filter').value;

        let queryParams = [];
        if (status) queryParams.push(`status=${encodeURIComponent(status)}`);
        if (amount) queryParams.push(`amount=${encodeURIComponent(amount)}`);
        if (date) queryParams.push(`created_at=${encodeURIComponent(date)}`);

        const queryString = queryParams.length > 0 ? '?' + queryParams.join('&') : '';

        // Ricarica la pagina con i filtri applicati
        window.location.href = `/admin/cms/pages/orders${queryString}`;
    });
});
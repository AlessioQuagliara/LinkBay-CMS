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
            fetchCustomers(query);
        } else {
            searchResults.style.display = 'none'; // Nasconde il dropdown se non c’è ricerca
        }
    });

    function fetchCustomers(searchTerm) {
        fetch(`/api/customers/search?query=${encodeURIComponent(searchTerm)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateDropdown(data.customers);
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

    function updateDropdown(customers) {
        searchResultsList.innerHTML = ''; // Pulisce i risultati precedenti

        if (customers.length === 0) {
            searchResultsList.innerHTML = `<div class="dropdown-item text-muted">Nessun cliente trovato</div>`;
        } else {
            customers.forEach(customer => {
                const item = document.createElement('div');
                item.classList.add('dropdown-item', 'cursor-pointer');
                item.innerHTML = `<strong>${customer.first_name}</strong> <br> - ${customer.email}`;

                // Evento per selezionare il cliente e reindirizzare alla sua pagina
                item.addEventListener('click', function () {
                    window.location.href = `/admin/cms/pages/customer/${customer.id}`;
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
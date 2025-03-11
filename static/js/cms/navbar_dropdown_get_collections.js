       // DROPDOWN NAVBAR --------------------------------------------------------------------------------------------------- 
       document.addEventListener('DOMContentLoaded', function () {
        const collectionsMenu = document.getElementById('collectionsMenu');
    
        // Ottieni il nome del negozio dal subdomain o altra fonte
        const shopName = "{{ shop_subdomain }}";
    
        // Effettua una richiesta AJAX per ottenere le collezioni
        fetch(`/api/collections?shop_name=${shopName}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.collections.length > 0) {
                    // Popola il dropdown con le collezioni
                    data.collections.forEach(collection => {
                        const listItem = document.createElement('li');
                        listItem.innerHTML = `<a class="dropdown-item" href="/collections/${collection.slug}">${collection.name}</a>`;
                        collectionsMenu.appendChild(listItem);
                    });
                } else {
                    // Nessuna collezione trovata
                    const emptyItem = document.createElement('li');
                    emptyItem.innerHTML = `<span class="dropdown-item text-muted">No collections available</span>`;
                    collectionsMenu.appendChild(emptyItem);
                }
            })
            .catch(error => {
                console.error('Error fetching collections:', error);
            });
    });
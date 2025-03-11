        /* Mostra i prodotti nella sidebar */
        function renderCartItems(cart) {
            const cartItemsContainer = document.getElementById('cartItemsContainer');
            
            // Logga il contenitore per verificare che esista
            if (!cartItemsContainer) {
                console.error('Elemento con ID "cartItemsContainer" non trovato nel DOM.');
                return;
            }

            // Logga il contenuto del carrello
            console.log('Carrello ricevuto per il rendering:', cart);

            // Svuota il contenitore
            cartItemsContainer.innerHTML = '';

            // Controlla se il carrello è vuoto
            if (cart.length === 0) {
                cartItemsContainer.innerHTML = '<p>Il carrello è vuoto</p>';
                console.log('Carrello vuoto, messaggio impostato.');
                return;
            }

            // Itera attraverso i prodotti e crea l'HTML
            cart.forEach(item => {
                console.log('Rendering prodotto:', item); // Verifica i dati di ogni prodotto

                const productRow = document.createElement('div');
                productRow.classList.add('cart-item', 'd-flex', 'align-items-center', 'mb-3');

                // Genera l'HTML dinamico per il prodotto
                productRow.innerHTML = `
                    <div class="me-3">
                        <img src="${item.image || '/static/images/placeholder.png'}" 
                            alt="${item.name}" 
                            class="img-fluid" 
                            style="width: 50px; height: 50px; object-fit: cover;">
                    </div>
                    <div class="flex-grow-1">
                        <strong>${item.name}</strong><br>
                        <span class="text-muted">€${parseFloat(item.price).toFixed(2)}</span><br>
                        <span class="text-muted small">Quantità: ${item.quantity}</span>
                    </div>
                    <div>
                        <button class="btn btn-danger btn-sm" onclick="removeItemFromCart('${item.id}')">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                `;

                // Aggiungi il prodotto al contenitore
                cartItemsContainer.appendChild(productRow);
            });

            console.log('Prodotti renderizzati con successo.');
}
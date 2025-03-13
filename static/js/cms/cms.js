// Aggiungi al carrello -------------------------------------------------------------------------------------------
function addToCart(product) {
    const addToCartButton = document.getElementById('addToCartButton');

    // Cambia temporaneamente il testo del pulsante
    const originalText = addToCartButton.textContent;
    addToCartButton.textContent = 'Aggiungendo...';
    addToCartButton.disabled = true;

    fetch('/add_to_cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(product)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Prodotto aggiunto al carrello:', data.cart);

            // Cambia il testo del pulsante per confermare l'aggiunta
            addToCartButton.textContent = 'Aggiunto!';
            addToCartButton.classList.add('btn-success');
            setTimeout(() => {
                addToCartButton.textContent = originalText;
                addToCartButton.classList.remove('btn-success');
                addToCartButton.disabled = false;

                // Aggiorna il contenuto della sidebar se aperta
                if (document.getElementById('cartSidebar').classList.contains('open')) {
                    fetchCartContents();
                }
            }, 2000);
        } else {
            // Gestione errore
            addToCartButton.textContent = 'Errore!';
            addToCartButton.classList.add('btn-danger');
            setTimeout(() => {
                addToCartButton.textContent = originalText;
                addToCartButton.classList.remove('btn-danger');
                addToCartButton.disabled = false;
            }, 2000);
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        // Mostra errore sul pulsante
        addToCartButton.textContent = 'Errore!';
        addToCartButton.classList.add('btn-danger');
        setTimeout(() => {
            addToCartButton.textContent = originalText;
            addToCartButton.classList.remove('btn-danger');
            addToCartButton.disabled = false;
        }, 2000);
    });
}

// Aggiungi l'evento click al pulsante
document.getElementById('addToCartButton').addEventListener('click', () => {
    // Ottieni la quantità dall'input
    const quantityInput = document.getElementById('quantity');
    const quantity = parseInt(quantityInput.value) || 1; // Default a 1 se l'input non è valido

    // Crea l'oggetto prodotto dinamicamente
    const product = {
        product_id: '{{ product.id }}',
        name: '{{ product.name }}',
        image: '{{ product.image_url }}',
        price: '{{ product.price }}',
        quantity: quantity
    };

    addToCart(product);
});

// Cookie Banner ---------------------------------------------------------------------------------------------------
    document.addEventListener("DOMContentLoaded", function () {
        const cookieBar = document.getElementById("cookie-bar");
        const acceptBtn = document.getElementById("accept-cookies");
        const rejectBtn = document.getElementById("reject-cookies");

        // Controllo se l'utente ha già accettato/rifiutato i cookie
        if (!localStorage.getItem("cookiesAccepted")) {
            cookieBar.classList.remove("d-none");
        }

        // Accettazione cookie
        acceptBtn.addEventListener("click", function () {
            localStorage.setItem("cookiesAccepted", "true");
            cookieBar.classList.add("d-none");
        });

        // Rifiuto cookie
        rejectBtn.addEventListener("click", function () {
            localStorage.setItem("cookiesAccepted", "false");
            cookieBar.classList.add("d-none");
        });
    });

/* Recupera i contenuti del carrello dal backend */
function fetchCartContents() {
    fetch('/cart_contents')
        .then(response => response.json())
        .then(data => {
            if (data.cart) {
                renderCartItems(data.cart);
                updateCartTotals(data.cart);
            }
        })
        .catch(error => console.error('Errore nel recupero del carrello:', error));
}


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

// Tasti --------------------------------------------------------------------------------------------------- 

document.addEventListener("DOMContentLoaded", function () {
    // Apri il carrello
    document.getElementById("cart")?.addEventListener("click", function () {
        toggleCartSidebar();
    });

    // Vai alla pagina account
    document.getElementById("account")?.addEventListener("click", function () {
        window.location.href = "/account";
    });

    // Attiva la ricerca
    document.getElementById("search")?.addEventListener("click", function () {
        document.getElementById("searchInput").focus();
    });
});

// Funzione per aprire/chiudere la sidebar  ----------------------------------------------------------------
function toggleCartSidebar() {
    const sidebar = document.getElementById('cartSidebar');
    sidebar.classList.toggle('open');
    if (sidebar.classList.contains('open')) {
        fetchCartContents();
    }
}

/* Procedi al checkout */
function proceedToCheckout() {
    window.location.href = '/checkout';
}

/* Rimuove un prodotto dal carrello */
function removeItemFromCart(productId) {
    fetch('/remove_from_cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fetchCartContents();
        }
    })
    .catch(error => console.error('Errore nella rimozione del prodotto:', error));
}

document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/track-visit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ page_url: window.location.pathname })
    })
    .then(response => response.json())
    .then(data => console.log("📊 Analytics:", data))
    .catch(error => console.error("Error tracking visit:", error));
});

/* Aggiorna i totali del carrello */
function updateCartTotals(cart) {
    const subtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const total = subtotal; // Eventualmente aggiungi tasse/spedizione
    document.getElementById('cartSubtotal').textContent = `€${subtotal.toFixed(2)}`;
    document.getElementById('cartTotal').textContent = `€${total.toFixed(2)}`;
}


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
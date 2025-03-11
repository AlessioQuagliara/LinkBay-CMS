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
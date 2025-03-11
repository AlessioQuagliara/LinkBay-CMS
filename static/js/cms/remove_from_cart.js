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
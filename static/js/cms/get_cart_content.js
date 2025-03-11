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
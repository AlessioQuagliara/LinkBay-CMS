/* Aggiorna i totali del carrello */
function updateCartTotals(cart) {
    const subtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const total = subtotal; // Eventualmente aggiungi tasse/spedizione
    document.getElementById('cartSubtotal').textContent = `€${subtotal.toFixed(2)}`;
    document.getElementById('cartTotal').textContent = `€${total.toFixed(2)}`;
}
/* Funzione per aprire/chiudere la sidebar */
function toggleCartSidebar() {
    const sidebar = document.getElementById('cartSidebar');
    sidebar.classList.toggle('open');
    if (sidebar.classList.contains('open')) {
        fetchCartContents();
    }
}
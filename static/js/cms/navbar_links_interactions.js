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
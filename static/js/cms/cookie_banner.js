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
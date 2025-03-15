// AGGIUNGI AL CARRELLO -------------------------------------------------------------------------------------------

// FUNZIONI PER IL CARRELLO DINAMICO ----------------------------------------------------------------

// SOSTITUISCI LA NAVBAR ED IL FOTER -----------------------------------------------------------------------------------

// RENDERIZZA I NAVBAR LINKS --------------------------------------------------------------------------------------------------- 

// COOKIE BANNER ---------------------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
    const cookieBar = document.getElementById("cookie-bar");
    const acceptBtn = document.getElementById("accept-cookies");
    const rejectBtn = document.getElementById("reject-cookies");

    if (!cookieBar) return;

    // Controlla se i cookie sono già stati accettati
    if (!localStorage.getItem("cookiesAccepted")) {
        cookieBar.classList.remove("d-none");
    }

    acceptBtn.addEventListener("click", function () {
        localStorage.setItem("cookiesAccepted", "true");
        cookieBar.classList.add("d-none");
    });

    rejectBtn.addEventListener("click", function () {
        localStorage.setItem("cookiesAccepted", "false");
        cookieBar.classList.add("d-none");
    });
});
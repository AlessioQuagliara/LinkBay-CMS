// Helper condivisi dagli script della dashboard (overview.js, insights.js,
// declining.js, sites.js) — evita di duplicare escaping HTML e POST con CSRF
// token in ogni file. Caricare prima degli script che lo usano.
window.Common = (function () {
  "use strict";

  function csrfToken() {
    return (document.querySelector('meta[name="csrf-token"]') || {}).content || "";
  }

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : s;
    return d.innerHTML;
  }

  async function postForm(url, params) {
    return fetch(url, {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken(), "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams(params).toString(),
    });
  }

  // Toast daisyUI generato lato client — stessa struttura/classi del toast
  // server-side per i flash message Flask (vedi #flash-toast in
  // app/templates/base.html): stesso contenitore fisso toast-top/toast-end,
  // stesso alert-soft + shadow-lg, stesso auto-dismiss scaglionato. Usalo al
  // posto di alert()/confirm() nativi per qualunque feedback innescato da
  // JS (es. un fetch fallito), così l'esperienza resta coerente col resto
  // della piattaforma invece di un dialog di sistema fuori tema.
  function showToast(message, type) {
    let container = document.getElementById("flash-toast");
    if (!container) {
      container = document.createElement("div");
      container.id = "flash-toast";
      container.className = "toast toast-top toast-end z-50";
      document.body.appendChild(container);
    }

    const alertClass = type === "success" ? "alert-success" : type === "info" ? "alert-info" : "alert-error";
    const el = document.createElement("div");
    el.setAttribute("role", "alert");
    el.className = `alert ${alertClass} alert-soft shadow-lg max-w-xs sm:max-w-sm whitespace-normal`;
    el.dataset.flash = "";

    const span = document.createElement("span");
    span.textContent = message;
    el.appendChild(span);

    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "btn btn-ghost btn-xs btn-circle";
    closeBtn.setAttribute("aria-label", "Dismiss");
    closeBtn.textContent = "✕";
    el.appendChild(closeBtn);

    container.appendChild(el);

    const remove = () => {
      el.style.transition = "opacity .3s, transform .3s";
      el.style.opacity = "0";
      el.style.transform = "translateX(0.5rem)";
      setTimeout(() => el.remove(), 300);
    };
    closeBtn.addEventListener("click", remove);
    // Scaglionato sui toast già presenti, stessa logica del blocco flash
    // server-side, per non far sparire più messaggi tutti nello stesso istante.
    const stagger = container.querySelectorAll("[data-flash]").length - 1;
    setTimeout(remove, 4000 + Math.max(0, stagger) * 400);

    return el;
  }

  return { esc: esc, postForm: postForm, csrfToken: csrfToken, showToast: showToast };
})();

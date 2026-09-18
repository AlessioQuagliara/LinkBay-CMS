// Checkout Paddle (hosted, server-driven): il bottone chiama il backend con
// una sola chiave interna whitelistata (plan | credit_package — mai un
// price_id/importo), poi redirige al checkout_url restituito. Nessuna prova
// di pagamento viene letta qui: /billing/paddle/pending fa polling su
// /billing/status finché il webhook non conferma (vedi
// app/webhooks/routes.py).
window.PaddleCheckout = (function () {
  "use strict";

  function setBusy(button, busy) {
    if (!button) return;
    button.disabled = busy;
    if (busy) {
      button.dataset.originalText = button.dataset.originalText || button.textContent;
      button.textContent = button.dataset.loadingText || button.textContent;
    } else if (button.dataset.originalText) {
      button.textContent = button.dataset.originalText;
    }
  }

  async function startCheckout(url, params, button) {
    setBusy(button, true);
    try {
      const res = await window.Common.postForm(url, params);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        window.Common.showToast(data.message || "This payment option isn't available right now.", "error");
        setBusy(button, false);
        return;
      }
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
        return;
      }
      window.Common.showToast("Unexpected response — please try again.", "error");
      setBusy(button, false);
    } catch (e) {
      window.Common.showToast("Network error — please try again.", "error");
      setBusy(button, false);
    }
  }

  function bindSubscriptionButtons(selector, url) {
    document.querySelectorAll(selector).forEach((btn) => {
      btn.addEventListener("click", () => startCheckout(url, { plan: btn.dataset.plan }, btn));
    });
  }

  function bindCreditButtons(selector, url) {
    document.querySelectorAll(selector).forEach((btn) => {
      btn.addEventListener("click", () => startCheckout(url, { credit_package: btn.dataset.creditPackage }, btn));
    });
  }

  // Polling per la pagina "pagamento in elaborazione" (billing/paddle_pending.html).
  // Non tratta MAI il semplice ritorno su questa pagina come prova di
  // pagamento: aspetta che /billing/status rifletta lo stato scritto dal
  // webhook verificato.
  function pollStatus(opts) {
    const { statusUrl, subscriptionUrl, spinnerEl, successEl, titleEl, messageEl } = opts;
    const maxAttempts = 40; // ~2 minuti a 3s di intervallo
    let attempts = 0;

    async function tick() {
      attempts += 1;
      try {
        const res = await fetch(statusUrl, { headers: { Accept: "application/json" } });
        const data = await res.json();
        if (data.has_active_access) {
          if (spinnerEl) spinnerEl.classList.add("hidden");
          if (successEl) successEl.classList.remove("hidden");
          if (titleEl) titleEl.textContent = "Your plan is active!";
          if (messageEl) messageEl.textContent = "Redirecting…";
          setTimeout(() => {
            window.location.href = subscriptionUrl;
          }, 1200);
          return;
        }
      } catch (e) {
        // Errore di rete transitorio: continua a fare polling, non è un
        // fallimento definitivo.
      }

      if (attempts >= maxAttempts) {
        if (spinnerEl) spinnerEl.classList.add("hidden");
        if (titleEl) titleEl.textContent = "Still processing…";
        if (messageEl) {
          messageEl.textContent =
            "This is taking longer than usual. Your payment is safe — check back in a few minutes or contact support.";
        }
        return;
      }
      setTimeout(tick, 3000);
    }

    tick();
  }

  return { startCheckout: startCheckout, bindSubscriptionButtons: bindSubscriptionButtons, bindCreditButtons: bindCreditButtons, pollStatus: pollStatus };
})();

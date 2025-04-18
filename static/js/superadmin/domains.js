document.addEventListener("DOMContentLoaded", function () {
  const domainInput = document.getElementById("search-domain-input");
  const checkBtn = document.getElementById("check-domain-btn");
  const domainResult = document.getElementById("domain-result");

  checkBtn.addEventListener("click", async function () {
    const domain = domainInput.value.trim();
    if (!domain) {
      domainResult.innerHTML = `<div class="alert alert-warning">Inserisci un dominio valido</div>`;
      return;
    }

    domainResult.innerHTML = '<i class="fa fa-spinner fa-spin me-2"></i> Ricerca in corso...';
    domainResult.className = "small text-muted mt-2";

    try {
      const res = await fetch(`/api/domains/check?domain=${encodeURIComponent(domain)}`);
      const data = await res.json();

      if (res.ok && data.success && data.results && data.results.length > 0) {
        let html = `<div class="mt-3"><strong>Risultati disponibili:</strong><ul class="list-group mt-2">`;
        data.results.forEach(item => {
          const badge = item.available ? 'success' : 'secondary';
          const action = item.available ? `<button class="btn btn-sm btn-outline-primary float-end btn-purchase-domain" data-domain="${item.domain}" data-price="${item.price_eur}">Acquista</button>` : '';
          html += `
            <li class="list-group-item d-flex justify-content-between align-items-center">
              <span>
                <span class="badge bg-${badge} me-2">${item.available ? 'Disponibile' : 'Non disponibile'}</span>
                ${item.domain} - €${item.price_eur}
              </span>
              ${action}
            </li>
          `;
        });
        html += `</ul></div>`;
        domainResult.innerHTML = html;
      } else {
        domainResult.innerHTML = `<div class="alert alert-warning">Nessun risultato disponibile per il dominio inserito.</div>`;
      }
    } catch (err) {
      console.error(err);
      domainResult.innerHTML = `<div class="alert alert-danger">Errore nella richiesta al server.</div>`;
    }
  });
});


function disableRenewal(domainId) {
  Swal.fire({
    title: 'Sei sicuro?',
    text: "Il rinnovo automatico verrà disattivato.",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#aaa',
    confirmButtonText: 'Sì, disattiva'
  }).then((result) => {
    if (result.isConfirmed) {
      fetch(`/api/domains/${domainId}/disable-renewal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          Swal.fire('Disattivato', data.message, 'success').then(() => location.reload());
        } else {
          Swal.fire('Errore', data.message, 'error');
        }
      });
    }
  });
}
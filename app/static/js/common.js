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

  return { esc: esc, postForm: postForm, csrfToken: csrfToken };
})();

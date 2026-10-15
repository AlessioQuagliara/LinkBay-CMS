// Helper condivisi dagli script della dashboard (overview.js, insights.js,
// declining.js, sites.js, audits.js) — escaping, POST con CSRF, formattazione,
// stati della pagina, selettore siti, polling dei job. Caricare per primo.
window.Common = (function () {
  "use strict";

  function csrfToken() {
    return (document.querySelector('meta[name="csrf-token"]') || {}).content || "";
  }

  // Escape anche di " e ': il risultato finisce pure dentro attributi
  // (title/href/data-*) con dati di Search Console scritti da terzi.
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
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

  // --- Formattazione --------------------------------------------------------
  const nf = new Intl.NumberFormat();
  const fmtInt = (n) => nf.format(Math.round(n || 0));
  const fmtPos = (n) => (n || 0).toFixed(1);
  const fmtPct = (frac) => (100 * (frac || 0)).toFixed(1) + "%";

  function shortUrl(url) {
    try {
      const u = new URL(url);
      return u.pathname === "/" ? u.hostname : u.pathname;
    } catch (e) {
      return url;
    }
  }

  function shortDate(iso) {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  }

  // Delta percentuale con freccia + colore semantico. `emptyText` quando non
  // c'è storico, `suffix` opzionale dopo la percentuale (es. "vs prev.").
  function deltaHtml(deltaPct, lowerIsBetter, emptyText, suffix) {
    if (deltaPct === null || deltaPct === undefined) {
      return `<span class="text-base-content/40">${emptyText}</span>`;
    }
    const good = lowerIsBetter ? deltaPct < 0 : deltaPct > 0;
    const flat = Math.abs(deltaPct) < 0.05;
    const arrow = flat ? "→" : deltaPct > 0 ? "↗︎" : "↘︎";
    const cls = flat ? "text-base-content/50" : good ? "text-success" : "text-error";
    return `<span class="${cls}">${arrow} ${Math.abs(deltaPct).toFixed(0)}%${suffix ? " " + suffix : ""}</span>`;
  }

  // Rating 1-5 stelle (daisyUI). `name` deve essere unico nella pagina.
  function starsHtml(stars, name, sizeClass) {
    const color = stars >= 4 ? "bg-success" : stars === 3 ? "bg-warning" : "bg-error";
    let out = `<div class="rating ${sizeClass}" aria-label="Health ${stars} of 5">`;
    for (let i = 1; i <= 5; i++) {
      out +=
        `<input type="radio" name="${name}" class="mask mask-star-2 ${color}" ` +
        `aria-label="${i} star"${i === stars ? " checked" : ""} disabled />`;
    }
    return out + "</div>";
  }

  // --- Stati pagina (loading/error/empty/data) --------------------------------
  // `ids`: nome stato -> id elemento. Ritorna show(name) e showError(msg).
  function pageStates(ids) {
    const els = {};
    Object.entries(ids).forEach(([name, id]) => (els[name] = document.getElementById(id)));
    function show(name) {
      Object.entries(els).forEach(([key, el]) => {
        if (el) el.classList.toggle("hidden", key !== name);
      });
    }
    function showError(msg) {
      const el = document.getElementById("state-error-msg");
      if (el && msg) el.textContent = msg;
      show("error");
    }
    return { show: show, showError: showError };
  }

  // Popola il <select> con i siti monitorati (GET url -> {sites: [...]}) e
  // ritorna l'elenco; disabilitato se c'è un solo sito. Lancia su errore HTTP.
  async function fillSiteSelect(select, url) {
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const sites = (await res.json()).sites || [];
    select.innerHTML = sites.map((s) => `<option value="${esc(s)}">${esc(s)}</option>`).join("");
    select.disabled = sites.length < 2;
    return sites;
  }

  // Polling di un job RQ (vedi app/jobs/queue.py::job_status_payload) ogni 2s
  // finché non è concluso; {status: "timeout"} dopo maxAttempts tentativi.
  async function pollJob(statusUrl, maxAttempts) {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      let data;
      try {
        const res = await fetch(statusUrl, { headers: { Accept: "application/json" } });
        data = await res.json();
      } catch (e) {
        continue; // errore di rete transitorio: ritenta al prossimo giro
      }
      if (data.status === "finished" || data.status === "failed" || data.status === "not_found") {
        return data;
      }
    }
    return { status: "timeout" };
  }

  return {
    esc: esc, postForm: postForm, csrfToken: csrfToken, showToast: showToast,
    fmtInt: fmtInt, fmtPos: fmtPos, fmtPct: fmtPct, shortUrl: shortUrl, shortDate: shortDate,
    deltaHtml: deltaHtml, starsHtml: starsHtml, pageStates: pageStates,
    fillSiteSelect: fillSiteSelect, pollJob: pollJob,
  };
})();

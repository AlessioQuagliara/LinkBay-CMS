// Dashboard Overview: sceglie il sito monitorato, scarica i dati aggregati
// (/gsc/api/insights) e mostra KPI rapidi, le pagine monitorate (limite
// dipende dal piano, vedi app/entitlements — quelle che perdono più
// traffico per prime) e un'anteprima del sito.
(function () {
  "use strict";

  const select = document.getElementById("site-select");
  if (!select) return; // account non collegato: la pagina mostra il connettore

  const t = (window.I18N && window.I18N.t) || ((k) => k);

  const SITES_URL = select.dataset.sitesUrl;
  const INSIGHTS_URL = select.dataset.insightsUrl;
  const PAGE_LIMIT = parseInt(select.dataset.pageLimit || "3", 10);
  const DAYS = 28;

  const { esc, fmtInt, fmtPos, shortUrl, shortDate } = window.Common;
  const { show, showError } = window.Common.pageStates({
    loading: "state-loading", error: "state-error", empty: "state-empty", data: "state-data",
  });
  const deltaDesc = (pct, lowerIsBetter) => window.Common.deltaHtml(pct, lowerIsBetter, t("noPriorData"), t("vsPrev"));
  const starsHtml = (stars, seed) => window.Common.starsHtml(stars, "ov-rating-" + seed, "rating-xs");

  // siteUrl GSC -> URL navigabile (gestisce le domain property sc-domain:).
  function siteToUrl(siteUrl) {
    if (siteUrl.startsWith("sc-domain:")) return "https://" + siteUrl.slice("sc-domain:".length) + "/";
    return siteUrl;
  }

  // --- Rendering -------------------------------------------------------------
  function renderStats(o) {
    const host = document.getElementById("overview-stats");
    const cell = (title, value, deltaHtml) =>
      `<div class="stat place-items-center">
         <div class="stat-title">${title}</div>
         <div class="stat-value text-2xl">${value}</div>
         <div class="stat-desc">${deltaHtml}</div>
       </div>`;
    host.innerHTML =
      cell(t("statClicks"), fmtInt(o.clicks.value), deltaDesc(o.clicks.delta_pct, false)) +
      cell(t("statImpressions"), fmtInt(o.impressions.value), deltaDesc(o.impressions.delta_pct, false)) +
      cell(t("statAvgPosition"), fmtPos(o.position.value), deltaDesc(o.position.delta_pct, true));
  }

  function renderPages(pages) {
    const host = document.getElementById("pages-list");
    const note = document.getElementById("pages-note");
    const monitored = pages.slice(0, PAGE_LIMIT);
    note.textContent = `${monitored.length} of ${PAGE_LIMIT}`;

    if (!monitored.length) {
      host.innerHTML =
        `<p class="text-sm text-base-content/50">${t("noPageData")}</p>`;
      return;
    }

    host.innerHTML = monitored
      .map((p, i) => {
        const delta =
          p.clicks_delta_pct === null || p.clicks_delta_pct === undefined
            ? `<span class="text-base-content/40">— ${t("newDelta")}</span>`
            : deltaDesc(p.clicks_delta_pct, false);
        return `<div class="card card-border bg-base-100">
          <div class="card-body p-4 gap-2">
            <div class="flex items-center justify-between gap-3">
              <a href="${esc(p.url)}" target="_blank" rel="noopener"
                 class="link link-hover font-medium truncate" title="${esc(p.url)}">${esc(shortUrl(p.url))}</a>
              ${starsHtml(p.stars, i)}
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-base-content/70">${fmtInt(p.clicks)} ${t("statClicks")}</span>
              <span>${delta}</span>
            </div>
          </div>
        </div>`;
      })
      .join("");
  }

  function renderPreview(siteUrl) {
    const url = siteToUrl(siteUrl);
    const label = document.getElementById("site-preview-url");
    const frame = document.getElementById("site-preview");
    if (label) label.textContent = url;
    if (frame) frame.src = url;
  }

  function renderRange(range) {
    const el = document.getElementById("range-label");
    if (el && range) {
      el.textContent = t("rangeLabel", {
        start: shortDate(range.start),
        end: shortDate(range.end),
        days: range.days,
      });
    }
  }

  // --- Data flow -------------------------------------------------------------
  function loadInsights(siteUrl) {
    show("loading");
    renderPreview(siteUrl); // l'anteprima non dipende dai dati: caricala subito
    fetch(`${INSIGHTS_URL}?site=${encodeURIComponent(siteUrl)}&days=${DAYS}`, {
      headers: { "X-Requested-With": "fetch" },
    })
      .then((r) => {
        if (!r.ok) throw new Error("insights " + r.status);
        return r.json();
      })
      .then((data) => {
        if (data.error) throw new Error(data.error);
        renderRange(data.overview.range);
        renderStats(data.overview);
        renderPages(data.pages || []);
        show("data");
      })
      .catch(() => showError(t("loadInsightsError")));
  }

  function init() {
    // Sorgente: solo i siti già aggiunti al monitoraggio (non tutte le
    // proprietà verificate GSC) — aggiungerne di nuovi si fa dalla pagina
    // Sites (/dashboard/sites), qui il selettore è un puro switcher.
    window.Common.fillSiteSelect(select, SITES_URL)
      .then((sites) => {
        if (!sites.length) {
          show("empty");
          return;
        }
        select.addEventListener("change", () => loadInsights(select.value));
        loadInsights(sites[0]);
      })
      .catch(() => showError(t("loadSitesError")));
  }

  init();
})();

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

  const states = {
    loading: document.getElementById("state-loading"),
    error: document.getElementById("state-error"),
    empty: document.getElementById("state-empty"),
    data: document.getElementById("state-data"),
  };

  function show(name) {
    Object.entries(states).forEach(([key, el]) => {
      if (el) el.classList.toggle("hidden", key !== name);
    });
  }
  function showError(msg) {
    const el = document.getElementById("state-error-msg");
    if (el && msg) el.textContent = msg;
    show("error");
  }

  // --- Formattazione ---------------------------------------------------------
  const nf = new Intl.NumberFormat();
  const fmtInt = (n) => nf.format(Math.round(n || 0));
  const fmtPos = (n) => (n || 0).toFixed(1);

  const esc = window.Common.esc;
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

  // Delta come descrizione stat (freccia + colore semantico).
  function deltaDesc(deltaPct, lowerIsBetter) {
    if (deltaPct === null || deltaPct === undefined) {
      return `<span class="text-base-content/40">${t("noPriorData")}</span>`;
    }
    const good = lowerIsBetter ? deltaPct < 0 : deltaPct > 0;
    const flat = Math.abs(deltaPct) < 0.05;
    const arrow = flat ? "→" : deltaPct > 0 ? "↗︎" : "↘︎";
    const cls = flat ? "text-base-content/50" : good ? "text-success" : "text-error";
    return `<span class="${cls}">${arrow} ${Math.abs(deltaPct).toFixed(0)}% ${t("vsPrev")}</span>`;
  }

  function starsHtml(stars, seed) {
    const color = stars >= 4 ? "bg-success" : stars === 3 ? "bg-warning" : "bg-error";
    const name = "ov-rating-" + seed;
    let out = '<div class="rating rating-xs" aria-label="Health ' + stars + ' of 5">';
    for (let i = 1; i <= 5; i++) {
      out +=
        `<input type="radio" name="${name}" class="mask mask-star-2 ${color}" ` +
        `aria-label="${i} star"${i === stars ? " checked" : ""} disabled />`;
    }
    return out + "</div>";
  }

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
    fetch(SITES_URL, { headers: { "X-Requested-With": "fetch" } })
      .then((r) => {
        if (r.status === 401) throw new Error("not_connected");
        return r.json();
      })
      .then((data) => {
        const sites = data.sites || [];
        if (!sites.length) {
          show("empty");
          return;
        }
        select.innerHTML = sites.map((s) => `<option value="${esc(s)}">${esc(s)}</option>`).join("");
        select.disabled = sites.length < 2;
        select.addEventListener("change", () => loadInsights(select.value));
        loadInsights(sites[0]);
      })
      .catch(() => showError(t("loadSitesError")));
  }

  init();
})();

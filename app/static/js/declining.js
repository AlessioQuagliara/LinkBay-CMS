// Vista Declining Pages: per il sito scelto mostra le pagine in "vera discesa"
// prodotte dal rule engine (page_alerts), come card con priorità, click persi,
// posizione prima/dopo, motivazione testuale e trend a 6 mesi espandibile.
// Nessuna libreria di charting: la sparkline è SVG inline, stesso metodo del
// grafico #chart in insights.js.
(function () {
  "use strict";

  const select = document.getElementById("site-select");
  if (!select) return; // account non collegato: la pagina mostra il connettore

  const SITES_URL = select.dataset.sitesUrl;
  const MONITORED_URL = select.dataset.monitoredUrl;
  const LIST_URL = select.dataset.listUrl;
  const TREND_URL = select.dataset.trendUrl;
  const QUERY_LOSSES_URL = select.dataset.queryLossesUrl;
  const STATUS_URL = select.dataset.statusUrl;

  const CSRF = (document.querySelector('meta[name="csrf-token"]') || {}).content || "";

  const states = {
    loading: document.getElementById("state-loading"),
    error: document.getElementById("state-error"),
    empty: document.getElementById("state-empty"),
    data: document.getElementById("state-data"),
  };

  let currentStatus = "new";

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

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : s;
    return d.innerHTML;
  }
  function shortUrl(url) {
    try {
      const u = new URL(url);
      return u.pathname === "/" ? u.hostname : u.pathname;
    } catch (e) {
      return url;
    }
  }
  function shortMonth(iso) {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString(undefined, { month: "short", year: "2-digit" });
  }

  const STATUS_LABELS = {
    new: "Nuova",
    acknowledged: "Riconosciuta",
    done: "Fatta",
    recovered: "Recuperata",
  };

  // Priorità -> colore badge (alto=error, medio=warning, basso=neutral),
  // stessa soglia dello scoring lato server (66 / 33).
  function priority(score) {
    if (score >= 66) return { cls: "badge-error", label: "alta" };
    if (score >= 33) return { cls: "badge-warning", label: "media" };
    return { cls: "badge-neutral", label: "bassa" };
  }

  async function postForm(url, params) {
    return fetch(url, {
      method: "POST",
      headers: { "X-CSRFToken": CSRF, "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams(params).toString(),
    });
  }

  // --- Sparkline trend (SVG inline, single series, tema-aware) ----------------
  function renderSparkline(host, series) {
    if (!series || series.length < 2) {
      host.innerHTML =
        '<p class="text-base-content/50 text-xs py-3">Storico insufficiente per il trend.</p>';
      return;
    }

    const W = 320, H = 60, padL = 4, padR = 4, padT = 6, padB = 16;
    const plotW = W - padL - padR, plotH = H - padT - padB;
    const n = series.length;
    const maxClicks = Math.max(1, ...series.map((d) => d.clicks));

    const x = (i) => padL + (n <= 1 ? 0 : (i / (n - 1)) * plotW);
    const y = (v) => padT + plotH - (v / maxClicks) * plotH;

    const pts = series.map((d, i) => `${x(i).toFixed(1)},${y(d.clicks).toFixed(1)}`);
    const linePath = "M" + pts.join(" L");
    const areaPath =
      `M${x(0).toFixed(1)},${(padT + plotH).toFixed(1)} L` +
      pts.join(" L") +
      ` L${x(n - 1).toFixed(1)},${(padT + plotH).toFixed(1)} Z`;

    const labels =
      `<text class="text-base-content/50" x="${x(0).toFixed(1)}" y="${H - 4}" font-size="9" fill="currentColor">${esc(shortMonth(series[0].month))}</text>` +
      `<text class="text-base-content/50" x="${x(n - 1).toFixed(1)}" y="${H - 4}" text-anchor="end" font-size="9" fill="currentColor">${esc(shortMonth(series[n - 1].month))} · ${fmtInt(series[n - 1].clicks)} click</text>`;

    host.innerHTML =
      `<div class="text-primary mt-2">` +
      `<svg viewBox="0 0 ${W} ${H}" width="100%" preserveAspectRatio="none" role="img" aria-label="Trend click 6 mesi">` +
      `<path d="${areaPath}" fill="currentColor" fill-opacity="0.12" stroke="none"/>` +
      `<path d="${linePath}" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>` +
      labels +
      `</svg></div>`;
  }

  // --- Tabella query in perdita (una sola pagina) ----------------------------
  function renderQueryLosses(host, queries) {
    if (!queries || !queries.length) {
      host.innerHTML =
        '<p class="text-base-content/50 text-xs py-2">Nessuna query in calo per questa pagina.</p>';
      return;
    }
    const rows = queries
      .map((q) => {
        const lost = Math.max(0, (q.clicks_prev || 0) - (q.clicks || 0));
        return (
          `<tr>` +
          `<td class="truncate max-w-[16rem]" title="${esc(q.query)}">${esc(q.query)}</td>` +
          `<td class="text-right text-error">−${fmtInt(lost)}</td>` +
          `<td class="text-right whitespace-nowrap">${fmtPos(q.position_prev)} → ${fmtPos(q.position)}</td>` +
          `</tr>`
        );
      })
      .join("");
    host.innerHTML =
      `<div class="overflow-x-auto"><table class="table table-sm">` +
      `<thead><tr>` +
      `<th>Query</th><th class="text-right">Click persi</th><th class="text-right">Posizione</th>` +
      `</tr></thead><tbody>${rows}</tbody></table></div>`;
  }

  // --- Card di un alert ------------------------------------------------------
  function reasonHtml(text) {
    if (!text) return "";
    return (text || "")
      .split("\n")
      .filter((l) => l.trim() !== "")
      .map((l) => `<p>${esc(l)}</p>`)
      .join("");
  }

  function statusSelectHtml(a) {
    const opts = ["new", "acknowledged", "done", "recovered"]
      .map((s) => `<option value="${s}"${s === a.status ? " selected" : ""}>${STATUS_LABELS[s]}</option>`)
      .join("");
    return `<select class="select select-sm select-bordered status-select" data-id="${a.id}" aria-label="Cambia stato">${opts}</select>`;
  }

  function cardHtml(a) {
    const p = priority(a.priority_score);
    const lossAbs = Math.abs(a.click_loss_abs || 0);
    const lossPct = Math.round(Math.abs(a.click_loss_pct || 0));
    const label = shortUrl(a.url);

    return `
      <div class="card card-border bg-base-100 shadow-xs" data-id="${a.id}" data-status="${a.status}">
        <div class="card-body gap-3">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <span class="badge ${p.cls} badge-sm">Priorità ${p.label}</span>
                <span class="text-xs text-base-content/50">score ${fmtInt(a.priority_score)}</span>
              </div>
              <a href="${esc(a.url)}" target="_blank" rel="noopener"
                 class="link link-hover font-medium truncate block max-w-md mt-1"
                 title="${esc(a.url)}">${esc(label)}</a>
            </div>
            <div class="shrink-0">${statusSelectHtml(a)}</div>
          </div>

          <div class="flex flex-wrap gap-x-8 gap-y-1 text-sm">
            <div>
              <span class="text-base-content/50">Click persi/mese</span>
              <span class="font-semibold text-error ms-1">−${fmtInt(lossAbs)}</span>
              <span class="text-base-content/50">(−${lossPct}%)</span>
            </div>
            <div>
              <span class="text-base-content/50">Posizione</span>
              <span class="font-semibold ms-1">${fmtPos(a.position_before)} → ${fmtPos(a.position_after)}</span>
            </div>
          </div>

          <div class="text-sm text-base-content/80 space-y-0.5">${reasonHtml(a.reason_text)}</div>

          <div class="collapse collapse-arrow border border-base-300 rounded-box">
            <input type="checkbox" class="trend-toggle" data-page="${esc(a.url)}" />
            <div class="collapse-title text-sm font-medium py-2 min-h-0">Vedi trend 6 mesi</div>
            <div class="collapse-content">
              <div class="trend-host"><p class="text-base-content/50 text-xs py-3">Caricamento…</p></div>
              <div class="mt-3">
                <p class="text-sm font-medium mb-1">Query che hanno perso posizioni</p>
                <div class="qloss-host"><p class="text-base-content/50 text-xs py-2">Caricamento…</p></div>
              </div>
            </div>
          </div>
        </div>
      </div>`;
  }

  function renderList(alerts) {
    if (!alerts.length) {
      show("empty");
      return;
    }
    states.data.innerHTML =
      '<div class="flex flex-col gap-4">' + alerts.map(cardHtml).join("") + "</div>";
    wireCards();
    show("data");
  }

  // --- Interazioni delle card ------------------------------------------------
  function wireCards() {
    // Cambio stato -> POST; se non appartiene più al filtro corrente, togli la card.
    states.data.querySelectorAll(".status-select").forEach((sel) => {
      sel.dataset.prev = sel.value; // valore corrente, per il rollback in caso di errore
      sel.addEventListener("change", async () => {
        const id = sel.dataset.id;
        const status = sel.value;
        const prev = sel.dataset.prev;
        sel.disabled = true;
        try {
          const res = await postForm(STATUS_URL, { id, status });
          if (!res.ok) throw new Error("HTTP " + res.status);
          const { alert } = await res.json();
          sel.dataset.prev = alert.status;
          const card = states.data.querySelector(`.card[data-id="${id}"]`);
          if (card) card.dataset.status = alert.status;
          // Se il filtro non è "Tutte" e lo stato non combacia più, rimuovi la card.
          if (currentStatus !== "all" && alert.status !== currentStatus) {
            card && card.remove();
            if (!states.data.querySelector(".card")) show("empty");
          }
        } catch (e) {
          sel.value = prev; // rollback visivo
          showError("Non è stato possibile aggiornare lo stato. Riprova.");
        } finally {
          sel.disabled = false;
        }
      });
    });

    // Espansione: fetch una sola volta al primo apri (trend + query in perdita).
    states.data.querySelectorAll(".trend-toggle").forEach((toggle) => {
      toggle.addEventListener("change", async () => {
        if (!toggle.checked || toggle.dataset.loaded === "1") return;
        toggle.dataset.loaded = "1";
        const collapse = toggle.closest(".collapse");
        const page = toggle.dataset.page;

        const trendHost = collapse.querySelector(".trend-host");
        try {
          const url = TREND_URL + "?site=" + encodeURIComponent(select.value) +
            "&page=" + encodeURIComponent(page);
          const res = await fetch(url, { headers: { Accept: "application/json" } });
          if (!res.ok) throw new Error("HTTP " + res.status);
          const { series } = await res.json();
          renderSparkline(trendHost, series);
        } catch (e) {
          trendHost.innerHTML = '<p class="text-error text-xs py-3">Trend non disponibile.</p>';
        }

        const qlossHost = collapse.querySelector(".qloss-host");
        try {
          const url = QUERY_LOSSES_URL + "?site=" + encodeURIComponent(select.value) +
            "&page=" + encodeURIComponent(page);
          const res = await fetch(url, { headers: { Accept: "application/json" } });
          if (!res.ok) throw new Error("HTTP " + res.status);
          const { queries } = await res.json();
          renderQueryLosses(qlossHost, queries);
        } catch (e) {
          qlossHost.innerHTML = '<p class="text-error text-xs py-2">Query non disponibili.</p>';
        }
      });
    });
  }

  // --- Data flow -------------------------------------------------------------
  async function loadAlerts(site) {
    if (!site) return;
    show("loading");
    try {
      const url = LIST_URL + "?site=" + encodeURIComponent(site) + "&status=" + currentStatus;
      const res = await fetch(url, { headers: { Accept: "application/json" } });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const { alerts } = await res.json();
      renderList(alerts);
    } catch (e) {
      showError("Non è stato possibile caricare la lista. Riprova.");
    }
  }

  // Filtro per stato
  document.getElementById("status-filter").addEventListener("click", (ev) => {
    const btn = ev.target.closest("button[data-status]");
    if (!btn) return;
    currentStatus = btn.dataset.status;
    document
      .querySelectorAll("#status-filter button")
      .forEach((b) => b.classList.toggle("btn-active", b === btn));
    if (select.value) loadAlerts(select.value);
  });

  // --- Popolamento site-select (stesso pattern di insights.js) ---------------
  async function init() {
    show("loading");
    try {
      const res = await fetch(SITES_URL, { headers: { Accept: "application/json" } });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const { sites, monitored_site_url } = await res.json();
      if (!sites || !sites.length) {
        select.innerHTML = "<option>No sites</option>";
        show("empty");
        return;
      }
      select.innerHTML = sites
        .map((s) => `<option value="${esc(s.siteUrl)}">${esc(s.siteUrl)}</option>`)
        .join("");
      select.disabled = false;

      const preselect =
        monitored_site_url && sites.some((s) => s.siteUrl === monitored_site_url)
          ? monitored_site_url
          : sites[0].siteUrl;
      select.value = preselect;

      select.addEventListener("change", () => {
        postForm(MONITORED_URL, { site: select.value }).catch(() => {});
        loadAlerts(select.value);
      });
      loadAlerts(preselect);
    } catch (e) {
      showError("Couldn't load your Search Console sites. Please reconnect and try again.");
    }
  }

  init();
})();

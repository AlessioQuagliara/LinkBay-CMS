// Vista Declining Pages: per il sito scelto mostra le pagine in "vera discesa"
// prodotte dal rule engine (page_alerts), come card con priorità, click persi,
// posizione prima/dopo, motivazione testuale e trend a 6 mesi espandibile.
// Nessuna libreria di charting: la sparkline è SVG inline, stesso metodo del
// grafico #chart in insights.js.
(function () {
  "use strict";

  const select = document.getElementById("site-select");
  if (!select) return; // account non collegato: la pagina mostra il connettore

  const t = (window.I18N && window.I18N.t) || ((k) => k);

  const SITES_URL = select.dataset.sitesUrl;
  const LIST_URL = select.dataset.listUrl;
  const TREND_URL = select.dataset.trendUrl;
  const QUERY_LOSSES_URL = select.dataset.queryLossesUrl;
  const STATUS_URL = select.dataset.statusUrl;

  const states = {
    loading: document.getElementById("state-loading"),
    error: document.getElementById("state-error"),
    empty: document.getElementById("state-empty"),
    noSites: document.getElementById("state-no-sites"),
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

  const esc = window.Common.esc;
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

  function statusLabel(status) {
    return t(
      "status" + status.charAt(0).toUpperCase() + status.slice(1)
    );
  }

  // Priorità -> colore badge (alto=error, medio=warning, basso=neutral),
  // stessa soglia dello scoring lato server (66 / 33).
  function priority(score) {
    if (score >= 66) return { cls: "badge-error", label: t("priorityHigh") };
    if (score >= 33) return { cls: "badge-warning", label: t("priorityMedium") };
    return { cls: "badge-neutral", label: t("priorityLow") };
  }

  const postForm = window.Common.postForm;

  // --- Sparkline trend (SVG inline, single series, tema-aware) ----------------
  function renderSparkline(host, series) {
    if (!series || series.length < 2) {
      host.innerHTML =
        `<p class="text-base-content/50 text-xs py-3">${t("notEnoughHistoryTrend")}</p>`;
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
      `<text class="text-base-content/50" x="${x(n - 1).toFixed(1)}" y="${H - 4}" text-anchor="end" font-size="9" fill="currentColor">${esc(shortMonth(series[n - 1].month))} · ${fmtInt(series[n - 1].clicks)} ${t("statClicks")}</text>`;

    host.innerHTML =
      `<div class="text-primary mt-2">` +
      `<svg viewBox="0 0 ${W} ${H}" width="100%" preserveAspectRatio="none" role="img" aria-label="Trend">` +
      `<path d="${areaPath}" fill="currentColor" fill-opacity="0.12" stroke="none"/>` +
      `<path d="${linePath}" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>` +
      labels +
      `</svg></div>`;
  }

  // --- Tabella query in perdita (una sola pagina) ----------------------------
  function renderQueryLosses(host, queries) {
    if (!queries || !queries.length) {
      host.innerHTML =
        `<p class="text-base-content/50 text-xs py-2">${t("noDecliningQueries")}</p>`;
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
      `<th>${t("colQuery")}</th><th class="text-right">${t("colClicksLost")}</th><th class="text-right">${t("colPosition")}</th>` +
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
      .map((s) => `<option value="${s}"${s === a.status ? " selected" : ""}>${statusLabel(s)}</option>`)
      .join("");
    return `<select class="select select-sm select-bordered status-select" data-id="${a.id}" aria-label="${t("changeStatus")}">${opts}</select>`;
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
                <span class="badge ${p.cls} badge-sm">${t("priorityBadge", { label: p.label })}</span>
                <span class="text-xs text-base-content/50">${t("scoreLabel", { score: fmtInt(a.priority_score) })}</span>
              </div>
              <a href="${esc(a.url)}" target="_blank" rel="noopener"
                 class="link link-hover font-medium truncate block max-w-md mt-1"
                 title="${esc(a.url)}">${esc(label)}</a>
            </div>
            <div class="shrink-0">${statusSelectHtml(a)}</div>
          </div>

          <div class="flex flex-wrap gap-x-8 gap-y-1 text-sm">
            <div>
              <span class="text-base-content/50">${t("clicksLostPerMonth")}</span>
              <span class="font-semibold text-error ms-1">−${fmtInt(lossAbs)}</span>
              <span class="text-base-content/50">(−${lossPct}%)</span>
            </div>
            <div>
              <span class="text-base-content/50">${t("colPosition")}</span>
              <span class="font-semibold ms-1">${fmtPos(a.position_before)} → ${fmtPos(a.position_after)}</span>
            </div>
          </div>

          <div class="text-sm text-base-content/80 space-y-0.5">${reasonHtml(a.reason_text)}</div>

          <div class="collapse collapse-arrow border border-base-300 rounded-box">
            <input type="checkbox" class="trend-toggle" data-page="${esc(a.url)}" />
            <div class="collapse-title text-sm font-medium py-2 min-h-0">${t("seeTrend")}</div>
            <div class="collapse-content">
              <div class="trend-host"><p class="text-base-content/50 text-xs py-3">${t("loading")}</p></div>
              <div class="mt-3">
                <p class="text-sm font-medium mb-1">${t("queriesThatLostRankings")}</p>
                <div class="qloss-host"><p class="text-base-content/50 text-xs py-2">${t("loading")}</p></div>
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
          showError(t("updateStatusError"));
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
          trendHost.innerHTML = `<p class="text-error text-xs py-3">${t("trendNotAvailable")}</p>`;
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
          qlossHost.innerHTML = `<p class="text-error text-xs py-2">${t("queriesNotAvailable")}</p>`;
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
      showError(t("loadListError"));
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
      // Sorgente: solo i siti già aggiunti al monitoraggio — puro switcher,
      // aggiungerne di nuovi si fa dalla pagina Sites (/dashboard/sites).
      const res = await fetch(SITES_URL, { headers: { Accept: "application/json" } });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const { sites } = await res.json();
      if (!sites || !sites.length) {
        select.innerHTML = `<option>${esc(t("noSitesOption"))}</option>`;
        show("noSites");
        return;
      }
      select.innerHTML = sites.map((s) => `<option value="${esc(s)}">${esc(s)}</option>`).join("");
      select.disabled = sites.length < 2;

      select.addEventListener("change", () => loadAlerts(select.value));
      loadAlerts(sites[0]);
    } catch (e) {
      showError(t("loadSitesReconnectError"));
    }
  }

  init();
})();

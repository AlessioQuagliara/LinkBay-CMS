// Vista Insights: siti verificati -> per il sito scelto scarica dati aggregati
// (overview+delta, pagine con rating salute, query, serie storica click) e
// li mostra con grafico, stats, e suggerimenti AI opzionali (DeepSeek).
(function () {
  "use strict";

  const select = document.getElementById("site-select");
  if (!select) return; // account non collegato: la pagina mostra il connettore

  const t = (window.I18N && window.I18N.t) || ((k) => k);

  const SITES_URL = select.dataset.sitesUrl;
  const INSIGHTS_URL = select.dataset.insightsUrl;
  const AI_STATUS_URL = select.dataset.aiStatusUrl;
  const AI_TOGGLE_URL = select.dataset.aiToggleUrl;
  const AI_ANALYZE_URL = select.dataset.aiAnalyzeUrl;
  const AI_ANALYZE_STATUS_URL_TPL = select.dataset.aiAnalyzeStatusUrl; // contiene "__job_id__" da sostituire

  const states = {
    loading: document.getElementById("state-loading"),
    error: document.getElementById("state-error"),
    empty: document.getElementById("state-empty"),
    data: document.getElementById("state-data"),
  };

  let currentDays = 28;
  let aiAnalyses = {}; // url -> {score, suggestions, week_start}

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
  const fmtPct = (frac) => (100 * (frac || 0)).toFixed(1) + "%";
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

  function deltaBadge(deltaPct, lowerIsBetter) {
    if (deltaPct === null || deltaPct === undefined) {
      return `<span class="text-base-content/40">— ${t("noPriorData")}</span>`;
    }
    const good = lowerIsBetter ? deltaPct < 0 : deltaPct > 0;
    const flat = Math.abs(deltaPct) < 0.05;
    const arrow = flat ? "→" : deltaPct > 0 ? "↗︎" : "↘︎";
    const cls = flat ? "text-base-content/50" : good ? "text-success" : "text-error";
    return `<span class="${cls}">${arrow} ${Math.abs(deltaPct).toFixed(0)}%</span>`;
  }

  function starsHtml(stars, keySeed) {
    const color = stars >= 4 ? "bg-success" : stars === 3 ? "bg-warning" : "bg-error";
    const name = "rating-" + keySeed;
    let out = '<div class="rating rating-sm" aria-label="Health ' + stars + ' of 5">';
    for (let i = 1; i <= 5; i++) {
      out +=
        `<input type="radio" name="${name}" class="mask mask-star-2 ${color}" ` +
        `aria-label="${i} star"${i === stars ? " checked" : ""} disabled />`;
    }
    return out + "</div>";
  }

  function scoreColor(score) {
    return score >= 70 ? "text-success" : score >= 40 ? "text-warning" : "text-error";
  }

  // --- Grafico click nel tempo (SVG, single series, tema-aware) ---------------
  function renderChart(series) {
    const host = document.getElementById("chart");
    if (!series || series.length < 2) {
      host.innerHTML =
        `<p class="text-base-content/50 text-sm py-8 text-center">${t("notEnoughHistory")}</p>`;
      return;
    }

    const W = 720, H = 220, padL = 40, padR = 12, padT = 12, padB = 24;
    const plotW = W - padL - padR, plotH = H - padT - padB;
    const n = series.length;
    const maxClicks = Math.max(1, ...series.map((d) => d.clicks));

    const x = (i) => padL + (n <= 1 ? 0 : (i / (n - 1)) * plotW);
    const y = (v) => padT + plotH - (v / maxClicks) * plotH;

    const linePts = series.map((d, i) => `${x(i).toFixed(1)},${y(d.clicks).toFixed(1)}`);
    const linePath = "M" + linePts.join(" L");
    const areaPath =
      `M${x(0).toFixed(1)},${(padT + plotH).toFixed(1)} L` +
      linePts.join(" L") +
      ` L${x(n - 1).toFixed(1)},${(padT + plotH).toFixed(1)} Z`;

    // Griglia Y (0, metà, max) con etichette.
    const yTicks = [0, maxClicks / 2, maxClicks];
    const grid = yTicks
      .map((v) => {
        const yy = y(v).toFixed(1);
        return (
          `<line class="text-base-content/15" x1="${padL}" y1="${yy}" x2="${W - padR}" y2="${yy}" stroke="currentColor" stroke-width="1"/>` +
          `<text class="text-base-content/50" x="${padL - 6}" y="${yy}" text-anchor="end" dominant-baseline="middle" font-size="10" fill="currentColor">${fmtInt(v)}</text>`
        );
      })
      .join("");

    // Etichette X (prima, metà, ultima).
    const xIdx = [0, Math.floor((n - 1) / 2), n - 1];
    const xLabels = xIdx
      .map((i) => {
        const anchor = i === 0 ? "start" : i === n - 1 ? "end" : "middle";
        return `<text class="text-base-content/50" x="${x(i).toFixed(1)}" y="${H - 6}" text-anchor="${anchor}" font-size="10" fill="currentColor">${shortDate(series[i].date)}</text>`;
      })
      .join("");

    host.innerHTML =
      `<div class="relative text-primary">` +
      `<svg id="chart-svg" viewBox="0 0 ${W} ${H}" width="100%" preserveAspectRatio="none" role="img" aria-label="Clicks over time">` +
      grid +
      `<path d="${areaPath}" fill="currentColor" fill-opacity="0.12" stroke="none"/>` +
      `<path d="${linePath}" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>` +
      `<line id="chart-cross" class="text-base-content/30" x1="0" y1="${padT}" x2="0" y2="${padT + plotH}" stroke="currentColor" stroke-width="1" style="display:none"/>` +
      `<circle id="chart-dot" r="3.5" fill="currentColor" style="display:none"/>` +
      `<rect id="chart-hit" x="${padL}" y="${padT}" width="${plotW}" height="${plotH}" fill="transparent"/>` +
      `</svg>` +
      `<div id="chart-tip" class="pointer-events-none absolute hidden rounded bg-base-content text-base-100 text-xs px-2 py-1 shadow" style="transform:translate(-50%,-120%)"></div>` +
      `</div>`;

    // Hover: crosshair + dot + tooltip.
    const svg = document.getElementById("chart-svg");
    const cross = document.getElementById("chart-cross");
    const dot = document.getElementById("chart-dot");
    const tip = document.getElementById("chart-tip");
    const hit = document.getElementById("chart-hit");

    function onMove(ev) {
      const rect = svg.getBoundingClientRect();
      const relX = (ev.clientX - rect.left) / rect.width; // 0..1 sull'intera larghezza
      const frac = Math.min(1, Math.max(0, (relX * W - padL) / plotW));
      const i = Math.round(frac * (n - 1));
      const px = x(i), py = y(series[i].clicks);
      cross.setAttribute("x1", px); cross.setAttribute("x2", px); cross.style.display = "";
      dot.setAttribute("cx", px); dot.setAttribute("cy", py); dot.style.display = "";
      tip.classList.remove("hidden");
      tip.style.left = (px / W) * 100 + "%";
      tip.style.top = (py / H) * 100 + "%";
      tip.innerHTML = `<strong>${fmtInt(series[i].clicks)}</strong> clicks<br>${esc(shortDate(series[i].date))}`;
    }
    function onLeave() {
      cross.style.display = "none";
      dot.style.display = "none";
      tip.classList.add("hidden");
    }
    hit.addEventListener("mousemove", onMove);
    hit.addEventListener("mouseleave", onLeave);
  }

  // --- Rendering tabelle/stat ------------------------------------------------
  function renderOverview(o) {
    const label = document.getElementById("range-label");
    if (label) {
      label.textContent = t("overviewRangeLabel", {
        days: o.range.days,
        start: o.range.start,
        end: o.range.end,
      });
    }
    const stat = (title, value, deltaHtml) => `
      <div class="stat">
        <div class="stat-title">${title}</div>
        <div class="stat-value text-2xl">${value}</div>
        <div class="stat-desc">${deltaHtml}</div>
      </div>`;
    document.getElementById("overview-stats").innerHTML =
      stat(t("statClicks"), fmtInt(o.clicks.value), deltaBadge(o.clicks.delta_pct, false)) +
      stat(t("statImpressions"), fmtInt(o.impressions.value), deltaBadge(o.impressions.delta_pct, false)) +
      stat(t("statCtr"), fmtPct(o.ctr.value), deltaBadge(o.ctr.delta_pct, false)) +
      stat(t("statAvgPosition"), fmtPos(o.position.value), deltaBadge(o.position.delta_pct, true));
  }

  function aiCell(url) {
    const a = aiAnalyses[url];
    if (!a) return '<span class="text-base-content/30">—</span>';
    return (
      `<button class="btn btn-ghost btn-xs ai-open" data-url="${esc(url)}" aria-label="AI suggestions">` +
      `<span class="radial-progress ${scoreColor(a.score)}" style="--value:${a.score};--size:2.2rem;--thickness:3px;" role="progressbar">${a.score}</span>` +
      `</button>`
    );
  }

  function renderPages(pages) {
    const body = document.getElementById("pages-body");
    if (!pages.length) {
      body.innerHTML =
        `<tr><td colspan="8" class="text-center text-base-content/50 py-6">${t("noPageDataPeriod")}</td></tr>`;
      return;
    }
    body.innerHTML = pages
      .map((p, idx) => {
        const label = shortUrl(p.url);
        return `<tr>
          <td class="max-w-xs truncate" title="${esc(p.url)}">
            <a href="${esc(p.url)}" target="_blank" rel="noopener" class="link link-hover">${esc(label)}</a>
          </td>
          <td class="text-right">${fmtInt(p.clicks)}</td>
          <td class="text-right">${fmtInt(p.impressions)}</td>
          <td class="text-right">${fmtPct(p.ctr)}</td>
          <td class="text-right">${fmtPos(p.position)}</td>
          <td class="text-right">${deltaBadge(p.clicks_delta_pct, false)}</td>
          <td class="text-center">${starsHtml(p.stars, idx)}</td>
          <td class="text-center">${aiCell(p.url)}</td>
        </tr>`;
      })
      .join("");

    body.querySelectorAll(".ai-open").forEach((btn) => {
      btn.addEventListener("click", () => openAiModal(btn.dataset.url));
    });
  }

  function renderQueries(queries) {
    const body = document.getElementById("queries-body");
    if (!queries.length) {
      body.innerHTML =
        `<tr><td colspan="5" class="text-center text-base-content/50 py-6">${t("noQueryDataPeriod")}</td></tr>`;
      return;
    }
    body.innerHTML = queries
      .map(
        (q) => `<tr>
          <td class="max-w-xs truncate" title="${esc(q.query)}">${esc(q.query)}</td>
          <td class="text-right">${fmtInt(q.clicks)}</td>
          <td class="text-right">${fmtInt(q.impressions)}</td>
          <td class="text-right">${fmtPct(q.ctr)}</td>
          <td class="text-right">${fmtPos(q.position)}</td>
        </tr>`
      )
      .join("");
  }

  // --- Modal AI (stack di card, click per scorrere) --------------------------
  function openAiModal(url) {
    const a = aiAnalyses[url];
    if (!a) return;
    const radial = document.getElementById("ai-modal-radial");
    radial.style.setProperty("--value", a.score);
    radial.textContent = a.score;
    const col = scoreColor(a.score); // es. "text-success"
    radial.className = "radial-progress border-4 " + col + " " + col.replace("text-", "border-");

    const link = document.getElementById("ai-modal-url");
    link.href = url;
    link.textContent = shortUrl(url);

    const stack = document.getElementById("ai-modal-stack");
    const hint = document.getElementById("ai-modal-hint");
    const items = a.suggestions || [];
    if (!items.length) {
      stack.innerHTML = '<div class="card bg-base-100 border border-base-content text-center"><div class="card-body">No suggestions for this page.</div></div>';
      hint.style.display = "none";
    } else {
      hint.style.display = items.length > 1 ? "" : "none";
      stack.innerHTML = items
        .map(
          (s, i) =>
            `<div class="card bg-base-100 border border-base-content text-center"><div class="card-body">` +
            `<span class="text-xs text-base-content/40">${i + 1}/${items.length}</span>` +
            `<p>${esc(s)}</p></div></div>`
        )
        .join("");
      stack.onclick = () => {
        if (stack.children.length > 1) stack.appendChild(stack.firstElementChild);
      };
    }
    document.getElementById("ai-modal").showModal();
  }

  // --- AI controls -----------------------------------------------------------
  const aiToggle = document.getElementById("ai-toggle");
  const aiRun = document.getElementById("ai-run");
  const aiStatusText = document.getElementById("ai-status-text");

  function applyAiStatus(st) {
    aiAnalyses = st.analyses || {};
    aiToggle.checked = !!st.enabled;
    updateRunButton(st);
  }

  function updateRunButton(st) {
    const cooling = (st.cooldown_days_left || 0) > 0;
    aiRun.disabled = !st.enabled || cooling;
    if (!st.enabled) {
      aiStatusText.textContent = t("aiEnableHint");
    } else if (cooling) {
      aiStatusText.textContent = t("aiCooldownHint", { days: st.cooldown_days_left });
    } else if (st.last_run_at) {
      aiStatusText.textContent = t("aiReadyHint");
    } else {
      aiStatusText.textContent = t("aiFirstRunHint");
    }
  }

  const postForm = window.Common.postForm;

  aiToggle.addEventListener("change", async () => {
    const site = select.value;
    try {
      const res = await postForm(AI_TOGGLE_URL, { site, enabled: aiToggle.checked ? "true" : "false" });
      const st = await res.json();
      applyAiStatus(st);
    } catch (e) {
      aiStatusText.textContent = t("aiToggleError");
      aiToggle.checked = !aiToggle.checked;
    }
  });

  // L'analisi gira in background (coda RQ, vedi app/jobs/): la POST accoda
  // il job e ritorna subito un job_id, poi si fa polling finché non è
  // "finished"/"failed" invece di aspettarsi il risultato nella risposta.
  const AI_POLL_INTERVAL_MS = 2000;
  const AI_POLL_MAX_ATTEMPTS = 60; // ~2 minuti, poi si arrende con un errore

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  async function pollAiJob(jobId, site) {
    const statusUrl = AI_ANALYZE_STATUS_URL_TPL.replace("__job_id__", encodeURIComponent(jobId));
    for (let attempt = 0; attempt < AI_POLL_MAX_ATTEMPTS; attempt++) {
      await sleep(AI_POLL_INTERVAL_MS);
      let data;
      try {
        const res = await fetch(statusUrl + "?site=" + encodeURIComponent(site), {
          headers: { Accept: "application/json" },
        });
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

  aiRun.addEventListener("click", async () => {
    const site = select.value;
    aiRun.disabled = true;
    aiStatusText.textContent = t("aiRunning");
    try {
      const queueRes = await postForm(AI_ANALYZE_URL, { site });
      const queueData = await queueRes.json();
      if (!queueRes.ok) {
        if (queueRes.status === 429) {
          aiStatusText.textContent = t("aiCooldownError", { days: queueData.days_left });
        } else if (queueData.error === "disabled") {
          aiStatusText.textContent = t("aiDisabledError");
        } else {
          aiStatusText.textContent = t("aiFailedError");
        }
        return;
      }

      const outcome = await pollAiJob(queueData.job_id, site);
      const jobResult = outcome.job_result || {};
      if (outcome.status === "finished" && jobResult.ok && outcome.ai_status) {
        applyAiStatus(outcome.ai_status);
        renderPages(lastPages); // ridisegna con gli score aggiornati
        aiStatusText.textContent = t("aiRunComplete");
      } else if (jobResult.error === "ai_failed") {
        aiStatusText.textContent = t("aiProviderError");
      } else {
        aiStatusText.textContent = t("aiFailedError");
      }
    } catch (e) {
      aiStatusText.textContent = t("aiFailedError");
    } finally {
      updateRunButton({ enabled: aiToggle.checked, cooldown_days_left: 0, last_run_at: true });
    }
  });

  // --- Data flow -------------------------------------------------------------
  let lastPages = [];

  async function loadSite(siteUrl) {
    show("loading");
    try {
      const [insRes, aiRes] = await Promise.all([
        fetch(INSIGHTS_URL + "?site=" + encodeURIComponent(siteUrl) + "&days=" + currentDays, {
          headers: { Accept: "application/json" },
        }),
        fetch(AI_STATUS_URL + "?site=" + encodeURIComponent(siteUrl), {
          headers: { Accept: "application/json" },
        }),
      ]);
      if (!insRes.ok) throw new Error("HTTP " + insRes.status);
      const data = await insRes.json();
      if (aiRes.ok) applyAiStatus(await aiRes.json());

      lastPages = data.pages;
      renderChart(data.series);
      renderOverview(data.overview);
      renderPages(data.pages);
      renderQueries(data.queries);
      show("data");
    } catch (e) {
      showError(t("loadSiteDataError"));
    }
  }

  // Filtro periodo
  document.getElementById("period-filter").addEventListener("click", (ev) => {
    const btn = ev.target.closest("button[data-days]");
    if (!btn) return;
    currentDays = parseInt(btn.dataset.days, 10);
    document.querySelectorAll("#period-filter button").forEach((b) => b.classList.toggle("btn-active", b === btn));
    if (select.value) loadSite(select.value);
  });

  async function init() {
    show("loading");
    try {
      // Sorgente: solo i siti già aggiunti al monitoraggio (non tutte le
      // proprietà verificate GSC) — aggiungerne di nuovi si fa dalla pagina
      // Sites (/dashboard/sites), qui il selettore è un puro switcher.
      const res = await fetch(SITES_URL, { headers: { Accept: "application/json" } });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const { sites } = await res.json();
      if (!sites || !sites.length) {
        select.innerHTML = `<option>${esc(t("noSitesOption"))}</option>`;
        show("empty");
        return;
      }
      select.innerHTML = sites.map((s) => `<option value="${esc(s)}">${esc(s)}</option>`).join("");
      select.disabled = sites.length < 2;

      select.addEventListener("change", () => loadSite(select.value));
      loadSite(sites[0]);
    } catch (e) {
      showError(t("loadSitesReconnectError"));
    }
  }

  init();
})();

// Audit Presentations (app/templates/dashboard/audits.html): stessa coda RQ +
// polling di /ai/analyze (vedi app/static/js/insights.js::pollAiJob), qui su
// /dashboard/audits/generate + /dashboard/audits/generate-status/<job_id>.
(function () {
  "use strict";

  const script = document.getElementById("audits-script");
  if (!script) return;

  const GENERATE_URL = script.dataset.generateUrl;
  const STATUS_URL_TPL = script.dataset.statusUrlTpl;
  const VIEW_URL_BASE = script.dataset.viewUrlBase;
  const CREDITS_URL = script.dataset.creditsUrl;
  const LANG = script.dataset.lang || "en";

  const STRINGS = {
    en: {
      running: "Generating your presentation…",
      failed: "Something went wrong. Please try again.",
      noData: "No declining pages found for this site yet — nothing to put in a presentation.",
      providerError: "The AI provider is temporarily unavailable. Please try again shortly.",
      insufficient: "Not enough AI credits for this (costs %COST% credits).",
      buyCredits: "Buy AI credits",
      done: "Done! Opening your presentation…",
    },
    it: {
      running: "Sto generando la presentazione…",
      failed: "Qualcosa è andato storto. Riprova.",
      noData: "Nessuna pagina in calo trovata per questo sito — niente da mettere in presentazione.",
      providerError: "Il provider AI non è disponibile al momento. Riprova a breve.",
      insufficient: "Crediti AI insufficienti per questa richiesta (costa %COST% crediti).",
      buyCredits: "Compra crediti AI",
      done: "Fatto! Apro la tua presentazione…",
    },
  };
  const t = (key) => (STRINGS[LANG] && STRINGS[LANG][key]) || STRINGS.en[key];

  const form = document.getElementById("audit-generate-form");
  const select = document.getElementById("audit-site-select");
  const submitBtn = document.getElementById("audit-generate-submit");
  const statusEl = document.getElementById("audit-generate-status");

  const POLL_INTERVAL_MS = 2000;
  const POLL_MAX_ATTEMPTS = 90; // ~3 minuti

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  async function pollJob(jobId) {
    const statusUrl = STATUS_URL_TPL.replace("__job_id__", encodeURIComponent(jobId));
    for (let attempt = 0; attempt < POLL_MAX_ATTEMPTS; attempt++) {
      await sleep(POLL_INTERVAL_MS);
      let data;
      try {
        const res = await fetch(statusUrl, { headers: { Accept: "application/json" } });
        data = await res.json();
      } catch (e) {
        continue;
      }
      if (data.status === "finished" || data.status === "failed" || data.status === "not_found") {
        return data;
      }
    }
    return { status: "timeout" };
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const site = select.value;
      if (!site) return;

      submitBtn.disabled = true;
      statusEl.textContent = t("running");
      statusEl.classList.remove("text-error");

      try {
        const res = await window.Common.postForm(GENERATE_URL, { site });
        const data = await res.json();

        if (res.status === 402) {
          statusEl.innerHTML = "";
          const label = t("insufficient").replace("%COST%", data.cost);
          statusEl.appendChild(document.createTextNode(label + " "));
          if (data.upsell) {
            const a = document.createElement("a");
            a.href = CREDITS_URL;
            a.className = "link link-primary";
            a.textContent = t("buyCredits");
            statusEl.appendChild(a);
          }
          statusEl.classList.add("text-error");
          return;
        }
        if (!res.ok) {
          statusEl.textContent = t("failed");
          statusEl.classList.add("text-error");
          return;
        }

        const outcome = await pollJob(data.job_id);
        const jobResult = outcome.job_result || {};
        if (outcome.status === "finished" && jobResult.ok && outcome.presentation_id) {
          statusEl.textContent = t("done");
          window.location.href = VIEW_URL_BASE + outcome.presentation_id;
        } else if (jobResult.error === "no_data") {
          statusEl.textContent = t("noData");
          statusEl.classList.add("text-error");
        } else if (jobResult.error === "ai_failed") {
          statusEl.textContent = t("providerError");
          statusEl.classList.add("text-error");
        } else {
          statusEl.textContent = t("failed");
          statusEl.classList.add("text-error");
        }
      } catch (e) {
        statusEl.textContent = t("failed");
        statusEl.classList.add("text-error");
      } finally {
        submitBtn.disabled = false;
      }
    });
  }
})();

// Audit Presentations (app/templates/dashboard/audits.html): stessa coda RQ +
// polling di /ai/analyze (Common.pollJob), qui su
// /dashboard/audits/generate + /dashboard/audits/generate-status/<job_id>.
(function () {
  "use strict";

  const script = document.getElementById("audits-script");
  if (!script) return;

  const GENERATE_URL = script.dataset.generateUrl;
  const STATUS_URL_TPL = script.dataset.statusUrlTpl;
  const VIEW_URL_BASE = script.dataset.viewUrlBase;
  const CREDITS_URL = script.dataset.creditsUrl;
  const t = (key, vars) => window.I18N.t("audit" + key.charAt(0).toUpperCase() + key.slice(1), vars);

  const form = document.getElementById("audit-generate-form");
  const select = document.getElementById("audit-site-select");
  const submitBtn = document.getElementById("audit-generate-submit");
  const statusEl = document.getElementById("audit-generate-status");

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
          const label = t("insufficient", { cost: data.cost });
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

        const statusUrl = STATUS_URL_TPL.replace("__job_id__", encodeURIComponent(data.job_id));
        const outcome = await window.Common.pollJob(statusUrl, 90); // ~3 minuti
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

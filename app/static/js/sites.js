// Pagina "Sites" (dashboard/sites.html): elenca le proprietà Search Console
// verificate, distingue quelle già monitorate da quelle disponibili, e
// permette di aggiungere/rimuovere (vedi app/gsc/gsc.py — api_sites,
// api_monitored_site, api_monitored_site_remove).
(function () {
  "use strict";

  const script = document.getElementById("sites-script");
  if (!script) return;

  const t = (window.I18N && window.I18N.t) || ((k) => k);

  const SITES_URL = script.dataset.sitesUrl;
  const ADD_URL = script.dataset.addUrl;
  const REMOVE_URL = script.dataset.removeUrl;
  const SITE_LIMIT = parseInt(script.dataset.siteLimit, 10); // -1 = illimitato

  const loading = document.getElementById("sites-loading");
  const errorBox = document.getElementById("sites-error");
  const content = document.getElementById("sites-content");
  const monitoredList = document.getElementById("monitored-list");
  const monitoredEmpty = document.getElementById("monitored-empty");
  const availableList = document.getElementById("available-list");
  const availableEmpty = document.getElementById("available-empty");
  const limitHint = document.getElementById("site-limit-hint");
  const countBadge = document.getElementById("sites-count-badge");
  const feedback = document.getElementById("sites-feedback");

  const esc = window.Common.esc;
  const postForm = window.Common.postForm;

  function showFeedback(message, isError) {
    if (!feedback) return;
    feedback.textContent = message;
    feedback.classList.remove("hidden", "text-error", "text-success");
    feedback.classList.add(isError ? "text-error" : "text-success");
  }

  function updateCountBadge(monitoredCount) {
    if (!countBadge) return;
    if (SITE_LIMIT < 0) {
      countBadge.classList.add("hidden");
      return;
    }
    countBadge.textContent = t("sitesCount", { used: monitoredCount, limit: SITE_LIMIT });
    countBadge.classList.remove("hidden");
  }

  function renderMonitored(monitoredUrls) {
    monitoredList.innerHTML = "";
    monitoredEmpty.classList.toggle("hidden", monitoredUrls.length > 0);
    monitoredUrls.forEach((url) => {
      const row = document.createElement("div");
      row.className = "flex items-center justify-between gap-3 py-2";
      row.innerHTML =
        '<span class="text-sm truncate">' + esc(url) + "</span>" +
        '<button type="button" class="btn btn-ghost btn-xs text-error" data-remove="' + esc(url) + '">' +
        esc(t("removeSite")) + "</button>";
      monitoredList.appendChild(row);
    });
  }

  function renderAvailable(allSites, monitoredUrls, atLimit) {
    const monitoredSet = new Set(monitoredUrls);
    const available = allSites.filter((s) => !monitoredSet.has(s.siteUrl));
    availableList.innerHTML = "";
    availableEmpty.classList.toggle("hidden", available.length > 0);
    limitHint.classList.toggle("hidden", !(atLimit && available.length > 0));
    available.forEach((s) => {
      const row = document.createElement("div");
      row.className = "flex items-center justify-between gap-3 py-2";
      const disabledAttr = atLimit ? "disabled" : "";
      row.innerHTML =
        '<span class="text-sm truncate">' + esc(s.siteUrl) + "</span>" +
        '<button type="button" class="btn btn-primary btn-xs" data-add="' + esc(s.siteUrl) + '" ' + disabledAttr + ">" +
        esc(t("addSite")) + "</button>";
      availableList.appendChild(row);
    });
  }

  async function load() {
    loading.classList.remove("hidden");
    errorBox.classList.add("hidden");
    content.classList.add("hidden");
    try {
      const res = await fetch(SITES_URL, { headers: { Accept: "application/json" } });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      const monitored = data.monitored_site_urls || [];
      const atLimit = SITE_LIMIT >= 0 && monitored.length >= SITE_LIMIT;
      updateCountBadge(monitored.length);
      renderMonitored(monitored);
      renderAvailable(data.sites || [], monitored, atLimit);
      loading.classList.add("hidden");
      content.classList.remove("hidden");
    } catch (e) {
      loading.classList.add("hidden");
      errorBox.classList.remove("hidden");
    }
  }

  content.addEventListener("click", async (e) => {
    const addBtn = e.target.closest("[data-add]");
    const removeBtn = e.target.closest("[data-remove]");

    if (addBtn) {
      addBtn.disabled = true;
      const res = await postForm(ADD_URL, { site: addBtn.dataset.add });
      if (res.ok) {
        showFeedback(t("siteAdded"), false);
        load();
      } else {
        const data = await res.json().catch(() => ({}));
        showFeedback(data.message || t("addSiteError"), true);
        addBtn.disabled = false;
      }
    }

    if (removeBtn) {
      removeBtn.disabled = true;
      const res = await postForm(REMOVE_URL, { site: removeBtn.dataset.remove });
      if (res.ok) {
        showFeedback(t("siteRemoved"), false);
        load();
      } else {
        showFeedback(t("removeSiteError"), true);
        removeBtn.disabled = false;
      }
    }
  });

  load();
})();

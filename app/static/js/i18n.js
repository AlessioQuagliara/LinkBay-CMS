// Dizionario i18n per gli script client-side della dashboard (overview.js,
// insights.js, declining.js). Flask-Babel copre Python+Jinja; qui copriamo il
// testo generato via JS, che Babel non vede. La lingua corrente arriva da
// `window.APP_LOCALE` (impostato dal template da get_locale()).
window.I18N = (function () {
  "use strict";

  const DICTS = {
    en: {
      // overview.js
      noPriorData: "no prior data",
      vsPrev: "vs prev.",
      newDelta: "new",
      noPageData: "No page data yet for this period.",
      rangeLabel: "{start} – {end} · last {days} days",
      loadInsightsError: "We couldn't load your Search Console data. Please try again.",
      loadSitesError: "We couldn't reach your connected account. Try reconnecting from Connector.",
      statClicks: "Clicks",
      statImpressions: "Impressions",
      statAvgPosition: "Avg. position",
      statCtr: "CTR",

      // insights.js
      notEnoughHistory: "Not enough history yet — data will build up day by day.",
      overviewRangeLabel: "Last {days} days ({start} → {end}) vs previous {days} days",
      noPageDataPeriod: "No page data in this period.",
      noQueryDataPeriod: "No query data in this period.",
      loadSitesReconnectError: "Couldn't load your Search Console sites. Please reconnect and try again.",
      loadSiteDataError: "Couldn't load data for this site. Please try again.",
      aiEnableHint: "Enable to get weekly AI suggestions per page.",
      aiCooldownHint: "Runs weekly. Next run available in {days} day(s).",
      aiReadyHint: "Weekly. You can run a fresh analysis now.",
      aiFirstRunHint: "Enabled — run your first analysis now.",
      aiToggleError: "Couldn't update the AI setting. Try again.",
      aiRunning: "Analyzing your pages with AI…",
      aiRunComplete: "Analysis complete — open the AI column for suggestions.",
      aiCooldownError: "Already run recently. Next run in {days} day(s).",
      aiProviderError: "AI provider error (check DEEPSEEK_API on the server).",
      aiDisabledError: "Enable the AI analyzer first.",
      aiFailedError: "Analysis failed. Try again later.",

      // declining.js
      statusNew: "New",
      statusAcknowledged: "Acknowledged",
      statusDone: "Done",
      statusRecovered: "Recovered",
      priorityHigh: "high",
      priorityMedium: "medium",
      priorityLow: "low",
      priorityBadge: "Priority {label}",
      scoreLabel: "score {score}",
      notEnoughHistoryTrend: "Not enough history for the trend.",
      noDecliningQueries: "No declining queries for this page.",
      colQuery: "Query",
      colClicksLost: "Clicks lost",
      colPosition: "Position",
      changeStatus: "Change status",
      clicksLostPerMonth: "Clicks lost/month",
      seeTrend: "See 6-month trend",
      loading: "Loading…",
      queriesThatLostRankings: "Queries that lost rankings",
      updateStatusError: "Couldn't update status. Please try again.",
      trendNotAvailable: "Trend not available.",
      queriesNotAvailable: "Queries not available.",
      loadListError: "Couldn't load the list. Please try again.",

      // sites.js
      removeSite: "Remove",
      addSite: "Add",
      sitesCount: "{used} of {limit} sites",
      siteAdded: "Site added.",
      siteRemoved: "Site removed.",
      addSiteError: "Couldn't add this site. Please try again.",
      removeSiteError: "Couldn't remove this site. Please try again.",
      noSitesOption: "No sites monitored yet",
    },
    it: {
      noPriorData: "nessun dato precedente",
      vsPrev: "vs prec.",
      newDelta: "nuova",
      noPageData: "Nessun dato pagina per questo periodo.",
      rangeLabel: "{start} – {end} · ultimi {days} giorni",
      loadInsightsError: "Non è stato possibile caricare i dati di Search Console. Riprova.",
      loadSitesError: "Non è stato possibile raggiungere il tuo account collegato. Riprova a connetterti da Connettore.",
      statClicks: "Click",
      statImpressions: "Impression",
      statAvgPosition: "Posizione media",
      statCtr: "CTR",

      notEnoughHistory: "Storico ancora insufficiente — i dati si accumuleranno giorno per giorno.",
      overviewRangeLabel: "Ultimi {days} giorni ({start} → {end}) rispetto ai {days} giorni precedenti",
      noPageDataPeriod: "Nessun dato pagina in questo periodo.",
      noQueryDataPeriod: "Nessun dato query in questo periodo.",
      loadSitesReconnectError: "Non è stato possibile caricare i siti di Search Console. Riconnettiti e riprova.",
      loadSiteDataError: "Non è stato possibile caricare i dati per questo sito. Riprova.",
      aiEnableHint: "Attiva per ricevere suggerimenti AI settimanali per pagina.",
      aiCooldownHint: "Esecuzione settimanale. Prossima disponibile tra {days} giorno/i.",
      aiReadyHint: "Settimanale. Puoi eseguire subito una nuova analisi.",
      aiFirstRunHint: "Attivato — esegui ora la prima analisi.",
      aiToggleError: "Non è stato possibile aggiornare l'impostazione AI. Riprova.",
      aiRunning: "Analisi delle pagine con l'AI in corso…",
      aiRunComplete: "Analisi completata — apri la colonna AI per i suggerimenti.",
      aiCooldownError: "Già eseguita di recente. Prossima esecuzione tra {days} giorno/i.",
      aiProviderError: "Errore del provider AI (verifica DEEPSEEK_API sul server).",
      aiDisabledError: "Attiva prima l'analizzatore AI.",
      aiFailedError: "Analisi non riuscita. Riprova più tardi.",

      statusNew: "Nuova",
      statusAcknowledged: "Riconosciuta",
      statusDone: "Fatta",
      statusRecovered: "Recuperata",
      priorityHigh: "alta",
      priorityMedium: "media",
      priorityLow: "bassa",
      priorityBadge: "Priorità {label}",
      scoreLabel: "punteggio {score}",
      notEnoughHistoryTrend: "Storico insufficiente per il trend.",
      noDecliningQueries: "Nessuna query in calo per questa pagina.",
      colQuery: "Query",
      colClicksLost: "Click persi",
      colPosition: "Posizione",
      changeStatus: "Cambia stato",
      clicksLostPerMonth: "Click persi/mese",
      seeTrend: "Vedi trend 6 mesi",
      loading: "Caricamento…",
      queriesThatLostRankings: "Query che hanno perso posizioni",
      updateStatusError: "Non è stato possibile aggiornare lo stato. Riprova.",
      trendNotAvailable: "Trend non disponibile.",
      queriesNotAvailable: "Query non disponibili.",
      loadListError: "Non è stato possibile caricare la lista. Riprova.",

      removeSite: "Rimuovi",
      addSite: "Aggiungi",
      sitesCount: "{used} di {limit} siti",
      siteAdded: "Sito aggiunto.",
      siteRemoved: "Sito rimosso.",
      addSiteError: "Non è stato possibile aggiungere il sito. Riprova.",
      removeSiteError: "Non è stato possibile rimuovere il sito. Riprova.",
      noSitesOption: "Nessun sito ancora monitorato",
    },
  };

  const locale = DICTS[window.APP_LOCALE] ? window.APP_LOCALE : "en";

  function t(key, vars) {
    let s = (DICTS[locale] && DICTS[locale][key]) || DICTS.en[key] || key;
    if (vars) {
      Object.keys(vars).forEach((k) => {
        s = s.split("{" + k + "}").join(vars[k]);
      });
    }
    return s;
  }

  return { t: t, locale: locale };
})();

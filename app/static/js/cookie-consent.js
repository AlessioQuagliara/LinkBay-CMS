/*
 * Gestione consenso cookie — salva DAVVERO le preferenze dell'utente.
 *
 * Dove vengono salvate:
 *  - cookie first-party `lb_consent` (JSON url-encoded, 180 giorni): è la fonte
 *    di verità e, essendo un cookie, è leggibile anche lato server Flask con
 *    request.cookies.get("lb_consent") se un domani serve gating server-side.
 *  - copia in localStorage `lb_consent` come backup/lettura rapida dal client.
 *
 * Categorie:
 *  - necessary  : sempre attive, non disattivabili (funzionamento del sito).
 *  - analytics  : misurazione anonima del traffico.
 *  - marketing  : remarketing / annunci.
 *
 * Quando l'utente salva, viene emesso l'evento `lb:consent` sul document con
 * detail = { necessary, analytics, marketing }: gli script di terze parti
 * (es. Google Analytics) vanno caricati SOLO in ascolto di questo evento, così
 * partono unicamente con il consenso dato.
 */
;(function () {
  const COOKIE_NAME = "lb_consent"
  // Alza questa versione quando cambiano le categorie o l'informativa: i
  // consensi salvati con una versione diversa vengono considerati scaduti e il
  // banner viene rimostrato per raccogliere di nuovo la scelta.
  const VERSION = 1
  const MAX_AGE_DAYS = 180

  const DEFAULTS = { necessary: true, analytics: false, marketing: false }

  function isHttps() {
    return window.location.protocol === "https:"
  }

  function writeCookie(value) {
    const maxAge = MAX_AGE_DAYS * 24 * 60 * 60
    let cookie =
      COOKIE_NAME +
      "=" +
      encodeURIComponent(value) +
      "; Max-Age=" +
      maxAge +
      "; Path=/; SameSite=Lax"
    if (isHttps()) cookie += "; Secure"
    document.cookie = cookie
  }

  function readCookie() {
    const match = document.cookie.match(
      new RegExp("(?:^|; )" + COOKIE_NAME + "=([^;]*)")
    )
    return match ? decodeURIComponent(match[1]) : null
  }

  function loadConsent() {
    const raw = readCookie() || window.localStorage.getItem(COOKIE_NAME)
    if (!raw) return null
    try {
      const parsed = JSON.parse(raw)
      if (!parsed || parsed.version !== VERSION) return null
      return parsed
    } catch (e) {
      return null
    }
  }

  function saveConsent(categories) {
    const record = {
      version: VERSION,
      timestamp: new Date().toISOString(),
      necessary: true, // sempre attive
      analytics: !!categories.analytics,
      marketing: !!categories.marketing,
    }
    const serialized = JSON.stringify(record)
    writeCookie(serialized)
    try {
      window.localStorage.setItem(COOKIE_NAME, serialized)
    } catch (e) {
      /* localStorage non disponibile: il cookie basta */
    }
    document.dispatchEvent(new CustomEvent("lb:consent", { detail: record }))
    return record
  }

  // --- UI -----------------------------------------------------------------

  const banner = document.getElementById("cookie-banner")
  const modal = document.getElementById("cookie-modal")
  const toggleAnalytics = document.getElementById("cookie-toggle-analytics")
  const toggleMarketing = document.getElementById("cookie-toggle-marketing")

  function showBanner() {
    if (banner) banner.classList.remove("hidden")
  }
  function hideBanner() {
    if (banner) banner.classList.add("hidden")
  }
  function openModal(current) {
    if (!modal) return
    const c = current || loadConsent() || DEFAULTS
    if (toggleAnalytics) toggleAnalytics.checked = !!c.analytics
    if (toggleMarketing) toggleMarketing.checked = !!c.marketing
    modal.showModal()
  }
  function closeModal() {
    if (modal) modal.close()
  }

  function acceptAll() {
    saveConsent({ analytics: true, marketing: true })
    hideBanner()
    closeModal()
  }
  function rejectAll() {
    saveConsent({ analytics: false, marketing: false })
    hideBanner()
    closeModal()
  }
  function saveSelection() {
    saveConsent({
      analytics: toggleAnalytics ? toggleAnalytics.checked : false,
      marketing: toggleMarketing ? toggleMarketing.checked : false,
    })
    hideBanner()
    closeModal()
  }

  // Wiring dei bottoni tramite data-attribute, così l'HTML resta pulito.
  document.querySelectorAll("[data-cookie-action]").forEach((el) => {
    el.addEventListener("click", (e) => {
      const action = el.getAttribute("data-cookie-action")
      if (action === "accept") acceptAll()
      else if (action === "reject") rejectAll()
      else if (action === "save") saveSelection()
      else if (action === "prefs") {
        e.preventDefault()
        openModal()
      }
    })
  })

  // Primo caricamento: se non c'è ancora un consenso valido, mostra il banner.
  const existing = loadConsent()
  if (!existing) {
    showBanner()
  } else {
    // Riemette l'evento così gli script condizionati partono anche nelle
    // visite successive senza ripresentare il banner.
    document.dispatchEvent(new CustomEvent("lb:consent", { detail: existing }))
  }

  // API pubblica per riaprire le preferenze (link nel footer / cookie policy)
  // e per leggere lo stato dagli script che ne dipendono.
  window.LBConsent = {
    open: () => openModal(),
    get: () => loadConsent(),
    has: (category) => {
      const c = loadConsent()
      return !!(c && c[category])
    },
  }
})()

"""I filtri della sezione 4 del business plan, uno per riga della tabella.

Ogni filtro è una funzione pura con la stessa firma di base
`(series, [site,] t) -> FilterResult`, così l'ordine è configurabile e ognuno è
testabile in isolamento (ARCHITECTURE.md §9). Nessuna dipendenza esterna.
"""
from app.rules.types import FilterResult, PageSeries, SiteSeries, Thresholds


def _clicks(monthly: list[dict]) -> list[int]:
    return [int(m["clicks"]) for m in monthly]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _pct_change(current: float, previous: float) -> float:
    """Variazione percentuale current vs previous. Se previous è <= 0 non c'è
    un calo misurabile: ritorna 0.0 (il filtro non scatterà)."""
    if previous <= 0:
        return 0.0
    return (current - previous) / previous * 100.0


def passes_relevance(series: PageSeries, t: Thresholds) -> FilterResult:
    """Sez. 4: soglia minima di rilevanza. Il mese migliore deve aver fatto
    almeno `min_clicks_best_month` click."""
    clicks = _clicks(series.monthly)
    best = max(clicks) if clicks else 0
    ok = best >= t.min_clicks_best_month
    return FilterResult(
        passed=ok,
        reason=None if ok else f"mese migliore solo {best} click",
        data={"best_month_clicks": best},
    )


def compute_window_averages(series: PageSeries, t: Thresholds):
    """Helper (non un filtro): media click degli ultimi `window_months` mesi e
    dei `window_months` precedenti. Servono almeno 2*window_months mesi di
    storico, altrimenti ritorna (None, None)."""
    w = t.window_months
    clicks = _clicks(series.monthly)
    if len(clicks) < 2 * w:
        return None, None
    current = _mean(clicks[-w:])
    previous = _mean(clicks[-2 * w:-w])
    return current, previous


def passes_pct_loss(current_avg: float, previous_avg: float, t: Thresholds) -> FilterResult:
    """Sez. 4: perdita minima in percentuale (es. -35% passa, -20% no)."""
    pct = _pct_change(current_avg, previous_avg)
    ok = pct <= t.min_pct_loss
    return FilterResult(
        passed=ok,
        reason=None if ok else f"calo solo {pct:.1f}%",
        data={"click_loss_pct": pct},
    )


def passes_abs_loss(current_avg: float, previous_avg: float, t: Thresholds) -> FilterResult:
    """Sez. 4: perdita minima assoluta in click/mese (es. -20)."""
    diff = current_avg - previous_avg
    ok = diff <= t.min_abs_loss
    return FilterResult(
        passed=ok,
        reason=None if ok else f"calo solo {diff:.0f} click/mese",
        data={"click_loss_abs": int(round(diff))},
    )


def passes_persistence(series: PageSeries, t: Thresholds) -> FilterResult:
    """Sez. 4: persistenza. Il calo rispetto alla media dei `window_months`
    precedenti deve esserci in almeno `persistence_months` mesi consecutivi tra
    gli ultimi `window_months`."""
    w = t.window_months
    _, previous = compute_window_averages(series, t)
    if previous is None:
        return FilterResult(passed=False, reason="storico insufficiente", data={})

    last_window = _clicks(series.monthly)[-w:]
    best_run = run = 0
    for c in last_window:
        if c < previous:  # mese in calo rispetto alla baseline precedente
            run += 1
            best_run = max(best_run, run)
        else:
            run = 0
    ok = best_run >= t.persistence_months
    return FilterResult(
        passed=ok,
        reason=None if ok else f"calo consecutivo solo per {best_run} mese/i",
        data={"consecutive_drop_months": best_run},
    )


def check_seasonality(series: PageSeries, t: Thresholds) -> FilterResult:
    """Sez. 4: filtro stagionalità. Se lo storico supera i 13 mesi, confronta la
    media dell'ultimo trimestre con lo stesso trimestre dell'anno prima.

    - non applicabile (storico troppo corto per un confronto allineato):
      passed=True, yoy_applicable=False (verrà segnalato nel testo — vedi il
      ramo "Filtro stagionalità non applicabile" in ARCHITECTURE.md §9);
    - applicabile e il calo si conferma anche vs anno prima: passed=True;
    - applicabile ma stesso trimestre uguale/migliore dell'anno prima: è
      stagionalità, passed=False.
    """
    w = t.window_months
    clicks = _clicks(series.monthly)
    n = len(clicks)

    if n <= 13:
        return FilterResult(passed=True, reason=None, data={"yoy_applicable": False})

    # Trimestre di un anno fa, allineato all'ultimo trimestre (12 mesi prima).
    year_ago = clicks[n - w - 12:n - 12]
    if len(year_ago) < w:
        # Storico > 13 mesi ma non abbastanza per un confronto allineato.
        return FilterResult(passed=True, reason=None, data={"yoy_applicable": False})

    last_q = _mean(clicks[-w:])
    year_ago_avg = _mean(year_ago)
    yoy_pct = _pct_change(last_q, year_ago_avg)
    confirmed = yoy_pct <= t.min_pct_loss
    return FilterResult(
        passed=confirmed,
        reason=None if confirmed else "il calo c'era anche l'anno scorso: stagionalità",
        data={
            "yoy_applicable": True,
            "yoy_confirmed": confirmed,
            "yoy_pct": yoy_pct,
        },
    )


def passes_site_relative(series: PageSeries, site: SiteSeries, t: Thresholds) -> FilterResult:
    """Sez. 4: colpa del sito o colpa della pagina. Il calo % della pagina deve
    essere almeno `site_relative_margin` punti percentuali peggiore del calo %
    medio del sito nello stesso periodo."""
    w = t.window_months

    page_clicks = _clicks(series.monthly)
    page_pct = _pct_change(_mean(page_clicks[-w:]), _mean(page_clicks[-2 * w:-w]))

    site_clicks = _clicks(site.monthly)
    if len(site_clicks) < 2 * w:
        # Senza storico di sito confrontabile non possiamo attribuire la colpa:
        # non scartiamo la pagina, ma non c'è nulla da confrontare.
        site_pct = 0.0
    else:
        site_pct = _pct_change(_mean(site_clicks[-w:]), _mean(site_clicks[-2 * w:-w]))

    relative = page_pct - site_pct  # più negativo = pagina peggiore del sito
    ok = page_pct <= site_pct - t.site_relative_margin
    return FilterResult(
        passed=ok,
        reason=None if ok else f"segue la corrente del sito (pagina {page_pct:.0f}%, sito {site_pct:.0f}%)",
        data={
            "page_pct": page_pct,
            "site_pct": site_pct,
            "site_relative_drop_pct": relative,
        },
    )

"""Test del rule engine con dati sintetici passati a mano (niente DB né Flask).

Eseguibile sia con pytest sia direttamente: `python3 tests/test_rules.py`.
Copre i cinque casi limite richiesti (BUSINESS_PLAN.md §4).
"""
import os
import sys
import types
from datetime import date

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

# app/rules/ non importa nulla di Flask (vincolo ARCHITECTURE.md §4), ma il
# package genitore app/__init__.py sì. Per testare le regole in vero isolamento
# — senza Flask e senza avviare l'applicazione — registriamo uno stub del
# package `app` che punta alla cartella reale ma non esegue il suo __init__.
if "app" not in sys.modules:
    _app_pkg = types.ModuleType("app")
    _app_pkg.__path__ = [os.path.join(_ROOT, "app")]
    sys.modules["app"] = _app_pkg

from app.rules.engine import evaluate_page, evaluate_site  # noqa: E402
from app.rules.types import PageSeries, SiteSeries  # noqa: E402


# --- Costruzione dati sintetici --------------------------------------------

def _month_seq(n):
    out, y, m = [], 2023, 1
    for _ in range(n):
        out.append(date(y, m, 1))
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return out


def _monthly(clicks, impressions=None, positions=None):
    n = len(clicks)
    months = _month_seq(n)
    impressions = impressions if impressions is not None else [10000] * n
    positions = positions if positions is not None else [10.0] * n
    return [
        {
            "month": months[i],
            "clicks": clicks[i],
            "impressions": impressions[i],
            "ctr": 0.05,
            "position": positions[i],
        }
        for i in range(n)
    ]


def _page(url, clicks, impressions=None, positions=None):
    return PageSeries(url=url, monthly=_monthly(clicks, impressions, positions))


def _site(clicks, impressions=None, positions=None):
    return SiteSeries(monthly=_monthly(clicks, impressions, positions))


# --- I cinque casi ----------------------------------------------------------

def test_page_passes_all_filters():
    """Calo forte, isolato dal sito, storico breve: deve produrre un candidate."""
    page = _page(
        "https://esempio.it/guida",
        clicks=[1000, 1000, 1000, 600, 550, 600],
        impressions=[20000] * 6,
        positions=[3.0, 3.0, 3.0, 11.0, 11.0, 11.0],
    )
    site = _site([100000, 100000, 100000, 98000, 98000, 98000])

    cand = evaluate_page(page, site)
    assert cand is not None
    assert cand.best_month_clicks == 1000
    assert cand.click_loss_pct <= -30.0
    assert cand.click_loss_abs <= -20
    assert cand.position_before == 3.0
    assert cand.position_after == 11.0
    assert cand.site_relative_drop_pct < 0  # peggiore del sito
    assert cand.reason_text.strip() != ""


def test_page_below_relevance_returns_none():
    """Mese migliore sotto i 50 click: irrilevante, deve tornare None."""
    page = _page("https://esempio.it/nicchia", clicks=[12, 10, 11, 8, 9, 7])
    site = _site([100000, 100000, 100000, 98000, 98000, 98000])

    assert evaluate_page(page, site) is None


def test_seasonality_explains_drop_returns_none():
    """Stesso trimestre dell'anno prima uguale a quello attuale: è stagionalità,
    deve tornare None anche se i primi filtri passano."""
    # 15 mesi: anno-fa (idx 0-2) == ultimo trimestre (idx 12-14) == 600.
    clicks = [600, 600, 600, 800, 800, 800, 800, 800, 800, 1000, 1000, 1000, 600, 600, 600]
    page = _page("https://esempio.it/costumi", clicks=clicks)
    site = _site([100000] * 15)

    assert evaluate_page(page, site) is None


def test_page_follows_site_drop_returns_none():
    """Calo identico a quello medio del sito: segue la corrente, filtro
    site-relative lo scarta -> None."""
    page = _page(
        "https://esempio.it/segue-il-sito",
        clicks=[1000, 1000, 1000, 700, 700, 700],
    )
    site = _site([100000, 100000, 100000, 70000, 70000, 70000])  # anche il sito -30%

    assert evaluate_page(page, site) is None


def test_isolated_real_drop_has_reason_text():
    """Calo reale e isolato dal sito: candidate con reason_text non vuoto."""
    page = _page(
        "https://esempio.it/calo-vero",
        clicks=[2000, 2000, 2000, 800, 700, 750],
        impressions=[30000] * 6,
        positions=[3.0, 3.0, 3.0, 12.0, 12.0, 12.0],
    )
    site = _site([100000] * 6)  # sito piatto

    cand = evaluate_page(page, site)
    assert cand is not None
    assert cand.reason_text.strip() != ""
    assert "click" in cand.reason_text
    # una frase per riga
    assert len(cand.reason_text.splitlines()) >= 4


def test_evaluate_site_sorts_and_drops_none():
    """evaluate_site scarta i None e ordina per priorità decrescente."""
    winner = _page(
        "https://esempio.it/grande",
        clicks=[4000, 4000, 4000, 900, 900, 900],
        impressions=[50000] * 6,
        positions=[3.0, 3.0, 3.0, 11.0, 11.0, 11.0],
    )
    smaller = _page(
        "https://esempio.it/piccola",
        clicks=[200, 200, 200, 120, 110, 120],
        impressions=[5000] * 6,
        positions=[8.0, 8.0, 8.0, 15.0, 15.0, 15.0],
    )
    irrelevant = _page("https://esempio.it/nulla", clicks=[5, 4, 6, 3, 2, 3])
    site = _site([100000] * 6)

    result = evaluate_site([smaller, irrelevant, winner], site)
    urls = [c.url for c in result]
    assert "https://esempio.it/nulla" not in urls
    assert result[0].priority_score >= result[-1].priority_score
    assert result[0].url == "https://esempio.it/grande"


# --- Runner standalone (senza pytest) --------------------------------------

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"ERROR {fn.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passati")
    sys.exit(1 if failed else 0)

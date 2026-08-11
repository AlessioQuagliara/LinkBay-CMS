"""Tipi del rule engine: sole dataclass, nessuna dipendenza da Flask/SQLAlchemy.

Le serie mensili sono liste di dict `{month, clicks, impressions, ctr,
position}` ordinate dal mese più vecchio al più recente — stessa forma che
produce app/gsc/page_history.get_page_series.
"""
from dataclasses import dataclass, field


@dataclass
class PageSeries:
    """Storico mensile di una singola pagina (ordinato vecchio → recente)."""

    url: str
    monthly: list[dict]  # ogni dict: {month: date, clicks, impressions, ctr, position}


@dataclass
class SiteSeries:
    """Storico mensile aggregato dell'intero sito (stessa forma di monthly)."""

    monthly: list[dict]


@dataclass
class Thresholds:
    """Soglie del filtro (BUSINESS_PLAN.md §4). Valori di partenza, non verità:
    ogni sito deve poterle stringere o allargare."""

    min_clicks_best_month: int = 50
    min_pct_loss: float = -30.0
    min_abs_loss: int = -20
    window_months: int = 3
    persistence_months: int = 2
    site_relative_margin: float = 10.0


@dataclass
class FilterResult:
    """Esito di un singolo filtro. `reason` è valorizzato solo quando il filtro
    fallisce e serve alla taratura (ARCHITECTURE.md §9), non finisce nella lista
    utente. `data` porta i numeri calcolati, riusati dallo scoring."""

    passed: bool
    reason: str | None
    data: dict = field(default_factory=dict)


@dataclass
class AlertCandidate:
    """Una pagina che ha superato tutti i filtri, pronta per la lista utente."""

    url: str
    best_month_clicks: int
    click_loss_abs: int
    click_loss_pct: float
    position_before: float
    position_after: float
    impressions_trend_pct: float
    site_relative_drop_pct: float
    yoy_confirmed: bool
    yoy_applicable: bool
    priority_score: float
    reason_text: str

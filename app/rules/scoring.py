"""Punteggio di priorità (BUSINESS_PLAN.md §5, ARCHITECTURE.md §10) e testo di
motivazione deterministico.

Quattro score 0-100 combinati con pesi fissi. Il testo è generato da un template
deterministico, mai da un modello linguistico: la credibilità della lista è
l'unico patrimonio del prodotto (BUSINESS_PLAN.md §6), e la frase è sempre la
stessa struttura con numeri diversi.
"""
import math

from app.rules.types import AlertCandidate

# Riferimenti di normalizzazione (valori di partenza, da tarare sui siti reali).
_VALUE_MAX_CLICKS = 100000  # ~5 in log10: satura lo score del valore
_POS_BEST = 10.0            # cima della pagina 2: massima recuperabilità
_POS_WORST = 70.0           # oltre qui, poco recuperabile


def value_score(best_month_clicks: int) -> float:
    """Quanto valeva prima. Scala logaritmica su best_month_clicks, 0-100."""
    raw = math.log10(max(0, best_month_clicks) + 1) / math.log10(_VALUE_MAX_CLICKS)
    return max(0.0, min(100.0, raw * 100.0))


def severity_score(click_loss_pct: float) -> float:
    """Quanto sta perdendo. Più negativo il calo, più alto lo score, 0-100."""
    return max(0.0, min(100.0, abs(click_loss_pct)))


def recoverability_score(position_before: float, position_after: float) -> float:
    """Quanto è facile da recuperare. Alto se la posizione attuale è vicina alla
    prima pagina (pos 11 molto recuperabile, pos 60 poco), 0-100."""
    span = _POS_WORST - _POS_BEST
    raw = (_POS_WORST - position_after) / span * 100.0
    return max(0.0, min(100.0, raw))


def demand_score(impressions_trend_pct: float) -> float:
    """La domanda c'è ancora? Alto se le impression sono rimaste stabili/alte
    (problema di posizionamento), basso se sono crollate anche loro, 0-100."""
    return max(0.0, min(100.0, 100.0 + impressions_trend_pct))


def priority_score(value: float, severity: float, recoverability: float, demand: float) -> float:
    """Combinazione pesata (ARCHITECTURE.md §10): prima le pagine dove si
    guadagna tanto e si fatica poco."""
    return (
        value * 0.35
        + severity * 0.25
        + recoverability * 0.20
        + demand * 0.20
    )


# --- Testo della motivazione ------------------------------------------------

def _it_int(n: float) -> str:
    """Intero con il punto come separatore delle migliaia (stile italiano)."""
    return f"{int(round(n)):,}".replace(",", ".")


def _it_dec(n: float) -> str:
    """Un decimale con la virgola (stile italiano)."""
    return f"{n:.1f}".replace(".", ",")


def _priority_label(score: float) -> str:
    if score >= 66:
        return "alta"
    if score >= 33:
        return "media"
    return "bassa"


def build_reason_text(candidate: AlertCandidate, window_months: int = 3) -> str:
    """Genera la spiegazione in italiano semplice, una frase per riga, nello
    stile dell'esempio in BUSINESS_PLAN.md §3."""
    loss = _it_int(abs(candidate.click_loss_abs))
    lines = [
        f"Ha perso {loss} click al mese negli ultimi {window_months} mesi.",
        f"Era in posizione media {_it_dec(candidate.position_before)}, "
        f"ora è {_it_dec(candidate.position_after)}.",
    ]

    # Calo del sito nello stesso periodo, ricavato dallo scarto relativo.
    site_pct = candidate.click_loss_pct - candidate.site_relative_drop_pct
    lines.append(
        f"Il resto del sito nello stesso periodo è sceso solo del "
        f"{_it_int(abs(site_pct))}%: questa pagina sta scendendo per conto suo."
    )

    # La domanda: impressioni tenute o crollate.
    if candidate.impressions_trend_pct >= -15:
        lines.append(
            "Le impressioni sono rimaste alte: la domanda c'è ancora, "
            "il problema è il posizionamento."
        )
    else:
        lines.append(
            "Le impressioni sono calate: parte della domanda è venuta meno."
        )

    # Stagionalità: confermata, o non verificabile (va segnalato — ARCH §9).
    if not candidate.yoy_applicable:
        lines.append(
            "Storico troppo breve per confrontare con lo stesso periodo "
            "dell'anno scorso."
        )
    elif candidate.yoy_confirmed:
        lines.append(
            "Il calo si conferma anche rispetto allo stesso periodo dell'anno scorso."
        )

    # Riga di priorità.
    label = _priority_label(candidate.priority_score)
    rationale_parts = []
    if candidate.best_month_clicks >= 1000:
        rationale_parts.append("valeva molto")
    if abs(candidate.click_loss_pct) >= 50:
        rationale_parts.append("sta perdendo molto")
    if candidate.position_after <= 20:
        rationale_parts.append("ed è a poca distanza dalla prima pagina")
    rationale = ", ".join(rationale_parts) if rationale_parts else "vale la pena guardarla"
    lines.append(f"Priorità {label}: {rationale}.")

    return "\n".join(lines)

"""Ledger dei crediti AI (solo per piani ai_mode == "credit" — Pro
mensile/annuale e, per la quota mensile, AppSumo Tier 3). I piani a
cooldown (AppSumo Tier 1/2) non toccano questo modulo: restano sul freno
esistente in app/ai/service.py.

I crediti non scadono (nessuna logica di expiry qui, a differenza della
cooldown settimanale) — un pacchetto acquistato resta valido finché non
viene consumato."""
from datetime import datetime, timezone

from app.extensions import db
from app.models import AiCreditTransaction, User


def grant_credits(
    user: User,
    amount: int,
    type: str,
    product_key: str | None = None,
    payment_reference: str | None = None,
    payment_source: str | None = None,
) -> AiCreditTransaction:
    """Accredita `amount` crediti (deve essere positivo). Aggiorna il saldo
    denormalizzato su User nella stessa transazione DB del ledger.

    Non fa commit: il webhook Paddle (app/webhooks/routes.py) deve scrivere
    accredito ed evento in UNA sola transazione, quindi committa il chiamante."""
    if amount <= 0:
        raise ValueError("grant_credits richiede un importo positivo.")

    balance_before = user.ai_credit_balance
    user.ai_credit_balance += amount
    entry = AiCreditTransaction(
        user_id=user.id,
        type=type,
        amount=amount,
        balance_before=balance_before,
        balance_after=user.ai_credit_balance,
        product_key=product_key,
        payment_reference=payment_reference,
        payment_source=payment_source,
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(entry)
    return entry


def consume_credits(
    user: User, amount: int, site_url: str | None = None, action: str | None = None
) -> AiCreditTransaction | None:
    """Consuma `amount` crediti. Ritorna None (nessun effetto collaterale) se
    il saldo non basta — il chiamante deve aver già verificato la
    disponibilità con app/entitlements/service.py::check_ai_credits prima di
    arrivare qui; questa è una difesa in profondità, non il controllo
    primario.

    `action` è solo per l'etichetta leggibile nello storico crediti (vedi
    app/models/ai_credit_transaction.py) — non cambia in alcun modo la
    quantità scalata."""
    if amount <= 0:
        raise ValueError("consume_credits richiede un importo positivo.")
    if user.ai_credit_balance < amount:
        return None

    user.ai_credit_balance -= amount
    entry = AiCreditTransaction(
        user_id=user.id,
        type="consume",
        action=action,
        amount=-amount,
        balance_after=user.ai_credit_balance,
        site_url=site_url,
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(entry)
    db.session.commit()
    return entry


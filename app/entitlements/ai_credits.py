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


def get_ai_credit_balance(user: User) -> int:
    return user.ai_credit_balance


def grant_credits(
    user: User,
    amount: int,
    type: str,
    ls_order_id: str | None = None,
    site_url: str | None = None,
    product_key: str | None = None,
    payment_reference: str | None = None,
    payment_source: str | None = None,
    approved_by_user_id: int | None = None,
    admin_note: str | None = None,
) -> AiCreditTransaction:
    """Accredita `amount` crediti (deve essere positivo — usa `adjustment`
    con importo negativo per uno storno, non questa funzione). Aggiorna il
    saldo denormalizzato su User nella stessa transazione DB del ledger.

    Gli ultimi cinque parametri sono usati solo dai top-up a pagamento (vedi
    app/billing/paddle_transactions.py) — restano None per gli altri
    chiamanti (quota mensile, storico Lemon Squeezy)."""
    if amount <= 0:
        raise ValueError("grant_credits richiede un importo positivo (usa adjustment per gli storni).")

    balance_before = user.ai_credit_balance
    user.ai_credit_balance += amount
    entry = AiCreditTransaction(
        user_id=user.id,
        type=type,
        amount=amount,
        balance_before=balance_before,
        balance_after=user.ai_credit_balance,
        ls_order_id=ls_order_id,
        site_url=site_url,
        product_key=product_key,
        payment_reference=payment_reference,
        payment_source=payment_source,
        approved_by_user_id=approved_by_user_id,
        admin_note=admin_note,
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(entry)
    db.session.commit()
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


def adjust_credits(user: User, amount: int, ls_order_id: str | None = None) -> AiCreditTransaction:
    """Storno manuale/rimborso — `amount` può essere negativo (claw-back di
    un acquisto rimborsato) o positivo (correzione di supporto). A differenza
    di consume_credits, non blocca se il saldo scenderebbe sotto zero: un
    rimborso va registrato comunque, anche se l'utente aveva già consumato
    parte dei crediti nel frattempo (il saldo può quindi risultare negativo —
    accettato, è un segnale per il supporto, non un caso da impedire)."""
    user.ai_credit_balance += amount
    entry = AiCreditTransaction(
        user_id=user.id,
        type="adjustment",
        amount=amount,
        balance_after=user.ai_credit_balance,
        ls_order_id=ls_order_id,
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(entry)
    db.session.commit()
    return entry

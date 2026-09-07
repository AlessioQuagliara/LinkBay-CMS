"""Accredito manuale dei pacchetti di credito AI pagati via Revolut Business
Payment Link — vendita UNA TANTUM, separata dagli abbonamenti Pro (vedi
app/billing/revolut_manual_activation.py). Non tocca MAI
subscription_status, subscription_expires_at o plan_type, e non sostituisce
né declassa l'accesso lifetime AppSumo — un top-up è solo un movimento sul
ledger crediti AI (app/entitlements/ai_credits.py).

Nessun webhook, nessuna API Revolut: un admin verifica il pagamento a mano
(email di notifica Revolut) e accredita da Flask-Admin (vedi
app/admin/views.py::RevolutAiTopupView)."""
from dataclasses import dataclass
from datetime import datetime, timezone

from flask import current_app

from app.billing.payment_references import is_reference_used_for_subscription
from app.billing.revolut_products import AI_TOPUP_CATALOG
from app.emails.revolut import send_revolut_ai_topup_activated_email
from app.entitlements.ai_credits import grant_credits
from app.entitlements.service import get_plan_limits
from app.models import AiCreditTransaction


class RevolutAiTopupError(Exception):
    """Errore applicativo (pacchetto non valido, utente non eleggibile,
    riferimento mancante/in conflitto) — la view lo cattura e lo mostra come
    flash message, mai come 500."""


@dataclass(frozen=True)
class RevolutAiTopupResult:
    outcome: str  # "credited" | "already_processed"
    already_processed: bool
    product_key: str
    credits_added: int
    balance_before: int
    balance_after: int
    email_sent: bool = False


def credit_revolut_ai_topup(*, user, product_key, payment_reference, admin, note=None):
    """Accredita il pacchetto `product_key` (whitelistato contro
    AI_TOPUP_CATALOG — mai un valore libero) sul ledger di `user`.

    Regole:
    - `product_key` deve esistere nel catalogo: quantità e prezzo vengono
      SEMPRE letti da lì, mai da un valore inviato dal client.
    - `user` deve essere eleggibile ai top-up secondo la stessa regola già in
      uso nel resto del prodotto (get_plan_limits(user).ai_credit_topups_allowed
      — oggi solo i tier AppSumo). Non introduce una seconda regola di
      eleggibilità.
    - `payment_reference` è OBBLIGATORIO (a differenza dell'attivazione
      abbonamento, dove è solo raccomandato): senza riferimento non c'è modo
      di distinguere un top-up onesto da un doppio submit, e qui il rischio è
      credito reale, non solo una data di scadenza.
    - stesso riferimento, stesso utente, transazione "grant_purchase" già
      presente -> replay idempotente: nessun secondo accredito, nessuna
      seconda email.
    - stesso riferimento già usato da un ALTRO utente, o già usato dal flusso
      di attivazione abbonamento (vedi app/billing/payment_references.py) ->
      errore, non un caso silenzioso.
    - il commit avviene PRIMA del tentativo di invio email: un errore di
      invio non annulla il credito già accreditato.
    """
    if product_key not in AI_TOPUP_CATALOG:
        raise RevolutAiTopupError(f"Invalid AI credit package '{product_key}'.")

    if not get_plan_limits(user).ai_credit_topups_allowed:
        raise RevolutAiTopupError(
            f"{user.email}'s plan is not eligible for AI credit top-ups."
        )

    payment_reference = (payment_reference or "").strip()
    if not payment_reference:
        raise RevolutAiTopupError("A payment reference is required for AI credit top-ups.")
    note = (note or "").strip() or None

    existing = AiCreditTransaction.query.filter_by(payment_reference=payment_reference).first()
    if existing:
        if existing.user_id != user.id:
            raise RevolutAiTopupError(
                "This payment reference is already linked to a different account."
            )
        # Stesso utente, stesso riferimento: replay idempotente — nessun
        # secondo accredito, nessuna seconda email.
        return RevolutAiTopupResult(
            outcome="already_processed",
            already_processed=True,
            product_key=existing.product_key or product_key,
            credits_added=existing.amount,
            balance_before=existing.balance_before if existing.balance_before is not None else existing.balance_after,
            balance_after=existing.balance_after,
            email_sent=False,
        )

    # Un riferimento già usato per attivare/estendere un abbonamento Pro non
    # può accreditare anche un top-up — sono due pagamenti diversi per
    # definizione, anche se fosse lo stesso utente.
    if is_reference_used_for_subscription(payment_reference):
        raise RevolutAiTopupError(
            "This payment reference is already linked to a Pro subscription activation."
        )

    entry_data = AI_TOPUP_CATALOG[product_key]
    credits = entry_data["credits"]
    balance_before = user.ai_credit_balance

    entry = grant_credits(
        user,
        credits,
        type="grant_purchase",
        product_key=product_key,
        payment_reference=payment_reference,
        payment_source="revolut_manual",
        approved_by_user_id=admin.id,
        admin_note=note,
    )

    email_sent = False
    try:
        email_sent = send_revolut_ai_topup_activated_email(
            user, product_key=product_key, credits_added=credits, balance_after=entry.balance_after
        )
    except Exception:  # noqa: BLE001 — un errore di invio non deve mai annullare il credito
        current_app.logger.exception(
            "Invio email di conferma top-up AI Revolut fallito per user %s (credito già accreditato, non annullato).",
            user.id,
        )

    return RevolutAiTopupResult(
        outcome="credited",
        already_processed=False,
        product_key=product_key,
        credits_added=credits,
        balance_before=balance_before,
        balance_after=entry.balance_after,
        email_sent=email_sent,
    )

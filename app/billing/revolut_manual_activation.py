"""Attivazione manuale degli abbonamenti Pro pagati via Revolut Business
Payment Link — nessun webhook, nessuna API Revolut: un admin verifica il
pagamento a mano (email di notifica Revolut) e chiama questo service da
Flask-Admin (vedi app/admin/views.py::RevolutActivationView).

Un solo punto di ingresso, `activate_revolut_subscription`, così la business
logic non vive nella view di Flask-Admin (che resta un thin controller:
valida il form, chiama questo service, mostra il risultato).
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from flask import current_app

from app.emails.revolut import send_revolut_subscription_activated_email
from app.extensions import db
from app.models import User

# Durata di ciascun piano in giorni — unica fonte di verità per il calcolo
# della scadenza. Le tre chiavi sono anche gli unici valori di `plan`
# accettati da activate_revolut_subscription (validazione server-side, non
# fidarsi mai di un valore arbitrario dal form).
REVOLUT_PLAN_DAYS = {
    "revolut_1m": 30,
    "revolut_3m": 90,
    "revolut_12m": 365,
}


class RevolutActivationError(Exception):
    """Errore applicativo (piano non valido, utente lifetime AppSumo, ecc.) —
    la view lo cattura e lo mostra come flash message, mai come 500."""


@dataclass(frozen=True)
class RevolutActivationResult:
    outcome: str  # "activated" | "already_processed"
    already_processed: bool
    plan: str
    previous_expiry: datetime | None
    new_expiry: datetime
    user_id: int
    email_sent: bool = False


def _aware(dt):
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def activate_revolut_subscription(*, user, plan, admin, payment_reference=None, note=None):
    """Attiva o estende il piano Pro di `user` via Revolut manuale.

    Regole (vedi anche app/admin/views.py per il form che raccoglie questi
    input):
    - `plan` deve essere una delle tre chiavi di REVOLUT_PLAN_DAYS —
      validato qui, non fidarsi del form.
    - un utente AppSumo lifetime non può essere toccato da qui: non esiste
      oggi una policy di migrazione AppSumo->Revolut documentata, quindi
      l'operazione viene rifiutata invece di sovrascrivere in silenzio un
      account lifetime.
    - se `payment_reference` è valorizzato ed è già quello registrato su
      questo stesso utente (riattivazione con lo stesso pagamento, es. doppio
      submit del form), l'operazione è un no-op idempotente: nessuna nuova
      estensione, nessuna nuova email. Se lo stesso riferimento è già
      registrato su un ALTRO utente, è un errore di input dell'admin (colonna
      unique lato DB), non un caso da silenziare.
    - se `payment_reference` non è fornito, la protezione da doppio submit è
      solo lato form (bottone disabilitato al submit — vedi
      app/templates/admin/revolut_activate.html); qui si procede comunque,
      come da requisito ("controlla almeno via commit + bottone disabilitato").
    - la scadenza si estende dalla scadenza attuale se è futura, altrimenti
      riparte da now() — mai da un valore arbitrario del client.
    - il commit avviene PRIMA del tentativo di invio email: un errore di
      invio non annulla l'attivazione già registrata.
    """
    if plan not in REVOLUT_PLAN_DAYS:
        raise RevolutActivationError(f"Invalid plan '{plan}'.")

    if user.subscription_status == "lifetime":
        raise RevolutActivationError(
            "This account is on an AppSumo lifetime plan — Revolut activation is not applicable."
        )

    payment_reference = (payment_reference or "").strip() or None
    note = (note or "").strip() or None

    if payment_reference and user.subscription_activation_reference == payment_reference:
        # Stesso utente, stesso riferimento già registrato: replay
        # idempotente, nessuna estensione né email ripetuta.
        return RevolutActivationResult(
            outcome="already_processed",
            already_processed=True,
            plan=user.plan_type or plan,
            previous_expiry=None,
            new_expiry=_aware(user.subscription_expires_at),
            user_id=user.id,
            email_sent=False,
        )

    if payment_reference:
        conflict = User.query.filter(
            User.subscription_activation_reference == payment_reference,
            User.id != user.id,
        ).first()
        if conflict:
            raise RevolutActivationError(
                "This payment reference is already linked to a different account."
            )

    now = datetime.now(timezone.utc)
    previous_expiry = _aware(user.subscription_expires_at)
    base = previous_expiry if (previous_expiry and previous_expiry > now) else now
    new_expiry = base + timedelta(days=REVOLUT_PLAN_DAYS[plan])

    user.subscription_status = "active"
    user.subscription_expires_at = new_expiry
    user.subscription_source = "revolut_manual"
    user.plan_type = plan
    user.subscription_activated_at = now
    user.subscription_activated_by_id = admin.id
    user.subscription_activation_reference = payment_reference
    # Un'estensione manuale chiude qualunque periodo di grazia legacy
    # residuo (Lemon Squeezy past_due) — l'utente è di nuovo "active" a
    # tutti gli effetti.
    user.grace_period_ends_at = None

    db.session.add(user)
    db.session.commit()

    email_sent = False
    try:
        email_sent = send_revolut_subscription_activated_email(user, plan=plan, expires_at=new_expiry)
    except Exception:  # noqa: BLE001 — un errore di invio non deve mai annullare l'attivazione
        current_app.logger.exception(
            "Invio email di conferma attivazione Revolut fallito per user %s (già attivato, non annullato).",
            user.id,
        )

    return RevolutActivationResult(
        outcome="activated",
        already_processed=False,
        plan=plan,
        previous_expiry=previous_expiry,
        new_expiry=new_expiry,
        user_id=user.id,
        email_sent=email_sent,
    )

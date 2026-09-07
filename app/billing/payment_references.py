"""Unicità del riferimento pagamento Revolut CONDIVISA fra i due flussi
manuali che lo usano: attivazione/estensione di un piano Pro
(`users.subscription_activation_reference`, vedi
app/billing/revolut_manual_activation.py) e accredito di un pacchetto
crediti AI (`ai_credit_transactions.payment_reference`, vedi
app/billing/revolut_ai_topup.py).

Sono due tabelle diverse: nessun vincolo UNIQUE di database può coprirle
entrambe insieme. Un riferimento pagamento Revolut identifica un solo
pagamento reale — non deve mai poter sbloccare sia un abbonamento sia un
top-up — quindi ogni servizio, oltre a controllare la propria tabella (già
univoca lì), chiama qui per controllare anche quella dell'ALTRO flusso prima
di accettare il riferimento."""
from app.models import AiCreditTransaction, User


def is_reference_used_for_subscription(reference: str | None) -> bool:
    if not reference:
        return False
    return User.query.filter_by(subscription_activation_reference=reference).first() is not None


def is_reference_used_for_ai_topup(reference: str | None) -> bool:
    if not reference:
        return False
    return AiCreditTransaction.query.filter_by(payment_reference=reference).first() is not None

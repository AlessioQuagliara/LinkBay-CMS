"""Email di conferma per l'attivazione manuale di un piano Pro via Revolut
(vedi app/billing/revolut_manual_activation.py). Stesso spirito di
app/auth/password_reset.py: un solo punto di ingresso, chiamato SOLO dopo che
la transazione di attivazione è già stata committata — un fallimento di invio
qui non deve mai risalire e annullare l'attivazione già registrata (il
chiamante si occupa di catturare le eccezioni)."""
from flask import render_template, url_for

from app.emails import send_email

PLAN_MONTHS = {
    "revolut_1m": 1,
    "revolut_3m": 3,
    "revolut_12m": 12,
}


def send_revolut_subscription_activated_email(user, *, plan, expires_at):
    """Invia l'email "il tuo piano Pro è attivo" dopo un'attivazione/estensione
    Revolut andata a buon fine. Ritorna True/False come app.emails.send_email
    (non solleva mai — è già dentro un try/except lato chiamante, ma resta
    onesto anche se chiamata direttamente altrove in futuro).

    Contenuto volutamente minimale: niente importi, niente riferimento
    pagamento, niente note amministrative, niente dettagli Revolut — solo
    cosa è cambiato per il cliente (vedi Fase 5/6 del piano di migrazione)."""
    months = PLAN_MONTHS.get(plan, 1)
    try:
        dashboard_link = url_for("dashboard.overview", _external=True)
    except Exception:  # noqa: BLE001 — non deve mai bloccare l'invio dell'email
        dashboard_link = None

    expires_label = expires_at.strftime("%d %B %Y")

    # Nessun canale supporto dedicato è configurato in questo progetto (niente
    # SUPPORT_EMAIL, nessun link "contattaci" in footer) — l'email non ne
    # inventa uno (vedi Fase 5/6 del piano di migrazione: "se già configurato").
    subject = "Your LinkBayCMS Pro plan is active"
    html = render_template(
        "emails/revolut_subscription_activated.html",
        name=user.name,
        months=months,
        expires_label=expires_label,
        dashboard_link=dashboard_link,
    )
    text_lines = [
        f"Hi {user.name},",
        "",
        f"Your LinkBayCMS Pro plan is now active ({months} month" + ("s" if months != 1 else "") + ").",
        f"Your access is valid until {expires_label}.",
    ]
    if dashboard_link:
        text_lines += ["", f"Go to your dashboard: {dashboard_link}"]
    return send_email(user.email, subject, html, text="\n".join(text_lines))

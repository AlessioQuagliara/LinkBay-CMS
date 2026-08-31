"""Export PDF delle declining pages — render Jinja (stesso modello a
tabella/inline-CSS già usato per le email transazionali, vedi
app/templates/emails/weekly_digest.html) convertito in PDF da WeasyPrint.

Generato in sincrono dentro la request (non in coda): un report di poche
decine di righe è abbastanza leggero da non giustificare la complessità di
un job asincrono — a differenza degli scan GSC/run AI, non c'è una chiamata
esterna costosa qui, solo una query DB + un render."""
from datetime import datetime, timezone

from flask import render_template

from app.models import PageAlert


def _rows_for(user_id: int, site_url: str):
    return (
        PageAlert.query.filter_by(user_id=user_id, site_url=site_url)
        .order_by(PageAlert.priority_score.desc())
        .all()
    )


def build_declining_pages_pdf(user, site_url: str, white_label: bool) -> bytes:
    import weasyprint

    html = render_template(
        "exports/declining_report.html",
        user=user,
        site_url=site_url,
        pages=_rows_for(user.id, site_url),
        white_label=white_label,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )
    return weasyprint.HTML(string=html).write_pdf()

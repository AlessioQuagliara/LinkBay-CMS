"""Export CSV delle declining pages — stdlib csv, streaming (nessun file
temporaneo, nessun limite di dimensione tenuto in memoria)."""
import csv
import io
from collections.abc import Iterator

from app.models import PageAlert

CSV_HEADER = [
    "url", "status", "best_month_clicks", "click_loss_abs", "click_loss_pct",
    "position_before", "position_after", "priority_score", "reason_text",
]


def _rows_for(user_id: int, site_url: str):
    return (
        PageAlert.query.filter_by(user_id=user_id, site_url=site_url)
        .order_by(PageAlert.priority_score.desc())
        .all()
    )


def build_declining_pages_csv(user_id: int, site_url: str) -> Iterator[str]:
    """Genera il CSV riga per riga (generator) — usato con
    flask.stream_with_context per non tenere l'intero export in RAM."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(CSV_HEADER)
    yield buffer.getvalue()
    buffer.seek(0)
    buffer.truncate(0)

    for alert in _rows_for(user_id, site_url):
        writer.writerow([
            alert.url,
            alert.status,
            alert.best_month_clicks,
            alert.click_loss_abs,
            alert.click_loss_pct,
            alert.position_before,
            alert.position_after,
            alert.priority_score,
            (alert.reason_text or "").replace("\n", " "),
        ])
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)

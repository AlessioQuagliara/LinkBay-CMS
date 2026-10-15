from datetime import timezone


def aware(dt):
    """SQLite (test) restituisce datetime naive: li normalizza a UTC per poterli
    confrontare con datetime.now(timezone.utc). No-op su Postgres."""
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

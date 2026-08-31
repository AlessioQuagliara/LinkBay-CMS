"""Gestione dei siti monitorati (multi-sito) per utente.

Separato da app/gsc/repository.py, che resta dedicato alla sola persistenza
delle credenziali OAuth: qui vive la relazione 1:N utente→siti scelti per il
monitoraggio. Il controllo dei limiti di piano (quanti siti un utente può
aggiungere) NON vive qui — è responsabilità del chiamante (route), che deve
interrogare app/entitlements prima di chiamare add_monitored_site.
"""
from datetime import datetime, timezone

from app.extensions import db
from app.models import MonitoredSite


def list_monitored_sites(user_id: int, active_only: bool = True) -> list[MonitoredSite]:
    query = MonitoredSite.query.filter_by(user_id=user_id)
    if active_only:
        query = query.filter_by(is_active=True)
    return query.order_by(MonitoredSite.added_at.asc()).all()


def get_monitored_site_row(user_id: int, site_url: str) -> MonitoredSite | None:
    return MonitoredSite.query.filter_by(user_id=user_id, site_url=site_url).first()


def count_active_sites(user_id: int) -> int:
    return MonitoredSite.query.filter_by(user_id=user_id, is_active=True).count()


def add_monitored_site(user_id: int, site_url: str) -> MonitoredSite:
    """Aggiunge (o riattiva) un sito al monitoraggio. Idempotente: se il sito
    era già stato aggiunto e poi disattivato, lo riattiva invece di creare una
    riga duplicata (violerebbe l'unique su user_id+site_url)."""
    row = get_monitored_site_row(user_id, site_url)
    if row is None:
        row = MonitoredSite(user_id=user_id, site_url=site_url)
        db.session.add(row)
    elif not row.is_active:
        row.is_active = True
        row.deactivated_at = None
        row.added_at = datetime.now(timezone.utc)
    db.session.commit()
    return row


def deactivate_monitored_site(user_id: int, site_url: str) -> bool:
    row = get_monitored_site_row(user_id, site_url)
    if row is None or not row.is_active:
        return False
    row.is_active = False
    row.deactivated_at = datetime.now(timezone.utc)
    db.session.commit()
    return True


def touch_last_synced(user_id: int, site_url: str) -> None:
    """Aggiorna il timestamp di ultimo sync riuscito (usato in Fase 2 per
    decidere quando un refresh è dovuto)."""
    row = get_monitored_site_row(user_id, site_url)
    if row is None:
        return
    row.last_synced_at = datetime.now(timezone.utc)
    db.session.commit()

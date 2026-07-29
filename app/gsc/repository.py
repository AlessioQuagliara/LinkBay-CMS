"""Salvataggio/lettura delle credenziali OAuth di Search Console per utente.

Fa da ponte tra google.oauth2.credentials.Credentials (oggetto della libreria
Google) e GscConnection (riga DB, con i token cifrati).
"""
from flask import current_app

from app.extensions import db
from app.gsc.crypto import decrypt, encrypt
from app.models import GscConnection


def credentials_to_dict(credentials) -> dict:
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "scopes": credentials.scopes,
        "expiry": credentials.expiry,
    }


def save_gsc_credentials(user_id: int, creds: dict) -> GscConnection:
    connection = GscConnection.query.filter_by(user_id=user_id).first()
    if connection is None:
        connection = GscConnection(user_id=user_id)
        db.session.add(connection)

    connection.access_token = encrypt(creds["token"])
    # Google manda il refresh_token solo al primo consenso: se una chiamata
    # successiva non lo restituisce, non sovrascrivere quello già salvato.
    if creds.get("refresh_token"):
        connection.refresh_token = encrypt(creds["refresh_token"])
    connection.token_uri = creds["token_uri"]
    scopes = creds.get("scopes") or []
    connection.scopes = ",".join(scopes) if isinstance(scopes, (list, tuple)) else scopes
    connection.expiry = creds.get("expiry")

    db.session.commit()
    return connection


def load_gsc_credentials(user_id: int) -> dict | None:
    connection = GscConnection.query.filter_by(user_id=user_id).first()
    if connection is None:
        return None

    return {
        "token": decrypt(connection.access_token),
        "refresh_token": decrypt(connection.refresh_token) if connection.refresh_token else None,
        "token_uri": connection.token_uri,
        "client_id": current_app.config["GOOGLE_CLIENT_ID"],
        "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
        "scopes": connection.scopes.split(",") if connection.scopes else [],
        "expiry": connection.expiry,
    }


def delete_gsc_credentials(user_id: int) -> bool:
    connection = GscConnection.query.filter_by(user_id=user_id).first()
    if connection is None:
        return False
    db.session.delete(connection)
    db.session.commit()
    return True

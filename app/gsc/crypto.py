"""Cifratura simmetrica (Fernet) per i token OAuth salvati in DB.

Chiave letta da TOKEN_ENCRYPTION_KEY (config/.env). Non è mai hardcoded.
"""
from cryptography.fernet import Fernet, InvalidToken
from flask import current_app


class MissingEncryptionKey(RuntimeError):
    pass


def _fernet() -> Fernet:
    key = current_app.config.get("TOKEN_ENCRYPTION_KEY")
    if not key:
        raise MissingEncryptionKey(
            "TOKEN_ENCRYPTION_KEY non impostata. Generane una con: "
            'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" '
            "e mettila in .env."
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt(value: str | None) -> str | None:
    if value is None:
        return None
    return _fernet().encrypt(value.encode()).decode()


def decrypt(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return _fernet().decrypt(value.encode()).decode()
    except InvalidToken as exc:
        raise InvalidToken(
            "Impossibile decifrare il token: TOKEN_ENCRYPTION_KEY è cambiata rispetto a quando "
            "è stato salvato, oppure il dato è corrotto."
        ) from exc

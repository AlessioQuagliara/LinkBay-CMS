"""Configurazione dell'app, letta da variabili d'ambiente (.env)."""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://linkbay:linkbay@localhost:5432/linkbay_cms"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

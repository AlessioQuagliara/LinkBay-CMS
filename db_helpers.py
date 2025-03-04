from flask import g
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Carica le variabili d'ambiente dal file .env
load_dotenv()
environment = os.getenv('ENVIRONMENT')

class DatabaseHelper:
    """
    Classe per la gestione della connessione al database PostgreSQL (CMS_DEF).
    """

    def __init__(self):
        """
        Inizializza la connessione al database CMS_DEF.
        """
        self.db_engine = None
        self.db_session = None
        self.init_connection()

    def init_connection(self):
        """
        Inizializza l'engine e la sessione per il database CMS_DEF.
        """
        # Costruisce la stringa di connessione usando le variabili d'ambiente
        self.db_engine = create_engine(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
            f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )

        # Crea una sessione per gestire le query con SQLAlchemy
        self.db_session = scoped_session(sessionmaker(bind=self.db_engine))

    def get_db_session(self):
        """
        Ottiene la sessione per il database CMS_DEF. Se non esiste nel contesto Flask, la crea.

        :return: Oggetto sessione SQLAlchemy
        """
        if 'db_session' not in g:
            g.db_session = self.db_session()
        return g.db_session

    def execute_query(self, query, params=None):
        """
        Esegue una query SELECT sul database e restituisce il risultato come lista di dizionari.

        :param query: Query SQL da eseguire
        :param params: Parametri della query (default: None)
        :return: Lista di risultati come dizionari o lista vuota in caso di errore
        """
        session = self.get_db_session()
        try:
            result = session.execute(query, params if params else {}).fetchall()
            return [dict(row._mapping) for row in result]  # Converte in lista di dizionari
        except Exception as e:
            session.rollback()
            print(f"❌ Errore durante l'esecuzione della query: {e}")
            return []

    def execute_commit(self, query, params=None):
        """
        Esegue una query di tipo INSERT, UPDATE o DELETE e committa la transazione.

        :param query: Query SQL da eseguire
        :param params: Parametri della query (default: None)
        :return: ID della riga inserita o None in caso di errore
        """
        session = self.get_db_session()
        try:
            result = session.execute(query, params if params else {})
            session.commit()
            return result.inserted_primary_key if result else None  # Restituisce l'ID dell'ultima inserzione
        except Exception as e:
            session.rollback()
            print(f"❌ Errore durante l'esecuzione della query di commit: {e}")
            return None

    def close(self):
        """
        Chiude la sessione aperta nel contesto Flask.
        """
        db_session = g.pop('db_session', None)
        if db_session:
            db_session.close()
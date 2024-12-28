from flask import g
import mysql.connector

class DatabaseHelper:
    def __init__(self):
        self.conn = None
        self.auth_conn = None

    def get_db_connection(self):
        """
        Ottiene la connessione al database principale e la salva in 'g'.
        """
        if 'db' not in g:
            g.db = mysql.connector.connect(
                host='127.0.0.1',  # Modifica secondo la tua configurazione
                user='root',
                password='root',
                database='CMS_DEF',
                port=8889
            )
        return g.db

    def get_auth_db_connection(self):
        """
        Ottiene la connessione al database di autenticazione e la salva in 'g'.
        """
        if 'auth_db' not in g:
            g.auth_db = mysql.connector.connect(
                host='127.0.0.1',  # Modifica secondo la tua configurazione
                user='auth_user',
                password='auth_password',
                database='AUTH_DB',
                port=8889
            )
        return g.auth_db

    def execute_query(self, query, params=None, use_auth=False):
        """
        Esegue una query SELECT.
        """
        conn = self.get_auth_db_connection() if use_auth else self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute_commit(self, query, params=None, use_auth=False):
        """
        Esegue una query che richiede commit (INSERT, UPDATE, DELETE).
        """
        conn = self.get_auth_db_connection() if use_auth else self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        cursor.close()

    def close(self):
        """
        Chiude le connessioni al database principale e al database di autenticazione.
        """
        db = g.pop('db', None)
        if db is not None:
            db.close()

        auth_db = g.pop('auth_db', None)
        if auth_db is not None:
            auth_db.close()
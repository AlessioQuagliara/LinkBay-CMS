from flask import g
import mysql.connector

class DatabaseHelper:
    """
    Classe per gestire le connessioni al database.
    """
    def __init__(self):
        self.conn = None
        self.auth_conn = None

    def get_db_connection(self):
        """
        Ottiene la connessione al database principale (CMS_DEF) e la salva in 'g'.
        """
        if 'db' not in g:
            g.db = mysql.connector.connect(
                #host='127.0.0.1',  # Configurazione del database principale
                #user='root',
                #password='root',
                #database='CMS_DEF',
                #port=8889
                user="root",
                password="root",
                host="127.0.0.1",
                database="cms_def",
                port=3306,  # Usa la porta corretta per il database di produzione
                auth_plugin='mysql_native_password'  # Specifica il plugin se necessario
            )
        return g.db

    def get_auth_db_connection(self):
        """
        Ottiene la connessione al database CMS_INDEX e la salva in 'g'.
        """
        if 'auth_db' not in g:
            g.auth_db = mysql.connector.connect(
                #host='127.0.0.1',
                #user='root',         # Usa l'utente corretto
                #password='root',      # Usa la password corretta
                #database='CMS_INDEX', # Nome del database
                #port=8889             # Porta corretta
                user="root",
                password="root",
                host="127.0.0.1",
                database="cms_index",
                port=3306,  # Usa la porta corretta per il database di produzione
                auth_plugin='mysql_native_password'  # Specifica il plugin se necessario
            )
        return g.auth_db

    def execute_query(self, query, params=None, use_auth=False):
        """
        Esegue una query SELECT su uno dei database.
        """
        conn = self.get_auth_db_connection() if use_auth else self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params if params else ())
            result = cursor.fetchall()
        finally:
            cursor.close()
        return result

    def execute_commit(self, query, params=None, use_auth=False):
        """
        Esegue una query che richiede un commit (INSERT, UPDATE, DELETE).
        """
        conn = self.get_auth_db_connection() if use_auth else self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params if params else ())
            conn.commit()
            last_id = cursor.lastrowid
        finally:
            cursor.close()
        return last_id

    def close(self):
        """
        Chiude tutte le connessioni aperte.
        """
        db = g.pop('db', None)
        if db:
            db.close()

        auth_db = g.pop('auth_db', None)
        if auth_db:
            auth_db.close()
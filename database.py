import mysql.connector

class Database:
    def __init__(self, config):
        self.config = config
        self.conn = None

    def connect(self):
        if not self.conn:
            self.conn = mysql.connector.connect(
                host=self.config['DB_HOST'],
                user=self.config['DB_USER'],
                password=self.config['DB_PASSWORD'],
                database=self.config['DB_NAME'],
                port=self.config['DB_PORT']
            )
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def query(self, query, params=None):
        """
        Esegue una query SELECT e restituisce il risultato.
        """
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
        finally:
            cursor.close()
        return result

    def execute(self, query, params=None):
        """
        Esegue una query (INSERT, UPDATE, DELETE) e restituisce l'ID dell'ultimo record inserito.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            self.conn.commit()
            last_id = cursor.lastrowid
        finally:
            cursor.close()
        return last_id
    
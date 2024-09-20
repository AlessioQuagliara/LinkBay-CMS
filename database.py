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
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute(self, query, params=None):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id
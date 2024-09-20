from flask import g
import mysql.connector

class DatabaseHelper:
    def __init__(self):
        self.conn = self.get_db_connection()

    def get_db_connection(self):
        if 'db' not in g:
            g.db = mysql.connector.connect(
                host='127.0.0.1',
                user='root',
                password='root',
                database='CMS_DEF',
                port=8889
            )
        return g.db

    def execute_query(self, query, params=None):
        cursor = self.conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

    def execute_commit(self, query, params=None):
        cursor = self.conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.conn.commit()

    def close(self):
        db = g.pop('db', None)
        if db is not None:
            db.close()
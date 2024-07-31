import mysql.connector

config = {
    'user' : 'root',
    'password' : 'root',
    'host' : 'localhost',
    'unix_socket' : '/Applications/MAMP/tmp/mysql/mysql.sock',
    'database' : 'CMS_DEF',
    'raise_on_warnings' : True
}

def get_db_connection():
    cnx = mysql.connector.connect(**config)
    return cnx
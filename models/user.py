from werkzeug.security import generate_password_hash, check_password_hash

# CLASSE PER GESTIONE UTENTI ---------------------------------------------------------------------------------------------------

class User:
    def __init__(self, db_conn):
        self.conn = db_conn

    def get_all_users(self):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id, email, nome, cognome, telefono, profilo_foto, is_2fa_enabled FROM user")
                users = cursor.fetchall()
            return users
        except Exception as e:
           logging.info(f"Error fetching all users: {e}")
            return []

    def get_user_by_id(self, user_id):
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        return user

    def get_user_by_email(self, email):
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
            user = cursor.fetchone()
        return user

    def create_user(self, email, password, nome, cognome, telefono, profilo_foto):
        hashed_password = generate_password_hash(password)
        with self.conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO user (email, password, nome, cognome, telefono, profilo_foto) VALUES (%s, %s, %s, %s, %s, %s)",
                (email, hashed_password, nome, cognome, telefono, profilo_foto)
            )
            self.conn.commit()

    def update_user(self, user_id, nome, cognome, telefono, profilo_foto):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE user SET nome = %s, cognome = %s, telefono = %s, profilo_foto = %s WHERE id = %s",
                (nome, cognome, telefono, profilo_foto, user_id)
            )
            self.conn.commit()

    def delete_user(self, user_id):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
            self.conn.commit()
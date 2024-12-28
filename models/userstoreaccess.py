# Classe per UserStoreAccess --------------------------------------------------------------------------------------------

class UserStoreAccess:
    def __init__(self, db_conn):
        self.conn = db_conn

    def grant_access(self, user_id, shop_id, access_level='viewer'):
        """
        Concede accesso a un utente per uno specifico store con un livello di accesso.
        """
        query = """
            INSERT INTO user_store_access (user_id, shop_id, access_level)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE access_level = %s
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (user_id, shop_id, access_level, access_level))
            self.conn.commit()

    def revoke_access(self, user_id, shop_id):
        """
        Revoca l'accesso di un utente per uno specifico store.
        """
        query = "DELETE FROM user_store_access WHERE user_id = %s AND shop_id = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(query, (user_id, shop_id))
            self.conn.commit()

    def has_access(self, user_id, shop_id):
        """
        Controlla se un utente ha accesso a uno specifico store.
        """
        query = "SELECT * FROM user_store_access WHERE user_id = %s AND shop_id = %s"
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (user_id, shop_id))
            access = cursor.fetchone()
        return access is not None

    def get_access_level(self, user_id, shop_id):
        """
        Recupera il livello di accesso di un utente per uno specifico store.
        """
        query = "SELECT access_level FROM user_store_access WHERE user_id = %s AND shop_id = %s"
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (user_id, shop_id))
            access = cursor.fetchone()
        return access['access_level'] if access else None

    def get_user_stores(self, user_id):
        """
        Recupera tutti gli store a cui un utente ha accesso.
        """
        query = """
            SELECT ShopList.id, ShopList.shop_name, user_store_access.access_level
            FROM user_store_access
            JOIN ShopList ON user_store_access.shop_id = ShopList.id
            WHERE user_store_access.user_id = %s
        """
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (user_id,))
            stores = cursor.fetchall()
        return stores
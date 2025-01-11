# Classe per ShopList ---------------------------------------------------------------------------------------------------
class ShopList:
    def __init__(self, db_conn):
        self.conn = db_conn

    def get_shop_by_name(self, shop_name):
        query = """
            SELECT id, shop_name, themeOptions, domain, user_id, partner_id
            FROM ShopList
            WHERE shop_name = %s
        """
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (shop_name,))
            shop = cursor.fetchone()
        return shop
    
    def get_shop_by_name_or_domain(self, value):
        query = """
            SELECT id, shop_name, themeOptions, domain, user_id, partner_id
            FROM ShopList
            WHERE shop_name = %s OR domain = %s
        """
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (value, value))
            shop = cursor.fetchone()
        return shop
    
    def update_shop_domain(self, shop_name, domain):
        """
        Aggiorna il dominio per un negozio specifico.
        """
        query = """
            UPDATE ShopList
            SET domain = %s
            WHERE shop_name = %s
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (domain, shop_name))
                self.conn.commit()
                return cursor.rowcount > 0  # Restituisce True se almeno una riga è stata aggiornata
        except Exception as e:
            print(f"Error updating shop domain: {e}")
            self.conn.rollback()
            return False
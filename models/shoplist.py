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
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute(query, (shop_name,))
            shop = cursor.fetchone()
        finally:
            cursor.close()
        return shop
    
    def get_shop_by_name_or_domain(self, value):
        query = """
            SELECT id, shop_name, themeOptions, domain, user_id, partner_id
            FROM ShopList
            WHERE shop_name = %s OR domain = %s
        """
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute(query, (value, value))
            shop = cursor.fetchone()
        finally:
            cursor.close()
        return shop
    
    def update_shop_domain(self, shop_name, domain):
        query = """
            UPDATE ShopList
            SET domain = %s
            WHERE shop_name = %s
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, (domain, shop_name))
            self.conn.commit()
            return cursor.rowcount > 0  # Restituisce True se almeno una riga è stata aggiornata
        except Exception as e:
           logging.info(f"Error updating shop domain: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()
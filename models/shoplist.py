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
    
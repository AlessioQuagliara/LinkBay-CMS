# CATEGORIE ---------------------------------------------------------------------------------------------------

class Domain:
    def __init__(self, db_conn):
        self.conn = db_conn

    def get_all_domains(self, shop_name):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = "SELECT * FROM domains WHERE shop_name = %s"
                cursor.execute(query, (shop_name,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching categories: {e}")
                return []

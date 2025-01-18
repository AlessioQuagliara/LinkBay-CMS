# METODI DI SPEDIZIONE ---------------------------------------------------------------------------------------------------
import logging
logging.basicConfig(level=logging.INFO)

class ShippingMethods:
    def __init__(self, db_conn):
        self.conn = db_conn

    def create_shipping_method(self, data):
        try:
            with self.conn.cursor() as cursor:
                query = """
                    INSERT INTO shipping_methods (
                        shop_name, name, description, country, region, cost, 
                        estimated_delivery_time, is_active, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """
                values = (
                    data["shop_name"],
                    data["name"],
                    data.get("description"),
                    data.get("country"),
                    data.get("region"),
                    data["cost"],
                    data.get("estimated_delivery_time"),
                    data.get("is_active", True)
                )
                cursor.execute(query, values)
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logging.info(f"Error creating shipping method: {e}")
            self.conn.rollback()
            return None

    def get_all_shipping_methods(self, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT * FROM shipping_methods
                    WHERE shop_name = %s AND is_active = TRUE
                    ORDER BY created_at DESC
                """
                cursor.execute(query, (shop_name,))
                return cursor.fetchall()
        except Exception as e:
            logging.info(f"Error fetching shipping methods: {e}")
            return []

    def update_shipping_method(self, method_id, data):
        try:
            with self.conn.cursor() as cursor:
                query = """
                    UPDATE shipping_methods
                    SET name = %s, description = %s, country = %s, region = %s,
                        cost = %s, estimated_delivery_time = %s, is_active = %s, updated_at = NOW()
                    WHERE id = %s AND shop_name = %s
                """
                values = (
                    data["name"],
                    data.get("description"),
                    data.get("country"),
                    data.get("region"),
                    data["cost"],
                    data.get("estimated_delivery_time"),
                    data.get("is_active", True),
                    method_id,
                    data["shop_name"]
                )
                cursor.execute(query, values)
                self.conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.info(f"Error updating shipping method: {e}")
            self.conn.rollback()
            return False

    def delete_shipping_method(self, shipping_id):
        try:
            with self.conn.cursor() as cursor:
                query = "DELETE FROM shipping_methods WHERE id = %s"
                cursor.execute(query, (shipping_id,))
                self.conn.commit()
                return cursor.rowcount > 0  # Ritorna True se è stata eliminata almeno una riga
        except Exception as e:
            logging.info(f"Error deleting shipping method: {e}")
            self.conn.rollback()
            return False

    def get_shipping_method_by_id(self, shipping_id, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT id, shop_name, name, description, country, region, cost, 
                        estimated_delivery_time, is_active, created_at, updated_at
                    FROM shipping_methods
                    WHERE id = %s AND shop_name = %s
                """
                cursor.execute(query, (shipping_id, shop_name))
                return cursor.fetchone()  # Ritorna un dizionario con i dettagli del metodo di spedizione
        except Exception as e:
            logging.info(f"Error retrieving shipping method: {e}")
            return None

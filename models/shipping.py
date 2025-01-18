# SPEDIZIONI ---------------------------------------------------------------------------------------------------

class Shipping:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per ottenere i dettagli di spedizione associati a un ordine
    def get_shipping_by_order_id(self, order_id):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT id, shipping_method, tracking_number, carrier_name, 
                           estimated_delivery_date, delivery_status, created_at, updated_at
                    FROM shipping
                    WHERE order_id = %s
                """
                cursor.execute(query, (order_id,))
                return cursor.fetchone()
        except Exception as e:
           logging.info(f"Error fetching shipping details: {e}")
            return None

    def get_all_shippings(self, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT 
                        id, shipping_method, tracking_number, carrier_name, 
                        estimated_delivery_date, delivery_status, created_at, updated_at
                    FROM shipping
                    WHERE shop_name = %s
                    ORDER BY created_at DESC
                """
                cursor.execute(query, (shop_name,))
                return cursor.fetchall()
        except Exception as e:
           logging.info(f"Error fetching shipping: {e}")
            return []

    # Metodo per aggiungere o aggiornare i dettagli di spedizione
    def upsert_shipping(self, data):
        try:
            with self.conn.cursor() as cursor:
                query = """
                    INSERT INTO shipping (
                        shop_name, order_id, shipping_method, tracking_number, 
                        carrier_name, estimated_delivery_date, delivery_status, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    ON DUPLICATE KEY UPDATE
                        shipping_method = VALUES(shipping_method),
                        tracking_number = VALUES(tracking_number),
                        carrier_name = VALUES(carrier_name),
                        estimated_delivery_date = VALUES(estimated_delivery_date),
                        delivery_status = VALUES(delivery_status),
                        updated_at = NOW()
                """
                values = (
                    data.get("shop_name"),
                    data.get("order_id"),
                    data.get("shipping_method"),
                    data.get("tracking_number"),
                    data.get("carrier_name"),
                    data.get("estimated_delivery_date"),
                    data.get("delivery_status")
                )
                cursor.execute(query, values)
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
           logging.info(f"Error upserting shipping: {e}")
            self.conn.rollback()
            return None
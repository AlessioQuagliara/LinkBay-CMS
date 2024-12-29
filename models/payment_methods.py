# METODI DI PAGAMENTO ---------------------------------------------------------------------------------------------------

class PaymentMethods:
    def __init__(self, db_conn):
        self.conn = db_conn

    def create_payment_method(self, data):
        """
        Crea un nuovo metodo di pagamento per un negozio.
        """
        try:
            with self.conn.cursor() as cursor:
                query = """
                    INSERT INTO payment_methods (
                        shop_name, method_name, api_key, api_secret, extra_info, 
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                """
                values = (
                    data["shop_name"],
                    data["method_name"],
                    data.get("api_key"),
                    data.get("api_secret"),
                    data.get("extra_info")
                )
                cursor.execute(query, values)
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating payment method: {e}")
            self.conn.rollback()
            return None

    def get_all_payment_methods(self, shop_name):
        """
        Ottiene tutti i metodi di pagamento per un negozio.
        """
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT id, shop_name, method_name, api_key, api_secret, extra_info, 
                        created_at, updated_at
                    FROM payment_methods
                    WHERE shop_name = %s
                    ORDER BY created_at DESC
                """
                cursor.execute(query, (shop_name,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching payment methods: {e}")
            return []

    def update_payment_method(self, method_id, data):
        """
        Aggiorna i dettagli di un metodo di pagamento.
        """
        try:
            with self.conn.cursor() as cursor:
                query = """
                    UPDATE payment_methods
                    SET method_name = %s, api_key = %s, api_secret = %s, 
                        extra_info = %s, updated_at = NOW()
                    WHERE id = %s AND shop_name = %s
                """
                values = (
                    data["method_name"],
                    data.get("api_key"),
                    data.get("api_secret"),
                    data.get("extra_info"),
                    method_id,
                    data["shop_name"]
                )
                cursor.execute(query, values)
                self.conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating payment method: {e}")
            self.conn.rollback()
            return False

    def delete_payment_method(self, method_id, shop_name):
        """
        Elimina un metodo di pagamento.
        """
        try:
            with self.conn.cursor() as cursor:
                query = "DELETE FROM payment_methods WHERE id = %s AND shop_name = %s"
                cursor.execute(query, (method_id, shop_name))
                self.conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting payment method: {e}")
            self.conn.rollback()
            return False

    def get_payment_method_by_id(self, method_id, shop_name):
        """
        Ottiene i dettagli di un metodo di pagamento specifico.
        """
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT id, shop_name, method_name, api_key, api_secret, extra_info, 
                        created_at, updated_at
                    FROM payment_methods
                    WHERE id = %s AND shop_name = %s
                """
                cursor.execute(query, (method_id, shop_name))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error retrieving payment method: {e}")
            return None
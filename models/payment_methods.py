# METODI DI PAGAMENTO ---------------------------------------------------------------------------------------------------
import logging
logging.basicConfig(level=logging.INFO)

class PaymentMethods:
    def __init__(self, conn):
        self.conn = conn

    def create_payment_method(self, data):
        query = """
            INSERT INTO payment_methods (shop_name, method_name, api_key, api_secret, extra_info)
            VALUES (%s, %s, %s, %s, %s)
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (
                data['shop_name'], 
                data['method_name'], 
                data['api_key'], 
                data['api_secret'], 
                data.get('extra_info')  # Usa None se extra_info non è presente
            ))
            self.conn.commit()
            return cursor.lastrowid

    def update_payment_method(self, method_id, data, shop_name):
        query = """
            UPDATE payment_methods
            SET api_key = %s,
                api_secret = %s,
                extra_info = %s,
                updated_at = NOW()
            WHERE id = %s AND shop_name = %s
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (
                    data.get('api_key'),
                    data.get('api_secret'),
                    data.get('extra_info'),
                    method_id,
                    shop_name
                ))
                self.conn.commit()
                return cursor.rowcount > 0  # Restituisce True se una riga è stata aggiornata
        except Exception as e:
            logging.info(f"Error updating payment method: {e}")
            self.conn.rollback()
            return False

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
            logging.info(f"Error fetching payment methods: {e}")
            return []

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
            logging.info(f"Error deleting payment method: {e}")
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
            logging.info(f"Error retrieving payment method: {e}")
            return None
        
    def get_payment_method(self, shop_name, method_name):
        """
        Ottiene i dettagli di un metodo di pagamento specifico per shop_name e method_name.
        """
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT id, shop_name, method_name, api_key, api_secret, extra_info, 
                        created_at, updated_at
                    FROM payment_methods
                    WHERE shop_name = %s AND method_name = %s
                """
                cursor.execute(query, (shop_name, method_name))
                return cursor.fetchone()  # Restituisce un singolo risultato
        except Exception as e:
            logging.info(f"Error retrieving payment method for {method_name} in {shop_name}: {e}")
            return None
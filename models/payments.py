# PAGAMENTI ---------------------------------------------------------------------------------------------------

class Payments:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per ottenere i pagamenti associati a un ordine
    def get_payments_by_order_id(self, order_id):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT id, payment_method, payment_status, paid_amount, transaction_id, created_at
                    FROM payments
                    WHERE order_id = %s
                    ORDER BY created_at DESC
                """
                cursor.execute(query, (order_id,))
                return cursor.fetchall()
        except Exception as e:
           logging.info(f"Error fetching payments: {e}")
            return []

    # Metodo per aggiungere un pagamento
    def add_payment(self, data):
        try:
            with self.conn.cursor() as cursor:
                query = """
                    INSERT INTO payments (
                        order_id, payment_method, payment_status, paid_amount, transaction_id, created_at
                    ) VALUES (%s, %s, %s, %s, %s, NOW())
                """
                values = (
                    data.get("order_id"),
                    data.get("payment_method"),
                    data.get("payment_status"),
                    data.get("paid_amount"),
                    data.get("transaction_id")
                )
                cursor.execute(query, values)
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
           logging.info(f"Error adding payment: {e}")
            self.conn.rollback()
            return None
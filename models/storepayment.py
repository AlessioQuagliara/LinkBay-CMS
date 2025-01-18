# STORE PAYMENTS ONLINE ----INERN--- --------------------------------------------------------------------------------------------
import logging
logging.basicConfig(level=logging.INFO)

class StorePayment:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per creare un nuovo record di pagamento
    def create_payment(self, shop_name, payment_type, amount, stripe_payment_id, status='pending', 
                       integration_name=None, subscription_id=None, currency='EUR'):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO store_payments (shop_name, payment_type, amount, stripe_payment_id, 
                                                status, integration_name, subscription_id, currency, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, (shop_name, payment_type, amount, stripe_payment_id, status, integration_name, subscription_id, currency))
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logging.info(f"Error creating payment record: {e}")
            self.conn.rollback()
            return None

    # Metodo per aggiornare lo stato di un pagamento
    def update_payment_status(self, stripe_payment_id, status):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE store_payments
                    SET status = %s, updated_at = NOW()
                    WHERE stripe_payment_id = %s
                """, (status, stripe_payment_id))
                self.conn.commit()
                return True
        except Exception as e:
            logging.info(f"Error updating payment status: {e}")
            self.conn.rollback()
            return False

    # Metodo per ottenere i pagamenti per uno shop
    def get_payments_by_shop(self, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT * FROM store_payments
                    WHERE shop_name = %s
                    ORDER BY created_at DESC
                """, (shop_name,))
                return cursor.fetchall()
        except Exception as e:
            logging.info(f"Error fetching payments for shop: {e}")
            return []

    # Metodo per ottenere i dettagli di un pagamento specifico tramite ID di Stripe
    def get_payment_by_stripe_id(self, stripe_payment_id):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT * FROM store_payments
                    WHERE stripe_payment_id = %s
                """, (stripe_payment_id,))
                return cursor.fetchone()    
        except Exception as e:
            logging.info(f"Error fetching payment by Stripe ID: {e}")
            return None

    # Metodo per ottenere i pagamenti di tipo abbonamento
    def get_subscription_payments(self, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT * FROM store_payments
                    WHERE shop_name = %s AND payment_type = 'subscription'
                    ORDER BY created_at DESC
                """, (shop_name,))
                return cursor.fetchall()
        except Exception as e:
            logging.info(f"Error fetching subscription payments: {e}")
            return []
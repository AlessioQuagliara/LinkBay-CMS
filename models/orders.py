# CLASSE PER ORDINI ---------------------------------------------------------------------------------------------------
import logging
logging.basicConfig(level=logging.INFO)

class Orders:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per cancellare un ordine
    def delete_order(self, order_id):
        try:
            with self.conn.cursor() as cursor:
                query = "DELETE FROM orders WHERE id = %s"
                cursor.execute(query, (order_id,))
                self.conn.commit()
                return True
        except Exception as e:
            logging.info(f"Error deleting order: {e}")
            self.conn.rollback()
            return False

    # Metodo per creare un ordine
    def create_order(self, data):
        try:
            with self.conn.cursor() as cursor:
                print("Data received by create_order:", data)  # Log dei dati ricevuti

                # Query per inserire l'ordine
                query = """
                    INSERT INTO orders (
                        shop_name, order_number, customer_id, total_amount, status, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                """
                # Prepara i valori
                values = (
                    data.get("shop_name"),
                    data.get("order_number"),
                    data.get("customer_id", None),
                    data.get("total_amount", 0.0),
                    data.get("status", "Draft")
                )
                print("Query values:", values)  # Log dei valori preparati

                # Esegui la query
                cursor.execute(query, values)
                self.conn.commit()

                # Ritorna l'ID dell'ordine creato
                order_id = cursor.lastrowid
                print("Order ID created:", order_id)  # Log dell'ID creato
                return order_id
        except Exception as e:
            logging.info(f"Error in create_order: {e}")  # Log dell'errore
            self.conn.rollback()
            return None

    # Metodo per ottenere i dati dell'ordine dalla tabella "orders"
    def get_order_by_id(self, shop_name, order_id):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                # Query per ottenere i dettagli dell'ordine
                order_query = """
                    SELECT 
                        id AS order_id, 
                        shop_name, 
                        order_number, 
                        customer_id, 
                        total_amount, 
                        status, 
                        created_at, 
                        updated_at
                    FROM orders
                    WHERE id = %s AND shop_name = %s
                """
                cursor.execute(order_query, (order_id, shop_name))
                order = cursor.fetchone()  # Restituisce solo i dati dalla tabella "orders"

                return order  # Ritorna i dati della tabella orders
        except Exception as e:
            logging.info(f"Error fetching order: {e}")
            return None

    # Metodo per aggiornare lo stato di un ordine
    def update_order(self, shop_name, order_id, customer_id, status, total_amount):
        try:
            with self.conn.cursor() as cursor:
                # Query di aggiornamento
                query = """
                    UPDATE orders
                    SET 
                        status = %s,
                        updated_at = NOW(),
                        total_amount = %s,
                        customer_id = %s
                    WHERE id = %s AND shop_name = %s
                """
                values = (
                    status,
                    total_amount,
                    customer_id,
                    order_id,
                    shop_name
                )
                cursor.execute(query, values)
                self.conn.commit()
                return True
        except Exception as e:
            logging.info(f"Error updating order: {e}")
            self.conn.rollback()
            return False

    # Metodo per ottenere tutti gli ordini per uno shop
    def get_all_orders(self, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT o.id, o.order_number, o.total_amount, o.created_at, o.status,
                        c.first_name, c.last_name
                    FROM orders o
                    LEFT JOIN customers c ON o.customer_id = c.id
                    WHERE o.shop_name = %s
                    ORDER BY o.created_at DESC
                """
                cursor.execute(query, (shop_name,))
                return cursor.fetchall()
        except Exception as e:
            logging.info(f"Error fetching orders: {e}")
            return []

    def get_order_items(self, order_id):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT 
                        order_items.id,
                        order_items.order_id,
                        order_items.product_id,
                        order_items.quantity,
                        order_items.price,
                        order_items.subtotal,
                        products.name AS product_name,
                        products.image_url AS product_image
                    FROM order_items
                    LEFT JOIN products ON order_items.product_id = products.id
                    WHERE order_items.order_id = %s
                """
                cursor.execute(query, (order_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.info(f"Error retrieving order items: {e}")
            return []

    # Metodo per aggiungere un prodotto a un ordine
    def add_product_to_order(self, order_id, product_id, quantity=1):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                # Recupera il prezzo del prodotto
                query_get_price = "SELECT price FROM products WHERE id = %s"
                cursor.execute(query_get_price, (product_id,))
                product = cursor.fetchone()

                if not product:
                    return {'success': False, 'message': 'Product not found.'}

                price = product['price']

                # Inserisce il prodotto nella tabella order_items
                query_insert_item = """
                    INSERT INTO order_items (order_id, product_id, quantity, price, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """
                cursor.execute(query_insert_item, (order_id, product_id, quantity, price))
                self.conn.commit()

                return {'success': True, 'message': 'Product added successfully.'}
        except Exception as e:
            logging.info(f"Error adding product to order: {e}")
            self.conn.rollback()
            return {'success': False, 'message': 'An error occurred while adding the product.'}

    def remove_order_items(self, order_id, product_ids):
        try:
            with self.conn.cursor() as cursor:
                # Crea una clausola IN dinamica
                placeholders = ', '.join(['%s'] * len(product_ids))
                query = f"""
                    DELETE FROM order_items 
                    WHERE order_id = %s AND product_id IN ({placeholders})
                """
                # Passa l'ordine e i prodotti come parametri
                cursor.execute(query, [order_id] + product_ids)
                self.conn.commit()
                return cursor.rowcount > 0  # True se almeno una riga è stata eliminata
        except Exception as e:
            logging.info(f"Error removing order items: {e}")
            self.conn.rollback()
            return False

    def add_multiple_order_items(self, order_id, products):
        try:
            with self.conn.cursor() as cursor:
                query = """
                    INSERT INTO order_items (order_id, product_id, quantity, price, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """
                values = [
                    (order_id, product['id'], 1, product['price'])
                    for product in products
                ]
                cursor.executemany(query, values)
                self.conn.commit()
                return True
        except Exception as e:
            logging.info(f"Error adding multiple order items: {e}")
            self.conn.rollback()
            return False

    def update_order_items_quantities(self, order_id, items):
        try:
            with self.conn.cursor() as cursor:
                # Aggiorna le quantità per ogni articolo
                query = """
                    UPDATE order_items
                    SET quantity = %s
                    WHERE order_id = %s AND product_id = %s
                """
                for item in items:
                    cursor.execute(query, (item['quantity'], order_id, item['product_id']))
                self.conn.commit()
                return True
        except Exception as e:
            logging.info(f"Error updating order item quantities: {e}")
            self.conn.rollback()
            return False

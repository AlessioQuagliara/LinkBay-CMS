# CLIENTI ---------------------------------------------------------------------------------------------------
import logging
logging.basicConfig(level=logging.INFO)

class Customers:
    def __init__(self, db_conn):
        self.conn = db_conn

    def get_customer_by_id(self, customer_id):
        query = """
        SELECT * FROM customers
        WHERE id = %s
        """
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (customer_id,))
            return cursor.fetchone()
        
    def create_customer(self, data):
        query = """
            INSERT INTO customers (
                shop_name, first_name, last_name, email, phone, address, city, state, postal_code, country, password, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        values = (
            data['shop_name'], data['first_name'], data['last_name'], data['email'],
            data['phone'], data['address'], data['city'], data['state'], data['postal_code'],
            data['country'], data['password']
        )
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, values)
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logging.info(f"Error creating customer: {e}")
            self.conn.rollback()
            return None

    def get_all_customers(self, shop_name):
        query = """
            SELECT *
            FROM customers
            WHERE shop_name = %s
        """
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, (shop_name,))
                customers = cursor.fetchall()
                return customers
        except Exception as e:
            logging.info(f"Error fetching customers: {e}")
            return []

    def update_customer(self, customer_id, data, shop_name):
        query = """
            UPDATE customers
            SET first_name = %s,
                last_name = %s,
                email = %s,
                password = %s,
                phone = %s,
                address = %s,
                city = %s,
                state = %s,
                postal_code = %s,
                country = %s,
                updated_at = NOW()
            WHERE id = %s AND shop_name = %s
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (
                    data.get('first_name'),
                    data.get('last_name'),
                    data.get('email'),
                    data.get('password'),
                    data.get('phone'),
                    data.get('address'),
                    data.get('city'),
                    data.get('state'),
                    data.get('postal_code'),
                    data.get('country'),
                    customer_id,
                    shop_name
                ))
                self.conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.info(f"Error updating customer: {e}")
            self.conn.rollback()
            return False

    def delete_customer(self, customer_id, shop_name):
        query = "DELETE FROM customers WHERE id = %s AND shop_name = %s"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (customer_id, shop_name))
                self.conn.commit()
                return True
        except Exception as e:
            logging.info(f"Error deleting customer: {e}")
            self.conn.rollback()
            return False
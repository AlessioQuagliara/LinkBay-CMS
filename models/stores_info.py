# Classe per STORES_INFO --------------------------------------------------------------------------------------------
import logging
logging.basicConfig(level=logging.INFO)

class StoreInfo:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Ottieni le informazioni di uno store specifico
    def get_store_by_name(self, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM stores_info WHERE shop_name = %s", (shop_name,))
                store = cursor.fetchone()
            return store
        except Exception as e:
            logging.error(f"Error fetching store info for '{shop_name}': {e}")
            return None

    # Crea un nuovo store
    def create_store(self, shop_name, owner_name, email, phone=None, industry=None, description=None, website_url=None, revenue=0.0):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO stores_info 
                    (shop_name, owner_name, email, phone, industry, description, website_url, revenue, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())""",
                    (shop_name, owner_name, email, phone, industry, description, website_url, revenue)
                )
                self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error creating store '{shop_name}': {e}")
            return False

    # Aggiorna le informazioni di uno store
    def update_store(self, shop_name, owner_name=None, email=None, phone=None, industry=None, description=None, website_url=None, revenue=None):
        try:
            with self.conn.cursor() as cursor:
                query = """UPDATE stores_info 
                           SET updated_at = NOW()"""
                params = []

                # Aggiungi i campi aggiornabili alla query dinamicamente
                if owner_name:
                    query += ", owner_name = %s"
                    params.append(owner_name)
                if email:
                    query += ", email = %s"
                    params.append(email)
                if phone:
                    query += ", phone = %s"
                    params.append(phone)
                if industry:
                    query += ", industry = %s"
                    params.append(industry)
                if description:
                    query += ", description = %s"
                    params.append(description)
                if website_url:
                    query += ", website_url = %s"
                    params.append(website_url)
                if revenue is not None:
                    query += ", revenue = %s"
                    params.append(revenue)

                # Aggiungi la condizione WHERE
                query += " WHERE shop_name = %s"
                params.append(shop_name)

                cursor.execute(query, params)
                self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error updating store '{shop_name}': {e}")
            return False

    # Elimina uno store
    def delete_store(self, shop_name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM stores_info WHERE shop_name = %s", (shop_name,))
                self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error deleting store '{shop_name}': {e}")
            return False

    # Ottieni la lista di tutti gli store
    def get_all_stores(self):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM stores_info")
                stores = cursor.fetchall()
            return stores
        except Exception as e:
            logging.error(f"Error fetching all stores: {e}")
            return []

    # Controlla se uno store esiste
    def store_exists(self, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT 1 FROM stores_info WHERE shop_name = %s", (shop_name,))
                exists = cursor.fetchone()
            return exists is not None
        except Exception as e:
            logging.error(f"Error checking if store exists for '{shop_name}': {e}")
            return False

    def get_store_by_shop_name(self, shop_name):
            """
            Recupera le informazioni del negozio dalla tabella stores_info in base al shop_name.
            """
            try:
                with self.conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        "SELECT * FROM stores_info WHERE shop_name = %s LIMIT 1", (shop_name,)
                    )
                    return cursor.fetchone()  # Restituisce il primo risultato o None se non trovato
            except Exception as e:
                logging.error(f"Error fetching store info for '{shop_name}': {e}")
                return None
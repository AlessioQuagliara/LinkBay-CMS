import logging
logging.basicConfig(level=logging.INFO)

class Navbar:
    def __init__(self, db_conn):
        self.conn = db_conn
    
    def get_navbar_links(self, shop_name):
        """
        Recupera tutti i link della navbar ordinati per posizione.
        """
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM navbar_links WHERE shop_name = %s ORDER BY position ASC", (shop_name,))
            return cursor.fetchall()

    def create_navbar_link(self, shop_name, link_text, link_url, link_type, parent_id=None, position=None):
            """
            Crea un nuovo link nella navbar.
            """
            try:
                with self.conn.cursor() as cursor:
                    query = """
                        INSERT INTO navbar_links (shop_name, link_text, link_url, link_type, parent_id, position, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """
                    cursor.execute(query, (shop_name, link_text, link_url, link_type, parent_id, position))
                    self.conn.commit()
            except Exception as e:
                logging.error(f"Errore durante l'inserimento del link navbar: {str(e)}")
                raise

    def update_navbar_link(self, link_id, shop_name, link_text, link_url, link_type, parent_id=None, position=None):
        """
        Aggiorna un link esistente nella navbar.
        """
        with self.conn.cursor() as cursor:
            query = """
                UPDATE navbar_links
                SET link_text = %s, link_url = %s, link_type = %s, parent_id = %s, position = %s, updated_at = NOW()
                WHERE id = %s AND shop_name = %s
            """
            cursor.execute(query, (link_text, link_url, link_type, parent_id, position, link_id, shop_name))
            self.conn.commit()

    def delete_navbar_link(self, link_id, shop_name):
        """
        Elimina un link dalla navbar.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM navbar_links WHERE id = %s AND shop_name = %s", (link_id, shop_name))
                self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Errore durante l'eliminazione del link: {e}")
            self.conn.rollback()
            return False

    def delete_all_navbar_links(self, shop_name):
        """
        Elimina tutti i link della navbar per un determinato shop.
        """
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM navbar_links WHERE shop_name = %s", (shop_name,))
            self.conn.commit()

    def reorder_navbar_links(self, shop_name, order_list):
        """
        Aggiorna la posizione dei link nella navbar in base al nuovo ordine.
        """
        with self.conn.cursor() as cursor:
            for position, link_id in enumerate(order_list, start=1):
                cursor.execute("""
                    UPDATE navbar_links
                    SET position = %s, updated_at = NOW()
                    WHERE id = %s AND shop_name = %s
                """, (position, link_id, shop_name))
            self.conn.commit()
# Classe per PAGES --------------------------------------------------------------------------------------------

class Page:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Ottieni tutte le pagine per un negozio specifico
    def get_all_pages(self, shop_name):
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM pages WHERE shop_name = %s", (shop_name,))
            pages = cursor.fetchall()
        return pages
    
    # Ottieni le inclusioni navbar per un negozio specifico
    def get_navbar(self, shop_name):
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT content FROM pages WHERE slug = 'navbar' AND shop_name = %s", (shop_name,))
            page = cursor.fetchone()
        return page['content'] if page else ''

    # Ottieni il footer per un negozio specifico
    def get_footer(self, shop_name):
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT content FROM pages WHERE slug = 'footer' AND shop_name = %s", (shop_name,))
            page = cursor.fetchone()
        return page['content'] if page else ''
        
    # Ottieni una pagina per slug e negozio
    def get_page_by_slug(self, slug, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM pages WHERE slug = %s AND shop_name = %s", (slug, shop_name))
                page = cursor.fetchone()
        except Exception as e:
            print(f"Errore durante il recupero della pagina: {e}")
            page = None
        return page

    # Crea una nuova pagina per un negozio specifico
    def create_page(self, title, description, keywords, slug, content, theme_name, paid, language, published, shop_name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO pages 
                    (title, description, keywords, slug, content, theme_name, paid, language, published, shop_name, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())""",
                    (title, description, keywords, slug, content, theme_name, paid, language, published, shop_name)
                )
                self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating page: {e}")
            return False

    # Aggiorna il contenuto della pagina per un negozio specifico
    def update_page_content(self, page_id, content, shop_name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE pages 
                    SET content = %s, updated_at = NOW() 
                    WHERE id = %s AND shop_name = %s""",
                    (content, page_id, shop_name)
                )
                self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating page content: {e}")
            return False

    # Aggiorna i metadati SEO di una pagina per un negozio specifico
    def update_page_seo(self, page_id, title, description, keywords, slug, shop_name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE pages 
                    SET title = %s, description = %s, keywords = %s, slug = %s, updated_at = NOW() 
                    WHERE id = %s AND shop_name = %s""",
                    (title, description, keywords, slug, page_id, shop_name)
                )
                self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating page SEO: {e}")
            return False

    # Elimina una pagina per un negozio specifico
    def delete_page(self, page_id, shop_name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM pages WHERE id = %s AND shop_name = %s", (page_id, shop_name))
                self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error deleting page: {e}")
            return False
        
    # Aggiorna il contenuto della pagina per slug e negozio
    def update_page_content_by_slug(self, slug, content, shop_name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE pages 
                    SET content = %s, updated_at = NOW() 
                    WHERE slug = %s AND shop_name = %s""",
                    (content, slug, shop_name)
                )
                self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating page content: {e}")
            return False
        
    # ottieni la pagina tradotta
    def get_page_by_slug_and_language(self, slug, language, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM pages WHERE slug = %s AND language = %s AND shop_name = %s", 
                            (slug, language, shop_name))
                page = cursor.fetchone()
        except Exception as e:
            print(f"Error fetching translated page: {e}")
            page = None
        return page
    
    # Crea la pagina tradotta nel caso non ci sia
    def update_or_create_page_content(self, page_id, content, language, shop_name):
        try:
            with self.conn.cursor() as cursor:
                # Verifica se esiste già una pagina con lo stesso ID e lingua
                cursor.execute("SELECT id FROM pages WHERE id = %s AND language = %s AND shop_name = %s", 
                            (page_id, language, shop_name))
                existing_page = cursor.fetchone()

                if existing_page:
                    # Se esiste, aggiornala
                    cursor.execute(
                        """UPDATE pages 
                        SET content = %s, updated_at = NOW() 
                        WHERE id = %s AND language = %s AND shop_name = %s""",
                        (content, page_id, language, shop_name)
                    )
                else:
                    # Se non esiste, creala
                    cursor.execute(
                        """INSERT INTO pages (id, content, language, shop_name, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, NOW(), NOW())""",
                        (page_id, content, language, shop_name)
                    )

                self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating or creating page content: {e}")
            return False

    def get_product_references(self, page_id):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT product_id 
                    FROM page_products 
                    WHERE page_id = %s
                """
                cursor.execute(query, (page_id,))
                results = cursor.fetchall()
            return [row['product_id'] for row in results]
        except Exception as e:
            print(f"Errore durante il recupero dei riferimenti ai prodotti: {e}")
            return []

    def get_products_by_ids(self, product_ids):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = f"""
                    SELECT id, name, price
                    FROM products
                    WHERE id IN ({','.join(['%s'] * len(product_ids))})
                """
                cursor.execute(query, product_ids)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching products by IDs: {e}")
            return []
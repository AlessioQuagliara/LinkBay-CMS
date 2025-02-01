# Classe per PAGES --------------------------------------------------------------------------------------------
import logging, os, json
logging.basicConfig(level=logging.INFO)

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
            logging.info(f"Errore durante il recupero della pagina: {e}")
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
            logging.info(f"Error creating page: {e}")
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
            logging.info(f"Error updating page content: {e}")
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
            logging.info(f"Error updating page SEO: {e}")
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
            logging.info(f"Error deleting page: {e}")
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
            logging.info(f"Error updating page content: {e}")
            return False
        
    # ottieni la pagina tradotta
    def get_page_by_slug_and_language(self, slug, language, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM pages WHERE slug = %s AND language = %s AND shop_name = %s", 
                            (slug, language, shop_name))
                page = cursor.fetchone()
        except Exception as e:
            logging.info(f"Error fetching translated page: {e}")
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
            logging.info(f"Error updating or creating page content: {e}")
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
            logging.info(f"Errore durante il recupero dei riferimenti ai prodotti: {e}")
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
            logging.info(f"Error fetching products by IDs: {e}")
            return []
        
    def apply_theme(self, theme_name, shop_name):
        """
        Applica un tema a un negozio: salva il nome del tema e importa le pagine associate
        nella tabella `pages` e aggiorna la tabella `websettings` con i dati specifici del tema.
        """
        paid = 'Yes'
        try:
            # Percorso ai file predefiniti per i temi
            theme_path = os.path.join('themes', f'{theme_name}.json')

            # Leggi i dati del tema dal file JSON
            with open(theme_path, 'r') as theme_file:
                theme_data = json.load(theme_file)

            # Estrai informazioni generali per `websettings`
            head_content = theme_data.get('head', '')
            foot_content = theme_data.get('foot', '')
            script_content = theme_data.get('script', '')

            with self.conn.cursor() as cursor:
                # Inserisci o aggiorna i dati di `websettings`
                cursor.execute(
                    """INSERT INTO web_settings (shop_name, theme_name, google_analytics, facebook_pixel, tiktok_pixel, head, favicon, foot, script)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        theme_name = VALUES(theme_name),
                        google_analytics = VALUES(google_analytics),
                        facebook_pixel = VALUES(facebook_pixel),
                        tiktok_pixel = VALUES(tiktok_pixel),
                        head = VALUES(head),
                        favicon = VALUES(favicon),
                        foot = VALUES(foot),
                        script = VALUES(script)""",
                    (
                        shop_name,
                        theme_name,
                        theme_data.get('google_analytics', ' '),  # Default value
                        theme_data.get('facebook_pixel', ' '),    # Default value
                        theme_data.get('tiktok_pixel', ' '),      # Default value
                        head_content if head_content.strip() else ' ',  # Ensure non-empty
                        theme_data.get('favicon', ' '),          # Default value
                        foot_content if foot_content.strip() else ' ',  # Ensure non-empty
                        script_content if script_content.strip() else ' ',  # Ensure non-empty
                    )
                )

                # Inserisci o aggiorna le pagine nella tabella `pages`
                for page in theme_data['pages']:
                    if not all(key in page for key in ['title', 'slug', 'content']):
                        logging.error(f"Missing required fields in page: {page}")
                        continue

                    logging.info(f"Inserting page: {page['title']} for shop: {shop_name}")

                    cursor.execute(
                        """INSERT INTO pages 
                        (title, description, keywords, slug, content, theme_name, paid, language, published, shop_name, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        ON DUPLICATE KEY UPDATE 
                        content = VALUES(content), 
                        updated_at = NOW()""",
                        (
                            page.get('title', ''),
                            page.get('description', None),
                            page.get('keywords', None),
                            page.get('slug', ''),
                            page.get('content', None),
                            theme_name,
                            paid,
                            page.get('language', None),
                            1 if page.get('published', True) else 0,
                            shop_name,
                        )
                    )

                self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error applying theme '{theme_name}' for shop '{shop_name}': {e}")
            return False
        
    def get_published_pages(self, shop_name):
            """
            Recupera solo le pagine pubblicate di un negozio, escludendo 'navbar' e 'footer'.
            """
            with self.conn.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("""
                        SELECT id, title, slug
                        FROM pages
                        WHERE shop_name = %s 
                        AND published = 1 
                        AND slug NOT IN ('navbar', 'footer')
                        ORDER BY created_at DESC
                    """, (shop_name,))
                    pages = cursor.fetchall()
                    return pages
                except Exception as e:
                    logging.error(f"Errore nel recupero delle pagine pubblicate: {e}")
                    return []                                                               
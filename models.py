from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

# CLASSE PER GESTIONE DATABASE ---------------------------------------------------------------------------------------------------

class Database:
    def __init__(self, config):
        self.config = config
        self.conn = None

    def connect(self):
        if not self.conn:
            self.conn = mysql.connector.connect(
                host=self.config['DB_HOST'],
                user=self.config['DB_USER'],
                password=self.config['DB_PASSWORD'],
                database=self.config['DB_NAME'],
                port=self.config['DB_PORT']
            )
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

# CLASSE PER GESTIONE UTENTI ---------------------------------------------------------------------------------------------------

class User:
    def __init__(self, db_conn):
        self.conn = db_conn

    def get_all_users(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT id, email, nome, cognome, telefono, profilo_foto, is_2fa_enabled FROM user")
        users = cursor.fetchall()
        cursor.close()
        return users

    def get_user_by_id(self, user_id):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return user

    def get_user_by_email(self, email):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        return user

    def create_user(self, email, password, nome, cognome, telefono, profilo_foto):
        cursor = self.conn.cursor()
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO user (email, password, nome, cognome, telefono, profilo_foto) VALUES (%s, %s, %s, %s, %s, %s)",
            (email, hashed_password, nome, cognome, telefono, profilo_foto)
        )
        self.conn.commit()
        cursor.close()

    def update_user(self, user_id, nome, cognome, telefono, profilo_foto):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE user SET nome = %s, cognome = %s, telefono = %s, profilo_foto = %s WHERE id = %s",
            (nome, cognome, telefono, profilo_foto, user_id)
        )
        self.conn.commit()
        cursor.close()

    def delete_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
        self.conn.commit()
        cursor.close()

# Classe per ShopList ---------------------------------------------------------------------------------------------------
class ShopList:
    def __init__(self, db_conn):
        self.conn = db_conn

    def get_shop_by_name(self, shop_name):
        cursor = self.conn.cursor(dictionary=True)
        query = """
            SELECT id, shop_name, themeOptions, domain, user_id, partner_id
            FROM ShopList
            WHERE shop_name = %s
        """
        cursor.execute(query, (shop_name,))
        shop = cursor.fetchone() 
        cursor.close()
        return shop
    
    def get_shop_by_name_or_domain(self, value):
        cursor = self.conn.cursor(dictionary=True)
        query = """
            SELECT id, shop_name, themeOptions, domain, user_id, partner_id
            FROM ShopList
            WHERE shop_name = %s OR domain = %s
        """
        cursor.execute(query, (value, value))
        shop = cursor.fetchone()
        cursor.close()
        return shop
    
# Classe per UserStoreAccess --------------------------------------------------------------------------------------------

class UserStoreAccess:
    def __init__(self, db_conn):
        self.conn = db_conn

    def grant_access(self, user_id, shop_id, access_level='viewer'):
        """
        Concede accesso a un utente per uno specifico store con un livello di accesso.
        """
        cursor = self.conn.cursor()
        query = """
            INSERT INTO user_store_access (user_id, shop_id, access_level)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE access_level = %s
        """
        cursor.execute(query, (user_id, shop_id, access_level, access_level))
        self.conn.commit()
        cursor.close()

    def revoke_access(self, user_id, shop_id):
        """
        Revoca l'accesso di un utente per uno specifico store.
        """
        cursor = self.conn.cursor()
        query = "DELETE FROM user_store_access WHERE user_id = %s AND shop_id = %s"
        cursor.execute(query, (user_id, shop_id))
        self.conn.commit()
        cursor.close()

    def has_access(self, user_id, shop_id):
        """
        Controlla se un utente ha accesso a uno specifico store.
        """
        cursor = self.conn.cursor(dictionary=True)
        query = "SELECT * FROM user_store_access WHERE user_id = %s AND shop_id = %s"
        cursor.execute(query, (user_id, shop_id))
        access = cursor.fetchone()
        cursor.close()
        return access is not None

    def get_access_level(self, user_id, shop_id):
        """
        Recupera il livello di accesso di un utente per uno specifico store.
        """
        cursor = self.conn.cursor(dictionary=True)
        query = "SELECT access_level FROM user_store_access WHERE user_id = %s AND shop_id = %s"
        cursor.execute(query, (user_id, shop_id))
        access = cursor.fetchone()
        cursor.close()
        return access['access_level'] if access else None

    def get_user_stores(self, user_id):
        """
        Recupera tutti gli store a cui un utente ha accesso.
        """
        cursor = self.conn.cursor(dictionary=True)
        query = """
            SELECT ShopList.id, ShopList.shop_name, user_store_access.access_level
            FROM user_store_access
            JOIN ShopList ON user_store_access.shop_id = ShopList.id
            WHERE user_store_access.user_id = %s
        """
        cursor.execute(query, (user_id,))
        stores = cursor.fetchall()
        cursor.close()
        return stores

# Classe per Web_Settings --------------------------------------------------------------------------------------------

class WebSettings:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per ottenere le impostazioni web di un negozio specifico
    def get_web_settings(self, shop_name):
        cursor = self.conn.cursor(dictionary=True)
        query = """SELECT * FROM web_settings WHERE shop_name = %s"""
        cursor.execute(query, (shop_name,))
        web_settings = cursor.fetchone()  # Ottieni le impostazioni specifiche per il negozio
        cursor.close()
        return web_settings

    # Metodo per aggiornare head, foot e script nella tabella web_settings per un negozio specifico
    def update_web_settings(self, shop_name, head_content, script_content, foot_content):
        cursor = self.conn.cursor()
        try:
            query = """
                UPDATE web_settings 
                SET head = %s, script = %s, foot = %s
                WHERE shop_name = %s
            """
            cursor.execute(query, (head_content, script_content, foot_content, shop_name))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating web settings: {e}")
            cursor.close()
            return False

# Classe per PAGES --------------------------------------------------------------------------------------------

class Page:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Ottieni tutte le pagine per un negozio specifico
    def get_all_pages(self, shop_name):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pages WHERE shop_name = %s", (shop_name,))
        pages = cursor.fetchall()
        cursor.close()
        return pages
    
    # Ottieni le inclusioni navbar per un negozio specifico
    def get_navbar(self, shop_name):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT content FROM pages WHERE slug = 'navbar' AND shop_name = %s", (shop_name,))
        page = cursor.fetchone()
        cursor.close()
        return page['content'] if page else ''

    # Ottieni il footer per un negozio specifico
    def get_footer(self, shop_name):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT content FROM pages WHERE slug = 'footer' AND shop_name = %s", (shop_name,))
        page = cursor.fetchone()
        cursor.close()
        return page['content'] if page else ''
        
    # Ottieni una pagina per slug e negozio
    def get_page_by_slug(self, slug, shop_name):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM pages WHERE slug = %s AND shop_name = %s", (slug, shop_name))
            page = cursor.fetchone()
        except Exception as e:
            print(f"Errore durante il recupero della pagina: {e}")
            page = None
        finally:
            cursor.close()
        
        return page

    # Crea una nuova pagina per un negozio specifico
    def create_page(self, title, description, keywords, slug, content, theme_name, paid, language, published, shop_name):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO pages 
                (title, description, keywords, slug, content, theme_name, paid, language, published, shop_name, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())""",
                (title, description, keywords, slug, content, theme_name, paid, language, published, shop_name)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating page: {e}")
            cursor.close()
            return False

#    # Aggiorna il contenuto della pagina per un negozio specifico
    def update_page_content(self, page_id, content, shop_name):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """UPDATE pages 
                SET content = %s, updated_at = NOW() 
                WHERE id = %s AND shop_name = %s""",
                (content, page_id, shop_name)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating page content: {e}")
            cursor.close()
            return False

        
    # Aggiorna i metadati SEO di una pagina per un negozio specifico
    def update_page_seo(self, page_id, title, description, keywords, slug, shop_name):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """UPDATE pages 
                SET title = %s, description = %s, keywords = %s, slug = %s, updated_at = NOW() 
                WHERE id = %s AND shop_name = %s""",
                (title, description, keywords, slug, page_id, shop_name)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating page SEO: {e}")
            cursor.close()
            return False

    # Elimina una pagina per un negozio specifico
    def delete_page(self, page_id, shop_name):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM pages WHERE id = %s AND shop_name = %s", (page_id, shop_name))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error deleting page: {e}")
            cursor.close()
            return False
        
    # Aggiorna il contenuto della pagina per slug e negozio
    def update_page_content_by_slug(self, slug, content, shop_name):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """UPDATE pages 
                SET content = %s, updated_at = NOW() 
                WHERE slug = %s AND shop_name = %s""",
                (content, slug, shop_name)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating page content: {e}")
            cursor.close()
            return False
        
    # ottieni la pagina tradotta
    def get_page_by_slug_and_language(self, slug, language, shop_name):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM pages WHERE slug = %s AND language = %s AND shop_name = %s", 
                        (slug, language, shop_name))
            page = cursor.fetchone()
        except Exception as e:
            print(f"Error fetching translated page: {e}")
            page = None
        finally:
            cursor.close()
        return page
    
    # Crea la pagina tradotta nel caso non ci sia
    def update_or_create_page_content(self, page_id, content, language, shop_name):
        cursor = self.conn.cursor()
        try:
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
        finally:
            cursor.close()


# Classe per Cookie e Policy --------------------------------------------------------------------------------------------

class CookiePolicy:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per ottenere le impostazioni del banner dei cookie per uno specifico negozio
    def get_policy_by_shop(self, shop_name):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM cookie_policy WHERE shop_name = %s", (shop_name,))
            policy = cursor.fetchone()
        finally:
            cursor.close()
        return policy

    # ----------------- Metodi per le politiche dei cookie interne -----------------

    # Metodo per aggiornare le impostazioni interne del banner dei cookie
    def update_internal_policy(self, shop_name, title, text_content, button_text, 
                               background_color, button_color, button_text_color, 
                               text_color, entry_animation):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE cookie_policy
                SET title = %s, text_content = %s, button_text = %s, 
                    background_color = %s, button_color = %s, button_text_color = %s, 
                    text_color = %s, entry_animation = %s, use_third_party = 0,
                    updated_at = NOW()
                WHERE shop_name = %s
            """, (title, text_content, button_text, background_color, button_color, 
                  button_text_color, text_color, entry_animation, shop_name))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating internal cookie policy: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()

    # Metodo per creare una nuova impostazione interna del banner dei cookie
    def create_internal_policy(self, shop_name, title, text_content, button_text, 
                               background_color, button_color, button_text_color, 
                               text_color, entry_animation):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO cookie_policy 
                (shop_name, title, text_content, button_text, background_color, button_color, 
                 button_text_color, text_color, entry_animation, use_third_party, 
                 created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0, NOW(), NOW())
            """, (shop_name, title, text_content, button_text, background_color, button_color, 
                  button_text_color, text_color, entry_animation))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating internal cookie policy: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()

    # ----------------- Metodi per le politiche dei cookie di terze parti -----------------

    # Metodo per aggiornare le impostazioni del banner dei cookie di terze parti
    def update_third_party_policy(self, shop_name, use_third_party, third_party_cookie, third_party_privacy, 
                                third_party_terms, third_party_consent):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE cookie_policy
                SET use_third_party = %s, third_party_cookie = %s, 
                    third_party_privacy = %s, third_party_terms = %s, 
                    third_party_consent = %s, updated_at = NOW()
                WHERE shop_name = %s
            """, (use_third_party, third_party_cookie, third_party_privacy, third_party_terms, 
                third_party_consent, shop_name))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating third-party cookie policy: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()

    # Metodo per creare una nuova impostazione del banner dei cookie di terze parti
    def create_third_party_policy(self, shop_name, use_third_party, third_party_cookie, third_party_privacy, 
                                third_party_terms, third_party_consent):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO cookie_policy 
                (shop_name, use_third_party, third_party_cookie, third_party_privacy, 
                third_party_terms, third_party_consent, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (shop_name, use_third_party, third_party_cookie, third_party_privacy, 
                third_party_terms, third_party_consent))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating third-party cookie policy: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()

# Classe per i PLUGINS e gli ADDONS --------------------------------------------------------------------------------------------

class CMSAddon:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per ottenere tutti gli addon di un certo tipo dalla tabella cms_addons
    def get_addons_by_type(self, addon_type):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM cms_addons WHERE type = %s", (addon_type,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching addons by type: {e}")
            return []
        finally:
            cursor.close()

    # Metodo per selezionare un addon per uno specifico negozio, aggiornando il suo stato
    def select_addon(self, shop_name, addon_id, addon_type):
        cursor = self.conn.cursor()
        try:
            # Verifica se l'addon è già stato acquistato
            cursor.execute("""
                SELECT status FROM shop_addons 
                WHERE shop_name = %s AND addon_id = %s
            """, (shop_name, addon_id))
            result = cursor.fetchone()
            
            if result and result['status'] == 'purchased':
                # Se l'add-on è già acquistato, non modificarlo
                print(f"Addon {addon_id} is already purchased and cannot be re-selected.")
                return False
            
            # Deseleziona altri addon dello stesso tipo per il negozio, eccetto quelli "purchased"
            cursor.execute("""
                UPDATE shop_addons
                SET status = 'deselected'
                WHERE shop_name = %s AND addon_type = %s AND status = 'selected'
            """, (shop_name, addon_type))
            
            # Inserisce o aggiorna l'addon selezionato come 'selected'
            cursor.execute("""
                INSERT INTO shop_addons (shop_name, addon_id, addon_type, status, updated_at)
                VALUES (%s, %s, %s, 'selected', NOW())
                ON DUPLICATE KEY UPDATE status = 'selected', updated_at = NOW()
            """, (shop_name, addon_id, addon_type))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error selecting addon for shop: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()

    # Metodo per acquistare un addon per uno specifico negozio, impostando lo stato su 'purchased'
    def purchase_addon(self, shop_name, addon_id, addon_type):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO shop_addons (shop_name, addon_id, addon_type, status, updated_at)
                VALUES (%s, %s, %s, 'purchased', NOW())
                ON DUPLICATE KEY UPDATE status = 'purchased', updated_at = NOW()
            """, (shop_name, addon_id, addon_type))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error purchasing addon for shop: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()

    # Metodo per ottenere lo stato di un addon specifico per un negozio
    def get_addon_status(self, shop_name, addon_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT status FROM shop_addons 
                WHERE shop_name = %s AND addon_id = %s
            """, (shop_name, addon_id))
            result = cursor.fetchone()
            return result['status'] if result else None
        except Exception as e:
            print(f"Error fetching addon status: {e}")
            return None
        finally:
            cursor.close()

    def update_shop_addon_status(self, shop_name, addon_id, addon_type, status):
        cursor = self.conn.cursor()
        try:
            # Usa ON DUPLICATE KEY UPDATE per eseguire un upsert
            cursor.execute("""
                INSERT INTO shop_addons (shop_name, addon_id, addon_type, status, updated_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE 
                    status = VALUES(status), 
                    updated_at = NOW()
            """, (shop_name, addon_id, addon_type, status))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating shop addon status: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()

    # Metodo per deselezionare altri addon dello stesso tipo, eccetto quelli "purchased"
    def deselect_other_addons(self, shop_name, addon_id, addon_type):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE shop_addons
                SET status = 'deselected'
                WHERE shop_name = %s AND addon_type = %s AND addon_id != %s AND status != 'purchased'
            """, (shop_name, addon_type, addon_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error deselecting other addons: {e}")
            self.conn.rollback()
        finally:
            cursor.close()

    # Metodo per ottenere l'addon di tipo specificato con status 'selected' per uno shop
    def get_selected_addon_for_shop(self, shop_name, addon_type):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT cms_addons.name, cms_addons.description, cms_addons.price, cms_addons.type
                FROM shop_addons
                JOIN cms_addons ON shop_addons.addon_id = cms_addons.id
                WHERE shop_addons.shop_name = %s AND shop_addons.addon_type = %s AND shop_addons.status = 'selected'
                LIMIT 1
            """, (shop_name, addon_type))
            return cursor.fetchone()  # Restituisce l'addon selezionato con nome e altri dettagli, o None
        except Exception as e:
            print(f"Error fetching selected addon: {e}")
            return None
        finally:
            cursor.close()

# STORE PAYMENTS ONLINE ----INERN--- --------------------------------------------------------------------------------------------

class StorePayment:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per creare un nuovo record di pagamento
    def create_payment(self, shop_name, payment_type, amount, stripe_payment_id, status='pending', 
                       integration_name=None, subscription_id=None, currency='EUR'):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO store_payments (shop_name, payment_type, amount, stripe_payment_id, 
                                            status, integration_name, subscription_id, currency, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (shop_name, payment_type, amount, stripe_payment_id, status, integration_name, subscription_id, currency))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating payment record: {e}")
            self.conn.rollback()
            return None
        finally:
            cursor.close()

    # Metodo per aggiornare lo stato di un pagamento
    def update_payment_status(self, stripe_payment_id, status):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE store_payments
                SET status = %s, updated_at = NOW()
                WHERE stripe_payment_id = %s
            """, (status, stripe_payment_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating payment status: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()

    # Metodo per ottenere i pagamenti per uno shop
    def get_payments_by_shop(self, shop_name):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * FROM store_payments
                WHERE shop_name = %s
                ORDER BY created_at DESC
            """, (shop_name,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching payments for shop: {e}")
            return []
        finally:
            cursor.close()

    # Metodo per ottenere i dettagli di un pagamento specifico tramite ID di Stripe
    def get_payment_by_stripe_id(self, stripe_payment_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * FROM store_payments
                WHERE stripe_payment_id = %s
            """, (stripe_payment_id,))
            return cursor.fetchone()    
        except Exception as e:
            print(f"Error fetching payment by Stripe ID: {e}")
            return None
        finally:
            cursor.close()

    # Metodo per ottenere i pagamenti di tipo abbonamento
    def get_subscription_payments(self, shop_name):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * FROM store_payments
                WHERE shop_name = %s AND payment_type = 'subscription'
                ORDER BY created_at DESC
            """, (shop_name,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching subscription payments: {e}")
            return []
        finally:
            cursor.close()

# Classe per PRODOTTI --------------------------------------------------------------------------------------------

class Products:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per ottenere tutti i prodotti
    def get_all_products(self, shop_name):
        cursor = self.conn.cursor(dictionary=True)
        try:
            # Query per estrarre tutti i dati relativi ai prodotti e tabelle correlate
            cursor.execute("""
                SELECT 
                    products.id,
                    products.name,
                    products.description,
                    products.short_description,
                    products.price,
                    products.discount_price,
                    products.stock_quantity,
                    products.sku,
                    products.weight,
                    products.dimensions,
                    products.color,
                    products.material,
                    products.image_url,
                    products.slug,
                    products.is_active,
                    products.created_at,
                    products.updated_at,
                    categories.name AS category_name,
                    brands.name AS brand_name
                FROM products
                LEFT JOIN categories ON products.category_id = categories.id
                LEFT JOIN brands ON products.brand_id = brands.id
                WHERE products.shop_name = %s
            """, (shop_name,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching products for shop: {e}")
            return []
        finally:
            cursor.close()

    # Metodo per ottenere un prodotto per slug
    def get_product_by_slug(self, slug, shop_name):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM products WHERE slug = %s AND shop_name = %s", (slug, shop_name))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching product by slug: {e}")
            return None
        finally:
            cursor.close()

    # Metodo per gestire i prodotti
    def create_product(self, data):
            cursor = self.conn.cursor()
            try:
                query = """
                    INSERT INTO products (name, short_description, description, price, discount_price, stock_quantity, sku, category_id, brand_id, weight, dimensions, color, material, image_url, slug, is_active, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """
                values = (
                    data['name'], data['short_description'], data['description'], data['price'], data['discount_price'], data['stock_quantity'], data['sku'],
                    data['category_id'], data['brand_id'], data['weight'], data['dimensions'], data['color'], data['material'], data['image_url'],
                    data['slug'], data['is_active']
                )
                cursor.execute(query, values)
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error creating product: {e}")
                self.conn.rollback()
                return False
            finally:
                cursor.close()

    # UPDATE PRODOTTO 
    def update_product(self, product_id, data):
        cursor = self.conn.cursor()
        try:
            query = """
                UPDATE products
                SET name = %s, short_description = %s, description = %s, price = %s, discount_price = %s, stock_quantity = %s,
                    sku = %s, category_id = %s, brand_id = %s, weight = %s, dimensions = %s, color = %s, material = %s,
                    image_url = %s, slug = %s, is_active = %s, updated_at = NOW()
                WHERE id = %s
            """
            values = (
                data.get('name'), data.get('short_description'), data.get('description'), data.get('price'),
                data.get('discount_price'), data.get('stock_quantity'), data.get('sku'), data.get('category_id'),
                data.get('brand_id'), data.get('weight'), data.get('dimensions'), data.get('color'), data.get('material'),
                data.get('image_url'), data.get('slug'), data.get('is_active'), product_id
            )
            cursor.execute(query, values)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Database Error: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()

    def get_product_by_id(self, product_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching product: {e}")
            return None
        finally:
            cursor.close()

    def create_product(self, data):
        cursor = self.conn.cursor()
        try:
            query = """
                INSERT INTO products (
                    name, short_description, description, price, discount_price, stock_quantity, sku, 
                    category_id, brand_id, weight, dimensions, color, material, image_url, slug, 
                    is_active, shop_name, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            values = (
                data["name"], data["short_description"], data["description"], data["price"],
                data["discount_price"], data["stock_quantity"], data["sku"], data["category_id"],
                data["brand_id"], data["weight"], data["dimensions"], data["color"],
                data["material"], data["image_url"], data["slug"], data["is_active"],
                data["shop_name"]
            )
            cursor.execute(query, values)
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating product: {e}")
            self.conn.rollback()
            return None
        finally:
            cursor.close()


    # Metodo per eliminare un prodotto
    def delete_product(self, product_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting product: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()

    # Metodo per ottenere i prodotti per categoria
    def get_products_by_category(self, category_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM products WHERE category_id = %s", (category_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching products by category: {e}")
            return []
        finally:
            cursor.close()

    # Metodo per ottenere i prodotti per brand
    def get_products_by_brand(self, brand_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM products WHERE brand_id = %s", (brand_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching products by brand: {e}")
            return []
        finally:
            cursor.close()

    # Metodo per ottenere le categorie
    def get_all_categories(self, shop_name):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM categories WHERE shop_name = %s", (shop_name,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []
        finally:
            cursor.close()

    # Metodo per ottenere gli attributi di un prodotto
    def get_product_attributes(self, product_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM product_attributes WHERE product_id = %s", (product_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching product attributes: {e}")
            return []
        finally:
            cursor.close()

    # Metodo per aggiungere un attributo a un prodotto
    def add_product_attribute(self, product_id, attribute_name, attribute_value):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO product_attributes (product_id, attribute_name, attribute_value)
                VALUES (%s, %s, %s)
            """, (product_id, attribute_name, attribute_value))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding product attribute: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()

    # Metodo per ottenere le immagini di un prodotto
    def get_product_images(self, product_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM product_images WHERE product_id = %s", (product_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching product images: {e}")
            return []
        finally:
            cursor.close()

    # Metodo per aggiungere un'immagine a un prodotto
    def add_product_image(self, product_id, image_url, is_main=False):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO product_images (product_id, image_url, is_main)
                VALUES (%s, %s, %s)
            """, (product_id, image_url, is_main))
            self.conn.commit()
            return cursor.lastrowid  # Restituisci l'ID del record appena inserito
        except Exception as e:
            print(f"Error adding product image: {e}")
            self.conn.rollback()
            return None
        finally:
            cursor.close()
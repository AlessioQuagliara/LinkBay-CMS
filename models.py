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
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id, email, nome, cognome, telefono, profilo_foto, is_2fa_enabled FROM user")
                users = cursor.fetchall()
            return users
        except Exception as e:
            print(f"Error fetching all users: {e}")
            return []

    def get_user_by_id(self, user_id):
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        return user

    def get_user_by_email(self, email):
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
            user = cursor.fetchone()
        return user

    def create_user(self, email, password, nome, cognome, telefono, profilo_foto):
        hashed_password = generate_password_hash(password)
        with self.conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO user (email, password, nome, cognome, telefono, profilo_foto) VALUES (%s, %s, %s, %s, %s, %s)",
                (email, hashed_password, nome, cognome, telefono, profilo_foto)
            )
            self.conn.commit()

    def update_user(self, user_id, nome, cognome, telefono, profilo_foto):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE user SET nome = %s, cognome = %s, telefono = %s, profilo_foto = %s WHERE id = %s",
                (nome, cognome, telefono, profilo_foto, user_id)
            )
            self.conn.commit()

    def delete_user(self, user_id):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
            self.conn.commit()

# Classe per ShopList ---------------------------------------------------------------------------------------------------
class ShopList:
    def __init__(self, db_conn):
        self.conn = db_conn

    def get_shop_by_name(self, shop_name):
        query = """
            SELECT id, shop_name, themeOptions, domain, user_id, partner_id
            FROM ShopList
            WHERE shop_name = %s
        """
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (shop_name,))
            shop = cursor.fetchone()
        return shop
    
    def get_shop_by_name_or_domain(self, value):
        query = """
            SELECT id, shop_name, themeOptions, domain, user_id, partner_id
            FROM ShopList
            WHERE shop_name = %s OR domain = %s
        """
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (value, value))
            shop = cursor.fetchone()
        return shop
    
# Classe per UserStoreAccess --------------------------------------------------------------------------------------------

class UserStoreAccess:
    def __init__(self, db_conn):
        self.conn = db_conn

    def grant_access(self, user_id, shop_id, access_level='viewer'):
        """
        Concede accesso a un utente per uno specifico store con un livello di accesso.
        """
        query = """
            INSERT INTO user_store_access (user_id, shop_id, access_level)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE access_level = %s
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (user_id, shop_id, access_level, access_level))
            self.conn.commit()

    def revoke_access(self, user_id, shop_id):
        """
        Revoca l'accesso di un utente per uno specifico store.
        """
        query = "DELETE FROM user_store_access WHERE user_id = %s AND shop_id = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(query, (user_id, shop_id))
            self.conn.commit()

    def has_access(self, user_id, shop_id):
        """
        Controlla se un utente ha accesso a uno specifico store.
        """
        query = "SELECT * FROM user_store_access WHERE user_id = %s AND shop_id = %s"
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (user_id, shop_id))
            access = cursor.fetchone()
        return access is not None

    def get_access_level(self, user_id, shop_id):
        """
        Recupera il livello di accesso di un utente per uno specifico store.
        """
        query = "SELECT access_level FROM user_store_access WHERE user_id = %s AND shop_id = %s"
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (user_id, shop_id))
            access = cursor.fetchone()
        return access['access_level'] if access else None

    def get_user_stores(self, user_id):
        """
        Recupera tutti gli store a cui un utente ha accesso.
        """
        query = """
            SELECT ShopList.id, ShopList.shop_name, user_store_access.access_level
            FROM user_store_access
            JOIN ShopList ON user_store_access.shop_id = ShopList.id
            WHERE user_store_access.user_id = %s
        """
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (user_id,))
            stores = cursor.fetchall()
        return stores

# Classe per Web_Settings --------------------------------------------------------------------------------------------

class WebSettings:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per ottenere le impostazioni web di un negozio specifico
    def get_web_settings(self, shop_name):
        query = """SELECT * FROM web_settings WHERE shop_name = %s"""
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (shop_name,))
            web_settings = cursor.fetchone()  # Ottieni le impostazioni specifiche per il negozio
        return web_settings

    # Metodo per aggiornare head, foot e script nella tabella web_settings per un negozio specifico
    def update_web_settings(self, shop_name, head_content, script_content, foot_content):
        query = """
            UPDATE web_settings 
            SET head = %s, script = %s, foot = %s
            WHERE shop_name = %s
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (head_content, script_content, foot_content, shop_name))
                self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating web settings: {e}")
            return False

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


# Classe per Cookie e Policy --------------------------------------------------------------------------------------------

class CookiePolicy:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per ottenere le impostazioni del banner dei cookie per uno specifico negozio
    def get_policy_by_shop(self, shop_name):
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM cookie_policy WHERE shop_name = %s", (shop_name,))
            policy = cursor.fetchone()
        return policy

    # ----------------- Metodi per le politiche dei cookie interne -----------------

    # Metodo per aggiornare le impostazioni interne del banner dei cookie
    def update_internal_policy(self, shop_name, title, text_content, button_text, 
                               background_color, button_color, button_text_color, 
                               text_color, entry_animation):
        try:
            with self.conn.cursor() as cursor:
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

    # Metodo per creare una nuova impostazione interna del banner dei cookie
    def create_internal_policy(self, shop_name, title, text_content, button_text, 
                               background_color, button_color, button_text_color, 
                               text_color, entry_animation):
        try:
            with self.conn.cursor() as cursor:
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

    # ----------------- Metodi per le politiche dei cookie di terze parti -----------------

    # Metodo per aggiornare le impostazioni del banner dei cookie di terze parti
    def update_third_party_policy(self, shop_name, use_third_party, third_party_cookie, third_party_privacy, 
                                third_party_terms, third_party_consent):
        try:
            with self.conn.cursor() as cursor:
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

    # Metodo per creare una nuova impostazione del banner dei cookie di terze parti
    def create_third_party_policy(self, shop_name, use_third_party, third_party_cookie, third_party_privacy, 
                                third_party_terms, third_party_consent):
        try:
            with self.conn.cursor() as cursor:
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

# Classe per i PLUGINS e gli ADDONS --------------------------------------------------------------------------------------------

class CMSAddon:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per ottenere tutti gli addon di un certo tipo dalla tabella cms_addons
    def get_addons_by_type(self, addon_type):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM cms_addons WHERE type = %s", (addon_type,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching addons by type: {e}")
                return []

    # Metodo per selezionare un addon per uno specifico negozio, aggiornando il suo stato
    def select_addon(self, shop_name, addon_id, addon_type):
        with self.conn.cursor() as cursor:
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

    # Metodo per acquistare un addon per uno specifico negozio, impostando lo stato su 'purchased'
    def purchase_addon(self, shop_name, addon_id, addon_type):
        with self.conn.cursor() as cursor:
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

    # Metodo per ottenere lo stato di un addon specifico per un negozio
    def get_addon_status(self, shop_name, addon_id):
        with self.conn.cursor(dictionary=True) as cursor:
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

    def update_shop_addon_status(self, shop_name, addon_id, addon_type, status):
        with self.conn.cursor() as cursor:
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

    # Metodo per deselezionare altri addon dello stesso tipo, eccetto quelli "purchased"
    def deselect_other_addons(self, shop_name, addon_id, addon_type):
        with self.conn.cursor() as cursor:
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

    # Metodo per ottenere l'addon di tipo specificato con status 'selected' per uno shop
    def get_selected_addon_for_shop(self, shop_name, addon_type):
        with self.conn.cursor(dictionary=True) as cursor:
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

# STORE PAYMENTS ONLINE ----INERN--- --------------------------------------------------------------------------------------------

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
            print(f"Error creating payment record: {e}")
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
            print(f"Error updating payment status: {e}")
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
            print(f"Error fetching payments for shop: {e}")
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
            print(f"Error fetching payment by Stripe ID: {e}")
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
            print(f"Error fetching subscription payments: {e}")
            return []

# Classe per PRODOTTI --------------------------------------------------------------------------------------------

class Products:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per ottenere tutti i prodotti
    def get_all_products(self, shop_name):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
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

    # Metodo per ottenere un prodotto per slug
    def get_product_by_slug(self, slug, shop_name):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM products WHERE slug = %s AND shop_name = %s", (slug, shop_name))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error fetching product by slug: {e}")
                return None

    # Metodo per gestire i prodotti
    def create_product(self, data):
        with self.conn.cursor() as cursor:
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

    # UPDATE PRODOTTO 
    def update_product(self, product_id, data):
        with self.conn.cursor() as cursor:
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

    def get_product_by_id(self, product_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error fetching product: {e}")
                return None

    def create_product(self, data):
        with self.conn.cursor() as cursor:
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

    # Metodo per eliminare un prodotto
    def delete_product(self, product_id):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error deleting product: {e}")
                self.conn.rollback()
                return False

    # Metodo per ottenere i prodotti per categoria
    def get_products_by_category(self, category_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM products WHERE category_id = %s", (category_id,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching products by category: {e}")
                return []

    # Metodo per ottenere i prodotti per brand
    def get_products_by_brand(self, brand_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM products WHERE brand_id = %s", (brand_id,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching products by brand: {e}")
                return []

    # Metodo per ottenere le categorie
    def get_all_categories(self, shop_name):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM categories WHERE shop_name = %s", (shop_name,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching categories: {e}")
                return []

    # Metodo per ottenere gli attributi di un prodotto
    def get_product_attributes(self, product_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM product_attributes WHERE product_id = %s", (product_id,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching product attributes: {e}")
                return []

    # Metodo per aggiungere un attributo a un prodotto
    def add_product_attribute(self, product_id, attribute_name, attribute_value):
        with self.conn.cursor() as cursor:
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

    # Metodo per ottenere le immagini di un prodotto
    def get_product_images(self, product_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM product_images WHERE product_id = %s", (product_id,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching product images: {e}")
                return []

    # Metodo per aggiungere un'immagine a un prodotto
    def add_product_image(self, product_id, image_url, is_main=False):
        with self.conn.cursor() as cursor:
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

    def search_products(self, query, shop_subdomain):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                sql = """
                    SELECT * 
                    FROM products 
                    WHERE name LIKE %s AND shop_name = %s
                """
                cursor.execute(sql, ('%' + query + '%', shop_subdomain))
                products = cursor.fetchall()
                print(f"SQL Result: {products}")  # Debug
                return products
            except Exception as e:
                print(f"Error in search_products: {e}")
                return []

    def get_products_by_ids(self, product_ids):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT id, name, price, stock_quantity FROM products WHERE id IN (%s)" % (
                        ','.join(['%s'] * len(product_ids))
                    ),
                    tuple(product_ids)
                )
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching products: {e}")
                return []

    def get_images_for_products(self, product_ids):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = """
                    SELECT product_id, image_url, is_main
                    FROM product_images
                    WHERE product_id IN (%s)
                """ % ','.join(['%s'] * len(product_ids))
                cursor.execute(query, product_ids)
                return cursor.fetchall()
            except Exception as e:
                print(f"Error retrieving product images: {e}")
                return []

# COLLEZIONI ---------------------------------------------------------------------------------------------------

class Collections:
    def __init__(self, db_conn):
        self.conn = db_conn

    def get_all_collections(self, shop_name):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = "SELECT * FROM collections WHERE shop_name = %s"
                cursor.execute(query, (shop_name,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching collections: {e}")
                return []

    def get_collection_by_id(self, collection_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = "SELECT * FROM collections WHERE id = %s"
                cursor.execute(query, (collection_id,))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error fetching collection by ID: {e}")
                return None

    def create_collection(self, data):
        with self.conn.cursor() as cursor:
            try:
                query = """
                    INSERT INTO collections (
                        name, slug, description, image_url,
                        is_active, shop_name, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                """
                values = (
                    data["name"], data["slug"], data["description"], data["image_url"], data["is_active"],
                    data["shop_name"]
                )
                cursor.execute(query, values)
                self.conn.commit()
                return cursor.lastrowid
            except Exception as e:
                print(f"Error creating collection: {e}")
                self.conn.rollback()
                return None

    def update_collection(self, collection_id, data):
        with self.conn.cursor() as cursor:
            try:
                query = """
                    UPDATE collections
                    SET name = %s, slug = %s, description = %s, image_url = %s, is_active = %s, updated_at = NOW()
                    WHERE id = %s
                """
                values = (
                    data.get('name'), data.get('slug'), data.get('description'), data.get('image_url'),
                    data.get('is_active'), collection_id
                )
                cursor.execute(query, values)
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Database Error: {e}")
                self.conn.rollback()
                return False

    def delete_collection(self, collection_id):
        with self.conn.cursor() as cursor:
            try:
                query = "DELETE FROM collections WHERE id = %s"
                cursor.execute(query, (collection_id,))
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error deleting collection: {e}")
                self.conn.rollback()
                return False

    def add_collection_image(self, collection_id, image_url, is_main=False):
        with self.conn.cursor() as cursor:
            try:
                query = """
                    INSERT INTO collection_images (collection_id, image_url, is_main)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (collection_id, image_url, is_main))
                self.conn.commit()
                return cursor.lastrowid
            except Exception as e:
                print(f"Error adding collection image: {e}")
                self.conn.rollback()
                return None

    def get_collection_images(self, collection_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = "SELECT * FROM collection_images WHERE collection_id = %s"
                cursor.execute(query, (collection_id,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching collection images: {e}")
                return []

    def get_collection_image_by_id(self, image_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = "SELECT * FROM collection_images WHERE id = %s"
                cursor.execute(query, (image_id,))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error fetching collection image by ID: {e}")
                return None

    def get_collection_by_slug(self, slug):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = "SELECT * FROM collections WHERE slug = %s"
                cursor.execute(query, (slug,))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error retrieving collection by slug: {e}")
                return None

    def add_product_to_collection(self, collection_id, product_id):
        with self.conn.cursor() as cursor:
            try:
                query = """
                    INSERT INTO collection_products (collection_id, product_id)
                    VALUES (%s, %s)
                """
                cursor.execute(query, (collection_id, product_id))
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error adding product to collection: {e}")
                self.conn.rollback()
                return False

    def remove_product_from_collection(self, collection_id, product_id):
        with self.conn.cursor() as cursor:
            try:
                query = """
                    DELETE FROM collection_products
                    WHERE collection_id = %s AND product_id = %s
                """
                cursor.execute(query, (collection_id, product_id))
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error removing product from collection: {e}")
                self.conn.rollback()
                return False

    def get_products_in_collection(self, collection_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = """
                    SELECT p.*
                    FROM products p
                    JOIN collection_products cp ON p.id = cp.product_id
                    WHERE cp.collection_id = %s
                """
                cursor.execute(query, (collection_id,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching products in collection: {e}")
                return []

    def get_collections_for_product(self, product_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = """
                    SELECT c.*
                    FROM collections c
                    JOIN collection_products cp ON c.id = cp.collection_id
                    WHERE cp.product_id = %s
                """
                cursor.execute(query, (product_id,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching collections for product: {e}")
                return []

    def remove_all_products_from_collection(self, collection_id):
        with self.conn.cursor() as cursor:
            try:
                query = """
                    DELETE FROM collection_products
                    WHERE collection_id = %s
                """
                cursor.execute(query, (collection_id,))
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error removing all products from collection: {e}")
                self.conn.rollback()
                return False

    def remove_products_from_collection(self, collection_id, product_ids):
        with self.conn.cursor() as cursor:
            try:
                query = """
                    DELETE FROM collection_products 
                    WHERE collection_id = %s AND product_id IN (%s)
                """
                formatted_query = query % (collection_id, ', '.join(['%s'] * len(product_ids)))
                cursor.execute(formatted_query, product_ids)
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error removing products from collection: {e}")
                self.conn.rollback()
                return False

    def add_products_to_collection(self, collection_id, product_ids):
        with self.conn.cursor() as cursor:
            try:
                query = """
                    INSERT INTO collection_products (collection_id, product_id) 
                    VALUES (%s, %s)
                """
                values = [(collection_id, product_id) for product_id in product_ids]
                cursor.executemany(query, values)
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error adding products to collection: {e}")
                self.conn.rollback()
                return False

    def get_collections_by_shop(self, shop_name):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = """
                    SELECT * 
                    FROM collections 
                    WHERE shop_name = %s AND is_active = 1
                    ORDER BY name
                """
                cursor.execute(query, (shop_name,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching collections: {e}")
                return []
    
# CATEGORIE ---------------------------------------------------------------------------------------------------

class Categories:
    def __init__(self, db_conn):
        self.conn = db_conn

    def get_all_categories(self, shop_name):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = "SELECT * FROM categories WHERE shop_name = %s"
                cursor.execute(query, (shop_name,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching categories: {e}")
                return []

    def get_category_by_id(self, category_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = "SELECT * FROM categories WHERE id = %s"
                cursor.execute(query, (category_id,))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error fetching category by ID: {e}")
                return None

    def create_category(self, shop_name, name, parent_id=None):
        with self.conn.cursor() as cursor:
            try:
                query = """
                    INSERT INTO categories (shop_name, name, parent_id)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (shop_name, name, parent_id))
                self.conn.commit()
                return cursor.lastrowid
            except Exception as e:
                print(f"Error creating category: {e}")
                self.conn.rollback()
                return None

    def update_category(self, category_id, name=None, parent_id=None):
        with self.conn.cursor() as cursor:
            try:
                fields = []
                values = []
                if name:
                    fields.append("name = %s")
                    values.append(name)
                if parent_id is not None:
                    fields.append("parent_id = %s")
                    values.append(parent_id)

                values.append(category_id)
                query = f"UPDATE categories SET {', '.join(fields)} WHERE id = %s"
                cursor.execute(query, tuple(values))
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error updating category: {e}")
                self.conn.rollback()
                return False

    def delete_category(self, category_id):
        with self.conn.cursor() as cursor:
            try:
                query = "DELETE FROM categories WHERE id = %s"
                cursor.execute(query, (category_id,))
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error deleting category: {e}")
                self.conn.rollback()
                return False

    def get_subcategories(self, parent_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = "SELECT * FROM categories WHERE parent_id = %s"
                cursor.execute(query, (parent_id,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching subcategories: {e}")
                return []

# CLASSE PER ORDINI ---------------------------------------------------------------------------------------------------

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
            print(f"Error deleting order: {e}")
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
            print(f"Error in create_order: {e}")  # Log dell'errore
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
            print(f"Error fetching order: {e}")
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
            print(f"Error updating order: {e}")
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
            print(f"Error fetching orders: {e}")
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
            print(f"Error retrieving order items: {e}")
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
            print(f"Error adding product to order: {e}")
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
            print(f"Error removing order items: {e}")
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
            print(f"Error adding multiple order items: {e}")
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
            print(f"Error updating order item quantities: {e}")
            self.conn.rollback()
            return False

# CLIENTI ---------------------------------------------------------------------------------------------------

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
            print(f"Error creating customer: {e}")
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
            print(f"Error fetching customers: {e}")
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
            print(f"Error updating customer: {e}")
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
            print(f"Error deleting customer: {e}")
            self.conn.rollback()
            return False
        
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
            print(f"Error fetching payments: {e}")
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
            print(f"Error adding payment: {e}")
            self.conn.rollback()
            return None

# SPEDIZIONI ---------------------------------------------------------------------------------------------------

class Shipping:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Metodo per ottenere i dettagli di spedizione associati a un ordine
    def get_shipping_by_order_id(self, order_id):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT id, shipping_method, tracking_number, carrier_name, 
                           estimated_delivery_date, delivery_status, created_at, updated_at
                    FROM shipping
                    WHERE order_id = %s
                """
                cursor.execute(query, (order_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching shipping details: {e}")
            return None

    def get_all_shippings(self, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT 
                        id, shipping_method, tracking_number, carrier_name, 
                        estimated_delivery_date, delivery_status, created_at, updated_at
                    FROM shipping
                    WHERE shop_name = %s
                    ORDER BY created_at DESC
                """
                cursor.execute(query, (shop_name,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching shipping: {e}")
            return []

    # Metodo per aggiungere o aggiornare i dettagli di spedizione
    def upsert_shipping(self, data):
        try:
            with self.conn.cursor() as cursor:
                query = """
                    INSERT INTO shipping (
                        shop_name, order_id, shipping_method, tracking_number, 
                        carrier_name, estimated_delivery_date, delivery_status, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    ON DUPLICATE KEY UPDATE
                        shipping_method = VALUES(shipping_method),
                        tracking_number = VALUES(tracking_number),
                        carrier_name = VALUES(carrier_name),
                        estimated_delivery_date = VALUES(estimated_delivery_date),
                        delivery_status = VALUES(delivery_status),
                        updated_at = NOW()
                """
                values = (
                    data.get("shop_name"),
                    data.get("order_id"),
                    data.get("shipping_method"),
                    data.get("tracking_number"),
                    data.get("carrier_name"),
                    data.get("estimated_delivery_date"),
                    data.get("delivery_status")
                )
                cursor.execute(query, values)
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error upserting shipping: {e}")
            self.conn.rollback()
            return None

# METODI DI SPEDIZIONE ---------------------------------------------------------------------------------------------------

class ShippingMethods:
    def __init__(self, db_conn):
        self.conn = db_conn

    def create_shipping_method(self, data):
        try:
            with self.conn.cursor() as cursor:
                query = """
                    INSERT INTO shipping_methods (
                        shop_name, name, description, country, region, cost, 
                        estimated_delivery_time, is_active, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """
                values = (
                    data["shop_name"],
                    data["name"],
                    data.get("description"),
                    data.get("country"),
                    data.get("region"),
                    data["cost"],
                    data.get("estimated_delivery_time"),
                    data.get("is_active", True)
                )
                cursor.execute(query, values)
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating shipping method: {e}")
            self.conn.rollback()
            return None

    def get_all_shipping_methods(self, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT * FROM shipping_methods
                    WHERE shop_name = %s AND is_active = TRUE
                    ORDER BY created_at DESC
                """
                cursor.execute(query, (shop_name,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching shipping methods: {e}")
            return []

    def update_shipping_method(self, method_id, data):
        try:
            with self.conn.cursor() as cursor:
                query = """
                    UPDATE shipping_methods
                    SET name = %s, description = %s, country = %s, region = %s,
                        cost = %s, estimated_delivery_time = %s, is_active = %s, updated_at = NOW()
                    WHERE id = %s AND shop_name = %s
                """
                values = (
                    data["name"],
                    data.get("description"),
                    data.get("country"),
                    data.get("region"),
                    data["cost"],
                    data.get("estimated_delivery_time"),
                    data.get("is_active", True),
                    method_id,
                    data["shop_name"]
                )
                cursor.execute(query, values)
                self.conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating shipping method: {e}")
            self.conn.rollback()
            return False

    def delete_shipping_method(self, shipping_id):
        try:
            with self.conn.cursor() as cursor:
                query = "DELETE FROM shipping_methods WHERE id = %s"
                cursor.execute(query, (shipping_id,))
                self.conn.commit()
                return cursor.rowcount > 0  # Ritorna True se è stata eliminata almeno una riga
        except Exception as e:
            print(f"Error deleting shipping method: {e}")
            self.conn.rollback()
            return False

    def get_shipping_method_by_id(self, shipping_id, shop_name):
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT id, shop_name, name, description, country, region, cost, 
                        estimated_delivery_time, is_active, created_at, updated_at
                    FROM shipping_methods
                    WHERE id = %s AND shop_name = %s
                """
                cursor.execute(query, (shipping_id, shop_name))
                return cursor.fetchone()  # Ritorna un dizionario con i dettagli del metodo di spedizione
        except Exception as e:
            print(f"Error retrieving shipping method: {e}")
            return None

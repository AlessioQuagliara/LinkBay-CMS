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
        shop = cursor.fetchone()  # Usa fetchone per ottenere un singolo negozio
        cursor.close()
        return shop
    
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
        cursor.execute("SELECT * FROM pages WHERE slug = %s AND shop_name = %s", (slug, shop_name))
        page = cursor.fetchone()
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

    # Aggiorna il contenuto della pagina per un negozio specifico
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




    
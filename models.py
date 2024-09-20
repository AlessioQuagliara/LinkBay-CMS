from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

# CLASSE PER GESTIONE DATABASE

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

# CLASSE PER GESTIONE UTENTI

class User:
    def __init__(self, db_conn):
        self.conn = db_conn

    def get_all_users(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user")
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

    def create_user(self, name, surname, email, password):
        cursor = self.conn.cursor()
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO user (name, surname, email, password) VALUES (%s, %s, %s, %s)",
                       (name, surname, email, hashed_password))
        self.conn.commit()
        cursor.close()

    def update_user(self, user_id, name, surname, email):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE user SET name = %s, surname = %s, email = %s WHERE id = %s",
                       (name, surname, email, user_id))
        self.conn.commit()
        cursor.close()

    def delete_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
        self.conn.commit()
        cursor.close()

# Classe per ShopList
class ShopList:
    def __init__(self, db_conn):
        self.conn = db_conn

    def get_all_shops(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ShopList")
        shops = cursor.fetchall()
        cursor.close()
        return shops

    def get_shop_by_id(self, shop_id):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ShopList WHERE id = %s", (shop_id,))
        shop = cursor.fetchone()
        cursor.close()
        return shop

    def create_shop(self, shop_name, user_id, themeOptions):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO ShopList (shop_name, user_id, themeOptions) VALUES (%s, %s, %s)",
            (shop_name, user_id, themeOptions)
        )
        self.conn.commit()
        cursor.close()

    def update_shop(self, shop_id, shop_name, themeOptions):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE ShopList SET shop_name = %s, themeOptions = %s WHERE id = %s",
            (shop_name, themeOptions, shop_id)
        )
        self.conn.commit()
        cursor.close()

    def delete_shop(self, shop_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM ShopList WHERE id = %s", (shop_id,))
        self.conn.commit()
        cursor.close()

# Classe per Pages

class Page:
    def __init__(self, db_conn):
        self.conn = db_conn

    # Ottieni tutte le pagine
    def get_all_pages(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pages")
        pages = cursor.fetchall()
        cursor.close()
        return pages

    # Ottieni una pagina per slug
    def get_page_by_slug(self, slug):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pages WHERE slug = %s", (slug,))
        page = cursor.fetchone()
        cursor.close()
        return page

    # Crea una nuova pagina
    def create_page(self, title, description, keywords, slug, content, theme_name, paid, language, published):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO pages 
                (title, description, keywords, slug, content, theme_name, paid, language, published, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())""",
                (title, description, keywords, slug, content, theme_name, paid, language, published)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating page: {e}")
            cursor.close()
            return False

    # Aggiorna il contenuto della pagina
    def update_page_content(self, page_id, content):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """UPDATE pages 
                SET content = %s, updated_at = NOW() 
                WHERE id = %s""",
                (content, page_id)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating page content: {e}")
            cursor.close()
            return False

    # Aggiorna i metadati SEO di una pagina
    def update_page_seo(self, page_id, title, description, keywords, slug):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """UPDATE pages 
                SET title = %s, description = %s, keywords = %s, slug = %s, updated_at = NOW() 
                WHERE id = %s""",
                (title, description, keywords, slug, page_id)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating page SEO: {e}")
            cursor.close()
            return False

    # Elimina una pagina
    def delete_page(self, page_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM pages WHERE id = %s", (page_id,))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error deleting page: {e}")
            cursor.close()
            return False
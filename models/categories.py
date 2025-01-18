# CATEGORIE ---------------------------------------------------------------------------------------------------
import logging
logging.basicConfig(level=logging.INFO)

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
                logging.info(f"Error fetching categories: {e}")
                return []

    def get_category_by_id(self, category_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = "SELECT * FROM categories WHERE id = %s"
                cursor.execute(query, (category_id,))
                return cursor.fetchone()
            except Exception as e:
                logging.info(f"Error fetching category by ID: {e}")
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
                logging.info(f"Error creating category: {e}")
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
                logging.info(f"Error updating category: {e}")
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
                logging.info(f"Error deleting category: {e}")
                self.conn.rollback()
                return False

    def get_subcategories(self, parent_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                query = "SELECT * FROM categories WHERE parent_id = %s"
                cursor.execute(query, (parent_id,))
                return cursor.fetchall()
            except Exception as e:
                logging.info(f"Error fetching subcategories: {e}")
                return []
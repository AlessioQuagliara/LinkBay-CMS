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
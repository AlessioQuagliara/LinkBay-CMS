# Classe per PRODOTTI --------------------------------------------------------------------------------------------
import logging
logging.basicConfig(level=logging.INFO)

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
                logging.info(f"Error fetching products for shop: {e}")
                return []

    # Metodo per ottenere un prodotto per slug
    def get_product_by_slug(self, slug, shop_name):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM products WHERE slug = %s AND shop_name = %s", (slug, shop_name))
                return cursor.fetchone()
            except Exception as e:
                logging.info(f"Error fetching product by slug: {e}")
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
                logging.info(f"Error creating product: {e}")
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
                logging.info(f"Database Error: {e}")
                self.conn.rollback()
                return False

    def get_product_by_id(self, product_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
                return cursor.fetchone()
            except Exception as e:
                logging.info(f"Error fetching product: {e}")
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
                logging.info(f"Error creating product: {e}")
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
                logging.info(f"Error deleting product: {e}")
                self.conn.rollback()
                return False

    # Metodo per ottenere i prodotti per categoria
    def get_products_by_category(self, category_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM products WHERE category_id = %s", (category_id,))
                return cursor.fetchall()
            except Exception as e:
                logging.info(f"Error fetching products by category: {e}")
                return []

    # Metodo per ottenere i prodotti per brand
    def get_products_by_brand(self, brand_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM products WHERE brand_id = %s", (brand_id,))
                return cursor.fetchall()
            except Exception as e:
                logging.info(f"Error fetching products by brand: {e}")
                return []

    # Metodo per ottenere le categorie
    def get_all_categories(self, shop_name):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM categories WHERE shop_name = %s", (shop_name,))
                return cursor.fetchall()
            except Exception as e:
                logging.info(f"Error fetching categories: {e}")
                return []

    # Metodo per ottenere gli attributi di un prodotto
    def get_product_attributes(self, product_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM product_attributes WHERE product_id = %s", (product_id,))
                return cursor.fetchall()
            except Exception as e:
                logging.info(f"Error fetching product attributes: {e}")
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
                logging.info(f"Error adding product attribute: {e}")
                self.conn.rollback()
                return False

    # Metodo per ottenere le immagini di un prodotto
    def get_product_images(self, product_id):
        with self.conn.cursor(dictionary=True) as cursor:
            try:
                cursor.execute("SELECT * FROM product_images WHERE product_id = %s", (product_id,))
                return cursor.fetchall()
            except Exception as e:
                logging.info(f"Error fetching product images: {e}")
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
                logging.info(f"Error adding product image: {e}")
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
                logging.info(f"SQL Result: {products}")  # Debug
                return products
            except Exception as e:
                logging.info(f"Error in search_products: {e}")
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
                logging.info(f"Error fetching products: {e}")
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
                logging.info(f"Error retrieving product images: {e}")
                return []
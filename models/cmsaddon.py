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
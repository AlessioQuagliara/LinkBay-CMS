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
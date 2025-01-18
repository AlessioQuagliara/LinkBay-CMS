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
           logging.info(f"Error updating internal cookie policy: {e}")
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
           logging.info(f"Error creating internal cookie policy: {e}")
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
           logging.info(f"Error updating third-party cookie policy: {e}")
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
           logging.info(f"Error creating third-party cookie policy: {e}")
            self.conn.rollback()
            return False
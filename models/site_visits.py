import logging
import datetime

logging.basicConfig(level=logging.INFO)

class SiteVisits:
    def __init__(self, db_conn):
        self.conn = db_conn

    # 🔹 REGISTRA UNA NUOVA VISITA
    def log_visit(self, shop_name, ip_address, user_agent, referrer, page_url):
        """
        Registra una nuova visita nel database.
        """
        try:
            visit_time = datetime.datetime.now()
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO site_visits (shop_name, ip_address, user_agent, referrer, page_url, visit_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (shop_name, ip_address, user_agent, referrer, page_url, visit_time))
            self.conn.commit()
        except Exception as e:
            logging.error(f"Errore durante la registrazione della visita: {e}")

    # 🔹 OTTIENI VISITATORI ATTIVI
    def get_active_visitors(self, shop_name, minutes=10):
        """
        Conta i visitatori attivi negli ultimi 'minutes' minuti.
        """
        try:
            time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT COUNT(DISTINCT ip_address) AS active_visitors
                    FROM site_visits
                    WHERE shop_name = %s AND visit_time >= %s
                """, (shop_name, time_threshold))
                result = cursor.fetchone() or {"active_visitors": 0}
            return result["active_visitors"]
        except Exception as e:
            logging.error(f"Errore durante il conteggio dei visitatori attivi: {e}")
            return 0

    # 🔹 OTTIENI VISITE GIORNALIERE
    def get_daily_visitors(self, shop_name):
        """
        Conta i visitatori unici per la giornata corrente.
        """
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT COUNT(DISTINCT ip_address) AS daily_visitors
                    FROM site_visits
                    WHERE shop_name = %s AND DATE(visit_time) = CURDATE()
                """, (shop_name,))
                result = cursor.fetchone() or {"daily_visitors": 0}
            return result["daily_visitors"]
        except Exception as e:
            logging.error(f"Errore durante il conteggio dei visitatori giornalieri: {e}")
            return 0

    # 🔹 OTTIENI LE PAGINE PIÙ VISITATE
    def get_most_visited_pages(self, shop_name, limit=5):
        """
        Recupera le pagine più visitate per un negozio, ordinate per numero di visite.
        """
        try:
            with self.conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT page_url, COUNT(*) AS visit_count
                    FROM site_visits
                    WHERE shop_name = %s
                    GROUP BY page_url
                    ORDER BY visit_count DESC
                    LIMIT %s
                """, (shop_name, limit))
                pages = cursor.fetchall()
            return pages
        except Exception as e:
            logging.error(f"Errore durante il recupero delle pagine più visitate: {e}")
            return []

    # 🔹 ELIMINA LE VISITE PIÙ VECCHIE DI N GIORNI
    def clean_old_visits(self, days=30):
        """
        Rimuove le visite più vecchie di 'days' giorni per mantenere pulito il database.
        """
        try:
            time_threshold = datetime.datetime.now() - datetime.timedelta(days=days)
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM site_visits WHERE visit_time < %s", (time_threshold,))
            self.conn.commit()
            logging.info(f"Visite più vecchie di {days} giorni eliminate con successo.")
        except Exception as e:
            logging.error(f"Errore durante la pulizia delle vecchie visite: {e}")

    # 🔹 ELIMINA TUTTE LE VISITE DI UNO SHOP
    def delete_visits_by_shop(self, shop_name):
        """
        Elimina tutte le visite registrate per uno specifico shop.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM site_visits WHERE shop_name = %s", (shop_name,))
            self.conn.commit()
            logging.info(f"Tutte le visite per il negozio '{shop_name}' sono state eliminate.")
        except Exception as e:
            logging.error(f"Errore durante l'eliminazione delle visite per '{shop_name}': {e}")

    def get_recent_visits(self, shop_name, limit=100):
            """
            Recupera le visite più recenti per un determinato shop, ordinate per data di visita.

            :param shop_name: Nome del negozio (subdomain)
            :param limit: Numero massimo di visite da recuperare (default: 100)
            :return: Lista di visite [{ip_address, referrer, page_url, visit_time}]
            """
            try:
                with self.conn.cursor(dictionary=True) as cursor:
                    cursor.execute("""
                        SELECT ip_address, user_agent, referrer, page_url, visit_time
                        FROM site_visits
                        WHERE shop_name = %s
                        ORDER BY visit_time DESC
                        LIMIT %s
                    """, (shop_name, limit))
                    visits = cursor.fetchall()
                return visits

            except Exception as e:
                logging.error(f"Errore durante il recupero delle visite recenti per '{shop_name}': {e}")
                return []
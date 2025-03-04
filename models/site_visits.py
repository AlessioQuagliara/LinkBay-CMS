from models.database import db
from datetime import datetime, timedelta
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

# 🔹 **Modello per le Visite del Sito**
class SiteVisit(db.Model):
    __tablename__ = "site_visits"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), nullable=False)  # 🏪 Nome del negozio
    ip_address = db.Column(db.String(50), nullable=False)  # 🌍 Indirizzo IP del visitatore
    user_agent = db.Column(db.String(500), nullable=True)  # 🖥️ User-Agent del browser
    referrer = db.Column(db.String(500), nullable=True)  # 🔗 Pagina di provenienza
    page_url = db.Column(db.String(500), nullable=False)  # 📄 URL visitato
    visit_time = db.Column(db.DateTime, default=datetime.utcnow)  # ⏱️ Data della visita

    def __repr__(self):
        return f"<SiteVisit {self.id} - {self.ip_address} - {self.page_url} - {self.visit_time}>"

# ✅ **Registra una nuova visita**
def log_visit(shop_name, ip_address, user_agent, referrer, page_url):
    try:
        visit = SiteVisit(
            shop_name=shop_name,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            page_url=page_url,
            visit_time=datetime.utcnow(),
        )
        db.session.add(visit)
        db.session.commit()
        logging.info(f"✅ Visita registrata: {ip_address} - {page_url}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella registrazione della visita: {e}")
        return False

# 🔍 **Recupera i visitatori attivi negli ultimi X minuti**
def get_active_visitors(shop_name, minutes=10):
    try:
        time_threshold = datetime.utcnow() - timedelta(minutes=minutes)
        active_visitors = (
            db.session.query(db.func.count(SiteVisit.ip_address.distinct()))
            .filter(SiteVisit.shop_name == shop_name, SiteVisit.visit_time >= time_threshold)
            .scalar()
        )
        return active_visitors or 0
    except Exception as e:
        logging.error(f"❌ Errore nel conteggio dei visitatori attivi: {e}")
        return 0

# 🔍 **Recupera i visitatori giornalieri**
def get_daily_visitors(shop_name):
    try:
        daily_visitors = (
            db.session.query(db.func.count(SiteVisit.ip_address.distinct()))
            .filter(SiteVisit.shop_name == shop_name, db.func.date(SiteVisit.visit_time) == db.func.current_date())
            .scalar()
        )
        return daily_visitors or 0
    except Exception as e:
        logging.error(f"❌ Errore nel conteggio dei visitatori giornalieri: {e}")
        return 0

# 🔍 **Recupera le pagine più visitate**
def get_most_visited_pages(shop_name, limit=5):
    try:
        pages = (
            db.session.query(SiteVisit.page_url, db.func.count().label("visit_count"))
            .filter(SiteVisit.shop_name == shop_name)
            .group_by(SiteVisit.page_url)
            .order_by(db.func.count().desc())
            .limit(limit)
            .all()
        )
        return [{"page_url": page[0], "visit_count": page[1]} for page in pages]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero delle pagine più visitate: {e}")
        return []

# ❌ **Elimina le visite più vecchie di X giorni**
def clean_old_visits(days=30):
    try:
        time_threshold = datetime.utcnow() - timedelta(days=days)
        deleted_count = SiteVisit.query.filter(SiteVisit.visit_time < time_threshold).delete()
        db.session.commit()
        logging.info(f"🗑️ Eliminati {deleted_count} record di visite più vecchie di {days} giorni.")
        return deleted_count
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella pulizia delle visite: {e}")
        return 0

# ❌ **Elimina tutte le visite di uno shop**
def delete_visits_by_shop(shop_name):
    try:
        deleted_count = SiteVisit.query.filter(SiteVisit.shop_name == shop_name).delete()
        db.session.commit()
        logging.info(f"🗑️ Eliminati {deleted_count} record per lo shop '{shop_name}'.")
        return deleted_count
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione delle visite per '{shop_name}': {e}")
        return 0

# 🔍 **Recupera le visite recenti**
def get_recent_visits(shop_name, limit=100):
    try:
        visits = (
            SiteVisit.query.filter(SiteVisit.shop_name == shop_name)
            .order_by(SiteVisit.visit_time.desc())
            .limit(limit)
            .all()
        )
        return [visit_to_dict(visit) for visit in visits]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero delle visite recenti per '{shop_name}': {e}")
        return []

# 📌 **Helper per convertire una visita in dizionario**
def visit_to_dict(visit):
    return {col.name: getattr(visit, col.name) for col in SiteVisit.__table__.columns} if visit else None
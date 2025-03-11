from models.database import db
from datetime import datetime, timedelta
import logging
from functools import wraps

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    
# DIZIONARIO ---------------------------------------------------- 
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# 🔄 **Decoratore per la gestione degli errori del database**
def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            db.session.rollback()
            logging.error(f"❌ Errore in {func.__name__}: {e}")
            return None
    return wrapper


# ✅ **Registra una nuova visita**
@handle_db_errors
def log_visit(shop_name, ip_address, user_agent, referrer, page_url):
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


# 🔍 **Recupera i visitatori attivi negli ultimi X minuti**
@handle_db_errors
def get_active_visitors(shop_name, minutes=10):
    time_threshold = datetime.utcnow() - timedelta(minutes=minutes)
    active_visitors = (
        db.session.query(db.func.count(SiteVisit.ip_address.distinct()))
        .filter(SiteVisit.shop_name == shop_name, SiteVisit.visit_time >= time_threshold)
        .scalar()
    )
    return active_visitors or 0


# 🔍 **Recupera i visitatori giornalieri**
@handle_db_errors
def get_daily_visitors(shop_name):
    daily_visitors = (
        db.session.query(db.func.count(SiteVisit.ip_address.distinct()))
        .filter(SiteVisit.shop_name == shop_name, db.func.date(SiteVisit.visit_time) == db.func.current_date())
        .scalar()
    )
    return daily_visitors or 0


# 🔍 **Recupera le pagine più visitate**
@handle_db_errors
def get_most_visited_pages(shop_name, limit=5):
    pages = (
        db.session.query(SiteVisit.page_url, db.func.count().label("visit_count"))
        .filter(SiteVisit.shop_name == shop_name)
        .group_by(SiteVisit.page_url)
        .order_by(db.func.count().desc())
        .limit(limit)
        .all()
    )
    return [{"page_url": page[0], "visit_count": page[1]} for page in pages]


# ❌ **Elimina le visite più vecchie di X giorni**
@handle_db_errors
def clean_old_visits(days=30):
    time_threshold = datetime.utcnow() - timedelta(days=days)
    deleted_count = SiteVisit.query.filter(SiteVisit.visit_time < time_threshold).delete()
    db.session.commit()
    logging.info(f"🗑️ Eliminati {deleted_count} record di visite più vecchie di {days} giorni.")
    return deleted_count


# ❌ **Elimina tutte le visite di uno shop**
@handle_db_errors
def delete_visits_by_shop(shop_name):
    deleted_count = SiteVisit.query.filter(SiteVisit.shop_name == shop_name).delete()
    db.session.commit()
    logging.info(f"🗑️ Eliminati {deleted_count} record per lo shop '{shop_name}'.")
    return deleted_count


# 🔍 **Recupera le visite recenti**
@handle_db_errors
def get_recent_visits(shop_name, limit=100):
    visits = (
        SiteVisit.query.filter(SiteVisit.shop_name == shop_name)
        .order_by(SiteVisit.visit_time.desc())
        .limit(limit)
        .all()
    )
    return [visit_to_dict(visit) for visit in visits]


# 📌 **Helper per convertire una visita in dizionario**
def visit_to_dict(visit):
    return {col.name: getattr(visit, col.name) for col in SiteVisit.__table__.columns} if visit else None
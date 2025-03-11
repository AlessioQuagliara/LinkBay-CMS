from models.database import db
import logging
from datetime import datetime, timedelta
from functools import wraps

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per le Visite Interne**
class SiteVisitIntern(db.Model):
    __tablename__ = "site_visit_intern"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    ip_address = db.Column(db.String(45), nullable=False)  # 🌍 Indirizzo IP del visitatore
    user_agent = db.Column(db.Text, nullable=False)  # 🖥️ User-Agent del browser
    referrer = db.Column(db.Text, nullable=True)  # 🔗 Pagina di provenienza
    page_url = db.Column(db.Text, nullable=False)  # 📄 URL visitato
    visit_time = db.Column(db.DateTime, default=datetime.utcnow)  # ⏱️ Data della visita

    def __repr__(self):
        return f"<SiteVisitIntern {self.id} - {self.ip_address} - {self.page_url} - {self.visit_time}>"
    
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


# ✅ **Registra una nuova visita interna**
@handle_db_errors
def log_internal_visit(ip_address, user_agent, referrer, page_url):
    visit = SiteVisitIntern(
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


# 🔍 **Recupera le visite più recenti**
@handle_db_errors
def get_recent_internal_visits(limit=50):
    visits = SiteVisitIntern.query.order_by(SiteVisitIntern.visit_time.desc()).limit(limit).all()
    return [visit_to_dict(visit) for visit in visits]


# ❌ **Elimina le visite più vecchie di N giorni**
@handle_db_errors
def clean_old_internal_visits(days=30):
    time_threshold = datetime.utcnow() - timedelta(days=days)
    deleted_count = SiteVisitIntern.query.filter(SiteVisitIntern.visit_time < time_threshold).delete()
    db.session.commit()
    logging.info(f"🗑️ Eliminati {deleted_count} record di visite più vecchie di {days} giorni.")
    return deleted_count


# 📌 **Helper per convertire una visita in dizionario**
def visit_to_dict(visit):
    return {col.name: getattr(visit, col.name) for col in SiteVisitIntern.__table__.columns} if visit else None
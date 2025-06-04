from models.database import db
import logging
from functools import wraps
from datetime import datetime, timedelta
import uuid

# --------------------------------------------------
# Logging (stesso formato usato negli altri modelli)
# --------------------------------------------------
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --------------------------------------------------
# Decoratore per intercettare e loggare errori DB
# --------------------------------------------------
def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            db.session.rollback()
            logging.error(f"❌ Errore in {func.__name__}: {exc}")
            return None
    return wrapper


# --------------------------------------------------
# Helper generico per serializzare un modello
# --------------------------------------------------
def model_to_dict(model):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}


# 🔹 **Modello uRequests / Invitation**
class uRequests(db.Model):
    """
    Gestisce inviti e richieste tra utenti in relazione a uno Shop.

    Tipi possibili (request_type):
      • collaboration → accesso come viewer / editor / admin
      • transfer      → vendita/trasferimento proprietà (campo price)
      • quote         → preventivo allegato a un PDF (campo attachment_path)

    Stato (status):
      • pending   • accepted   • rejected   • expired
    """
    __tablename__ = "requests"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(64), nullable=False, unique=True, index=True)

    request_type = db.Column(
        db.Enum('collaboration', 'transfer', 'quote', name='requesttype'),
        nullable=False
    )
    status = db.Column(
        db.Enum('pending', 'accepted', 'rejected', 'expired', name='requeststatus'),
        nullable=False,
        default='pending'
    )

    # --- Attori ---
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    recipient_email = db.Column(db.String(255), nullable=False)

    # --- Contesto negozio ---
    shop_id = db.Column(db.Integer, db.ForeignKey("ShopList.id"), nullable=False)

    # collaboration
    access_level = db.Column(db.String(20), nullable=True)  # viewer/editor/admin
    # transfer
    price = db.Column(db.Numeric(10, 2), nullable=True)
    # quote
    attachment_path = db.Column(db.String(255), nullable=True)

    # --- Metadati ---
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime,
                           nullable=False,
                           default=lambda: datetime.utcnow() + timedelta(days=3))

    # Evita doppioni di richieste pendenti identiche
    __table_args__ = (
        db.UniqueConstraint('recipient_email', 'shop_id', 'request_type', 'status',
                            name='uq_request_once_pending',
                            deferrable=True, initially='DEFERRED'),
    )

    # --------------------------------------------------
    # Utility
    # --------------------------------------------------
    @staticmethod
    def gen_token() -> str:
        """Genera un token url-safe."""
        return uuid.uuid4().hex

    def mark_expired(self):
        self.status = 'expired'

    def __repr__(self):
        return f"<uRequests {self.id} {self.request_type} -> {self.recipient_email} ({self.status})>"


# --------------------------------------------------
# CRUD helpers
# --------------------------------------------------
@handle_db_errors
def create_request(data):
    """
    Crea un record di richiesta e lo salva.
    data = {
        'sender_id': ..,
        'recipient_id': .. (può essere None),
        'recipient_email': ..,
        'shop_id': ..,
        'request_type': 'collaboration'|'transfer'|'quote',
        'access_level': ..,
        'price': ..,
        'attachment_path': ..,
        'message': ..,
        'expires_in_days': 3,  # opzionale
    }
    """
    expires = datetime.utcnow() + timedelta(days=data.get('expires_in_days', 3))
    new_req = uRequests(
        token=uRequests.gen_token(),
        request_type=data['request_type'],
        sender_id=data['sender_id'],
        recipient_id=data.get('recipient_id'),
        recipient_email=data['recipient_email'],
        shop_id=data['shop_id'],
        access_level=data.get('access_level'),
        price=data.get('price'),
        attachment_path=data.get('attachment_path'),
        message=data.get('message'),
        expires_at=expires
    )
    db.session.add(new_req)
    db.session.commit()
    logging.info(f"✅ uRequests {new_req.id} creata")
    return new_req.id


@handle_db_errors
def get_request_by_token(token):
    req = uRequests.query.filter_by(token=token).first()
    return model_to_dict(req) if req else None


@handle_db_errors
def respond_request(token, decision, user_id=None):
    """
    Accetta o rifiuta una richiesta.
    decision = 'accepted' | 'rejected'
    """
    req = uRequests.query.filter_by(token=token, status='pending').first()
    if not req:
        return False
    if datetime.utcnow() > req.expires_at:
        req.status = 'expired'
        db.session.commit()
        return False

    req.status = decision
    if user_id:
        req.recipient_id = user_id  # nel caso fosse None e l'utente si registra ora
    db.session.commit()
    logging.info(f"✅ uRequests {req.id} -> {decision}")
    return True


@handle_db_errors
def expire_old_requests():
    """Marca come expired tutte le richieste oltre expires_at."""
    now = datetime.utcnow()
    num = (uRequests.query
           .filter(uRequests.status == 'pending', uRequests.expires_at < now)
           .update({"status": "expired"}, synchronize_session=False))
    db.session.commit()
    if num:
        logging.info(f"ℹ️  {num} request scadute")
    return num
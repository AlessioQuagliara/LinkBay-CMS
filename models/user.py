from models.database import db
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

# 🔹 **Definizione della tabella User**
class User(db.Model):
    """
    Modello ORM per gli utenti del CMS.
    """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco dell'utente
    email = db.Column(db.String(255), unique=True, nullable=False)  # 📧 Email univoca
    password = db.Column(db.String(255), nullable=False)  # 🔒 Password hashata
    nome = db.Column(db.String(100), nullable=False)  # 🏷️ Nome
    cognome = db.Column(db.String(100), nullable=False)  # 🏷️ Cognome
    telefono = db.Column(db.String(20), nullable=True)  # 📞 Numero di telefono
    profilo_foto = db.Column(db.String(255), nullable=True)  # 🖼️ URL della foto profilo
    is_2fa_enabled = db.Column(db.Boolean, default=False)  # 🔐 Autenticazione a due fattori (2FA)
    otp_secret = db.Column(db.String(255), nullable=True)  # 🔑 Segreto OTP per 2FA

    # 🛠️ **Hash della password**
    def set_password(self, password):
        """
        Imposta la password dell'utente con un hash sicuro.
        """
        self.password = generate_password_hash(password)

    # ✅ **Verifica la password**
    def check_password(self, password):
        """
        Verifica se la password inserita è corretta.
        """
        return check_password_hash(self.password, password)


# ✅ **Recupera tutti gli utenti**
def get_all_users():
    """
    Recupera tutti gli utenti dal database.
    """
    try:
        return db.session.query(User).all()
    except Exception as e:
        logging.error(f"❌ Errore nel recupero di tutti gli utenti: {e}")
        return []


# 🔍 **Recupera un utente per ID**
def get_user_by_id(user_id):
    """
    Recupera un utente dal database tramite ID.
    """
    try:
        return db.session.get(User, user_id)  # ⚡ Ottimizzato per velocità
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dell'utente con ID {user_id}: {e}")
        return None


# 🔎 **Recupera un utente per Email**
def get_user_by_email(email):
    """
    Recupera un utente dal database tramite email.
    """
    try:
        return db.session.query(User).filter_by(email=email).first()
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dell'utente con email {email}: {e}")
        return None


# 🆕 **Crea un nuovo utente**
def create_user(email, password, nome, cognome, telefono=None, profilo_foto=None):
    """
    Crea un nuovo utente nel database.
    """
    try:
        hashed_password = generate_password_hash(password)  # 🔐 Hash della password
        new_user = User(
            email=email,
            password=hashed_password,
            nome=nome,
            cognome=cognome,
            telefono=telefono,
            profilo_foto=profilo_foto,
            is_2fa_enabled=False,
            otp_secret=None
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione dell'utente {email}: {e}")
        return None


# ✏️ **Aggiorna i dati di un utente**
def update_user(user_id, **kwargs):
    """
    Aggiorna i dati di un utente esistente nel database.
    """
    try:
        user = get_user_by_id(user_id)
        if not user:
            return False
        for key, value in kwargs.items():
            setattr(user, key, value)  # 🛠️ Aggiorna dinamicamente i campi
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento dell'utente {user_id}: {e}")
        return False


# 🗑️ **Elimina un utente**
def delete_user(user_id):
    """
    Elimina un utente dal database.
    """
    try:
        user = get_user_by_id(user_id)
        if not user:
            return False
        db.session.delete(user)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione dell'utente {user_id}: {e}")
        return False
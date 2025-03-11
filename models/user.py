from models.database import db
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from functools import wraps

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Definizione della tabella User**
class User(db.Model):
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
        self.password = generate_password_hash(password)

    # ✅ **Verifica la password**
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
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


# ✅ **Recupera tutti gli utenti**
@handle_db_errors
def get_all_users():
    return db.session.query(User).all()


# 🔍 **Recupera un utente per ID**
@handle_db_errors
def get_user_by_id(user_id):
    return db.session.get(User, user_id)  # ⚡ Ottimizzato per velocità


# 🔎 **Recupera un utente per Email**
@handle_db_errors
def get_user_by_email(email):
    return db.session.query(User).filter_by(email=email).first()


# 🆕 **Crea un nuovo utente**
@handle_db_errors
def create_user(email, password, nome, cognome, telefono=None, profilo_foto=None):
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


# ✏️ **Aggiorna i dati di un utente**
@handle_db_errors
def update_user(user_id, **kwargs):
    user = get_user_by_id(user_id)
    if not user:
        return False

    for key, value in kwargs.items():
        setattr(user, key, value)  # 🛠️ Aggiorna dinamicamente i campi

    db.session.commit()
    return True


# 🗑️ **Elimina un utente**
@handle_db_errors
def delete_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return False

    db.session.delete(user)
    db.session.commit()
    return True
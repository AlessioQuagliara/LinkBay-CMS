from models.database import db
import logging
from datetime import datetime

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

# 🔹 **Modello per la Cookie Policy**
class CookiePolicy(db.Model):
    __tablename__ = "cookie_policy"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), unique=True, nullable=False)  # 🏪 Nome del negozio
    title = db.Column(db.String(255), nullable=False)  # 🏷️ Titolo del banner
    text_content = db.Column(db.String(1024), nullable=False)  # 📝 Testo del banner
    button_text = db.Column(db.String(255), nullable=False)  # 🔘 Testo del pulsante
    background_color = db.Column(db.String(50), nullable=False)  # 🎨 Colore di sfondo
    button_color = db.Column(db.String(50), nullable=False)  # 🎨 Colore pulsante
    button_text_color = db.Column(db.String(50), nullable=False)  # 🎨 Colore testo pulsante
    text_color = db.Column(db.String(50), nullable=False)  # 🎨 Colore del testo
    entry_animation = db.Column(db.String(100), nullable=False)  # 🎬 Animazione d'entrata
    use_third_party = db.Column(db.Boolean, default=False)  # 🔄 Uso di servizi di terze parti
    third_party_cookie = db.Column(db.String(255), nullable=True)  # 🍪 Cookie di terze parti
    third_party_privacy = db.Column(db.String(255), nullable=True)  # 🔒 Privacy policy di terzi
    third_party_terms = db.Column(db.String(255), nullable=True)  # 📜 Termini di terzi
    third_party_consent = db.Column(db.String(255), nullable=True)  # ✅ Consenso ai cookie di terze parti
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Data di aggiornamento

    def __repr__(self):
        return f"<CookiePolicy {self.shop_name}>"

# 🔍 **Recupera le impostazioni della cookie policy per un negozio**
def get_policy_by_shop(shop_name):
    try:
        policy = CookiePolicy.query.filter_by(shop_name=shop_name).first()
        return policy_to_dict(policy) if policy else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero della Cookie Policy per {shop_name}: {e}")
        return None

# ✅ **Aggiorna la cookie policy interna**
def update_internal_policy(shop_name, title, text_content, button_text, background_color, 
                           button_color, button_text_color, text_color, entry_animation):
    try:
        policy = CookiePolicy.query.filter_by(shop_name=shop_name).first()
        if not policy:
            return False

        # Aggiorna i dati della policy
        policy.title = title
        policy.text_content = text_content
        policy.button_text = button_text
        policy.background_color = background_color
        policy.button_color = button_color
        policy.button_text_color = button_text_color
        policy.text_color = text_color
        policy.entry_animation = entry_animation
        policy.use_third_party = False

        db.session.commit()
        logging.info(f"✅ Cookie Policy interna aggiornata per {shop_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento della Cookie Policy: {e}")
        return False

# ✏️ **Crea una nuova impostazione interna del banner dei cookie**
def create_internal_policy(shop_name, title, text_content, button_text, background_color, 
                           button_color, button_text_color, text_color, entry_animation):
    try:
        new_policy = CookiePolicy(
            shop_name=shop_name,
            title=title,
            text_content=text_content,
            button_text=button_text,
            background_color=background_color,
            button_color=button_color,
            button_text_color=button_text_color,
            text_color=text_color,
            entry_animation=entry_animation,
            use_third_party=False,
        )
        db.session.add(new_policy)
        db.session.commit()
        logging.info(f"✅ Cookie Policy interna creata per {shop_name}")
        return new_policy.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione della Cookie Policy: {e}")
        return None

# 🔄 **Aggiorna le impostazioni per l'uso di terze parti**
def update_third_party_policy(shop_name, use_third_party, third_party_cookie, third_party_privacy, 
                              third_party_terms, third_party_consent):
    try:
        policy = CookiePolicy.query.filter_by(shop_name=shop_name).first()
        if not policy:
            return False

        policy.use_third_party = use_third_party
        policy.third_party_cookie = third_party_cookie
        policy.third_party_privacy = third_party_privacy
        policy.third_party_terms = third_party_terms
        policy.third_party_consent = third_party_consent

        db.session.commit()
        logging.info(f"✅ Cookie Policy di terze parti aggiornata per {shop_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento della Cookie Policy di terze parti: {e}")
        return False

# ✅ **Crea una nuova impostazione per il banner dei cookie di terze parti**
def create_third_party_policy(shop_name, use_third_party, third_party_cookie, third_party_privacy, 
                              third_party_terms, third_party_consent):
    try:
        new_policy = CookiePolicy(
            shop_name=shop_name,
            use_third_party=use_third_party,
            third_party_cookie=third_party_cookie,
            third_party_privacy=third_party_privacy,
            third_party_terms=third_party_terms,
            third_party_consent=third_party_consent,
        )
        db.session.add(new_policy)
        db.session.commit()
        logging.info(f"✅ Cookie Policy di terze parti creata per {shop_name}")
        return new_policy.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione della Cookie Policy di terze parti: {e}")
        return None

# 🔍 **Recupera i dati della cookie policy per un negozio**
def get_cookie_policy(shop_name):
    try:
        policy = CookiePolicy.query.filter_by(shop_name=shop_name).first()
        return policy_to_dict(policy) if policy else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero della Cookie Policy: {e}")
        return None

# 📌 **Helper per convertire una CookiePolicy in dizionario**
def policy_to_dict(policy):
    return {
        "id": policy.id,
        "shop_name": policy.shop_name,
        "title": policy.title,
        "text_content": policy.text_content,
        "button_text": policy.button_text,
        "background_color": policy.background_color,
        "button_color": policy.button_color,
        "button_text_color": policy.button_text_color,
        "text_color": policy.text_color,
        "entry_animation": policy.entry_animation,
        "use_third_party": policy.use_third_party,
        "third_party_cookie": policy.third_party_cookie,
        "third_party_privacy": policy.third_party_privacy,
        "third_party_terms": policy.third_party_terms,
        "third_party_consent": policy.third_party_consent,
        "created_at": policy.created_at,
        "updated_at": policy.updated_at,
    }
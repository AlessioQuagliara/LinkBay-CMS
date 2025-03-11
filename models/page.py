from models.database import db
import logging
from functools import wraps
from datetime import datetime
import os
import json

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per le Pagine**
class Page(db.Model):
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), nullable=False)  # 🏪 Nome del negozio
    title = db.Column(db.String(255), nullable=False)  # 🏷️ Titolo della pagina
    description = db.Column(db.Text, nullable=True)  # 📝 Descrizione SEO
    keywords = db.Column(db.String(255), nullable=True)  # 🔑 Parole chiave SEO
    slug = db.Column(db.String(255), unique=True, nullable=False)  # 🔗 Slug della pagina
    content = db.Column(db.Text, nullable=True)  # 🖋️ Contenuto della pagina
    theme_name = db.Column(db.String(255), nullable=True)  # 🎨 Nome del tema
    paid = db.Column(db.String(255), nullable=False, default="No")  # 💰 Stato pagato o no
    language = db.Column(db.String(10), nullable=True)  # 🌍 Lingua della pagina
    published = db.Column(db.Boolean, default=False)  # ✅ Pubblicata o no
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    def __repr__(self):
        return f"<Page {self.slug} - {self.shop_name}>"
    
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

# 🔄 **Helper per convertire un modello in dizionario**
def model_to_dict(model):
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}

# 🔍 **Recupera tutte le pagine di un negozio**
@handle_db_errors
def get_all_pages(shop_name):
    pages = Page.query.filter_by(shop_name=shop_name).all()
    return [model_to_dict(p) for p in pages]

# 🔍 **Recupera tutti i nomi e gli slug delle pagine di un negozio**
@handle_db_errors
def get_published_pages(shop_name):
    pages = (
        db.session.query(Page.title, Page.slug)
        .filter_by(shop_name=shop_name, published=True)
        .all()
    )
    return [{"title": page.title, "slug": page.slug} for page in pages]

# 🔍 **Recupera una pagina per slug e negozio**
@handle_db_errors
def get_page_by_slug(slug, shop_name):
    page = Page.query.filter_by(slug=slug, shop_name=shop_name).first()
    return model_to_dict(page) if page else None

# ✅ **Crea una nuova pagina**
@handle_db_errors
def create_page(data):
    new_page = Page(
        shop_name=data["shop_name"],
        title=data["title"],
        description=data["description"],
        keywords=data["keywords"],
        slug=data["slug"],
        content=data["content"],
        theme_name=data["theme_name"],
        paid=data["paid"],
        language=data["language"],
        published=data["published"],
    )
    db.session.add(new_page)
    db.session.commit()
    logging.info(f"✅ Pagina '{data['slug']}' creata con successo")
    return new_page.id

# 🔄 **Aggiorna il contenuto di una pagina**
@handle_db_errors
def update_page_content(page_id, content):
    page = Page.query.get(page_id)
    if not page:
        return False

    page.content = content
    page.updated_at = datetime.utcnow()
    db.session.commit()
    logging.info(f"✅ Contenuto della pagina {page_id} aggiornato")
    return True

# 🔄 **Aggiorna i metadati SEO della pagina**
@handle_db_errors
def update_page_seo(page_id, data):
    page = Page.query.get(page_id)
    if not page:
        return False

    page.title = data["title"]
    page.description = data["description"]
    page.keywords = data["keywords"]
    page.slug = data["slug"]
    page.updated_at = datetime.utcnow()
    db.session.commit()
    logging.info(f"✅ SEO aggiornato per la pagina {page_id}")
    return True

# ❌ **Elimina una pagina**
@handle_db_errors
def delete_page(page_id):
    page = Page.query.get(page_id)
    if not page:
        return False

    db.session.delete(page)
    db.session.commit()
    logging.info(f"✅ Pagina {page_id} eliminata con successo")
    return True

# 🔍 **Recupera una pagina tradotta**
@handle_db_errors
def get_page_by_slug_and_language(slug, language, shop_name):
    page = Page.query.filter_by(slug=slug, language=language, shop_name=shop_name).first()
    return model_to_dict(page) if page else None

# ✅ **Aggiorna o crea una pagina tradotta**
@handle_db_errors
def update_or_create_page_content(page_id, content, language, shop_name):
    page = Page.query.filter_by(id=page_id, language=language, shop_name=shop_name).first()

    if page:
        page.content = content
        page.updated_at = datetime.utcnow()
    else:
        new_page = Page(
            id=page_id,
            content=content,
            language=language,
            shop_name=shop_name,
        )
        db.session.add(new_page)

    db.session.commit()
    logging.info(f"✅ Pagina tradotta aggiornata/creata")
    return True

# 🔍 **Recupera le pagine pubblicate**
@handle_db_errors
def get_published_pages(shop_name):
    pages = Page.query.filter_by(shop_name=shop_name, published=True).all()
    return [model_to_dict(p) for p in pages if p.slug not in ["navbar", "footer"]]

# 🎨 **Applica un tema a un negozio**
@handle_db_errors
def apply_theme(theme_name, shop_name):
    theme_path = os.path.join("themes", f"{theme_name}.json")

    if not os.path.exists(theme_path):
        logging.error(f"❌ Theme file '{theme_path}' not found.")
        return False

    try:
        with open(theme_path, "r") as theme_file:
            theme_data = json.load(theme_file)

        for page in theme_data["pages"]:
            existing_page = Page.query.filter_by(slug=page["slug"], shop_name=shop_name).first()

            if existing_page:
                existing_page.content = page.get("content", "")
                existing_page.updated_at = datetime.utcnow()
            else:
                new_page = Page(
                    title=page.get("title", ""),
                    description=page.get("description", None),
                    keywords=page.get("keywords", None),
                    slug=page.get("slug", ""),
                    content=page.get("content", None),
                    theme_name=theme_name,
                    paid="Yes",
                    language=page.get("language", None),
                    published=bool(page.get("published", True)),
                    shop_name=shop_name,
                )
                db.session.add(new_page)

        db.session.commit()
        logging.info(f"✅ Tema '{theme_name}' applicato con successo a {shop_name}")
        return True
    except Exception as e:
        logging.error(f"❌ Errore nell'applicazione del tema '{theme_name}': {e}")
        return False
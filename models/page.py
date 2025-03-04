from models.database import db
from datetime import datetime
import logging, os, json

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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

# 🔍 **Recupera tutte le pagine di un negozio**
def get_all_pages(shop_name):
    try:
        pages = Page.query.filter_by(shop_name=shop_name).all()
        return [page_to_dict(p) for p in pages]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero delle pagine per {shop_name}: {e}")
        return []

# 🔍 **Recupera una pagina per slug e negozio**
def get_page_by_slug(slug, shop_name):
    try:
        page = Page.query.filter_by(slug=slug, shop_name=shop_name).first()
        return page_to_dict(page) if page else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero della pagina {slug} per {shop_name}: {e}")
        return None

# ✅ **Crea una nuova pagina**
def create_page(data):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione della pagina: {e}")
        return None

# 🔄 **Aggiorna il contenuto di una pagina**
def update_page_content(page_id, content):
    try:
        page = Page.query.get(page_id)
        if not page:
            return False

        page.content = content
        page.updated_at = datetime.utcnow()
        db.session.commit()
        logging.info(f"✅ Contenuto della pagina {page_id} aggiornato")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento della pagina {page_id}: {e}")
        return False

# 🔄 **Aggiorna i metadati SEO della pagina**
def update_page_seo(page_id, data):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento SEO della pagina {page_id}: {e}")
        return False

# ❌ **Elimina una pagina**
def delete_page(page_id):
    try:
        page = Page.query.get(page_id)
        if not page:
            return False

        db.session.delete(page)
        db.session.commit()
        logging.info(f"✅ Pagina {page_id} eliminata con successo")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione della pagina {page_id}: {e}")
        return False

# 🔍 **Recupera una pagina tradotta**
def get_page_by_slug_and_language(slug, language, shop_name):
    try:
        page = Page.query.filter_by(slug=slug, language=language, shop_name=shop_name).first()
        return page_to_dict(page) if page else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero della pagina tradotta {slug}: {e}")
        return None

# ✅ **Aggiorna o crea una pagina tradotta**
def update_or_create_page_content(page_id, content, language, shop_name):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione/aggiornamento della pagina tradotta: {e}")
        return False

# 🔍 **Recupera le pagine pubblicate**
def get_published_pages(shop_name):
    try:
        pages = Page.query.filter_by(shop_name=shop_name, published=True).all()
        return [page_to_dict(p) for p in pages if p.slug not in ["navbar", "footer"]]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero delle pagine pubblicate per {shop_name}: {e}")
        return []

# 🎨 **Applica un tema a un negozio**
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

# 📌 **Helper per convertire una pagina in dizionario**
def page_to_dict(page):
    return {col.name: getattr(page, col.name) for col in Page.__table__.columns} if page else None
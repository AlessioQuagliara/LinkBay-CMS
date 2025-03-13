from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from models.page import Page, get_published_pages
from models.shoplist import ShopList
from models.cmsaddon import CMSAddon, ShopAddon
from models.products import Product
from models.navbar import NavbarLink
from models.site_visits import SiteVisit
from config import Config
from datetime import datetime, timedelta
from functools import wraps
import os, uuid, re, base64, logging
from sqlalchemy.exc import SQLAlchemyError
from helpers import check_user_authentication, get_navbar_content
from models.database import db  # Importa il database SQLAlchemy

logging.basicConfig(level=logging.INFO)

# Blueprint
page_bp = Blueprint('page', __name__)

# 🔄 Funzione Helper per gestire gli errori
def handle_request_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"❌ Errore nel database: {str(e)}")
            flash('Errore durante l\'accesso ai dati del negozio o della pagina.', 'danger')
            return redirect(url_for('ui.homepage'))
        except Exception as e:
            logging.error(f"❌ Errore in {func.__name__}: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    return wrapper

# 🔄 Funzione Helper per salvare immagini base64
def save_image(base64_img, page_id, shop_subdomain):
    try:
        img_data = base64_img.split(',')[1]
        img_bytes = base64.b64decode(img_data)
        img_format = base64_img.split(';')[0].split('/')[1]
        img_filename = f"{uuid.uuid4()}.{img_format}"
        img_path = os.path.join(Config.UPLOAD_FOLDER, shop_subdomain, 'pages', str(page_id), img_filename)
        
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        with open(img_path, 'wb') as img_file:
            img_file.write(img_bytes)
        
        return f"/static/uploads/{shop_subdomain}/pages/{page_id}/{img_filename}"
    except Exception as e:
        logging.error(f"❌ Errore nel salvataggio dell'immagine: {str(e)}")
        return None

# Rotte per la gestione delle pagine
@page_bp.route('/admin/cms/pages/online-content')
@handle_request_errors
def online_content():
    """
    Mostra il contenuto online del negozio.
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, lo reindirizziamo correttamente
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    logging.info(f"📢 Accesso al contenuto online per: {shop_subdomain} da {request.remote_addr}")

    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash('Nessun negozio trovato per questo nome.', 'warning')
        return redirect(url_for('ui.homepage'))

    # Recupera la pagina "home"
    page = db.session.query(Page).filter_by(slug='home', shop_name=shop_subdomain).first()
    if page:
        minutes_ago = (datetime.utcnow() - page.updated_at).total_seconds() // 60
        return render_template(
            'admin/cms/pages/content.html', 
            title='Online Content', 
            username=username, 
            page=page,
            shop=shop,
            minutes_ago=int(minutes_ago)
        )
    
    flash("La pagina home non è stata trovata. Verifica le impostazioni del tema.", "warning")
    return redirect(url_for('cmsaddon.theme_ui'))  # ✅ Aggiunto flash per feedback all'utente

@page_bp.route('/admin/cms/function/edit-code/<slug>')
@handle_request_errors
def edit_code_page(slug):
    """
    Permette la modifica del codice di una pagina specifica identificata dallo slug.
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, lo reindirizziamo correttamente
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]

    # Recupera la pagina specifica e tutte le pagine dello shop
    page = db.session.query(Page).filter_by(slug=slug, shop_name=shop_subdomain).first()
    pages = db.session.query(Page).filter_by(shop_name=shop_subdomain).all()

    if not page:
        flash("La pagina specificata non è stata trovata.", "warning")
        return redirect(url_for('page_bp.online_content'))  # ✅ Redirect a una pagina esistente

    return render_template(
        'admin/cms/store_editor/code_editor.html', 
        title=page.title, 
        pages=pages,
        page=page, 
        slug=slug,  
        content=page.content, 
        username=username
    )

@page_bp.route('/admin/cms/function/save_code', methods=['POST'])
@handle_request_errors
def save_code_page():
    data = request.get_json()
    content = data.get('content')
    slug = data.get('slug')

    if not content or not slug:
        return jsonify({'success': False, 'error': 'Missing content or slug'}), 400

    shop_subdomain = request.host.split('.')[0]
    page = db.session.query(Page).filter_by(slug=slug, shop_name=shop_subdomain).first()

    if page:
        page.content = content
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Page not found'}), 404

@page_bp.route('/admin/cms/store_editor/editor_interface', defaults={'slug': None})
@page_bp.route('/admin/cms/store_editor/editor_interface/<slug>')
@handle_request_errors
def editor_interface(slug=None):
    """
    Interfaccia dell'editor per modificare i contenuti delle pagine del negozio.
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, lo reindirizziamo correttamente
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()

    if not shop:
        flash('Nessun negozio selezionato o negozio non trovato.', 'danger')
        return redirect(url_for('ui.homepage'))  # ✅ Assicurati che la route esista

    pages = db.session.query(Page).filter_by(shop_name=shop_subdomain).all()
    page = db.session.query(Page).filter_by(slug=slug, shop_name=shop_subdomain).first() if slug else None

    if slug and not page:
        flash("La pagina specificata non è stata trovata.", "warning")
        return redirect(url_for('page_bp.editor_interface'))  # ✅ Redirect alla lista delle pagine

    page_title = page.title if page else 'CMS Interface'

    # Recupera il tema UI selezionato
    selected_theme_ui = db.session.query(ShopAddon).filter_by(shop_name=shop_subdomain, addon_type='theme_ui').first()

    return render_template(
        'admin/cms/store_editor/editor_interface.html', 
        title=page_title, 
        pages=pages, 
        page=page,
        slug=slug,  
        current_url=request.path, 
        username=username,
        selected_theme_ui=selected_theme_ui
    )

@page_bp.route('/admin/cms/function/edit/<slug>')
@handle_request_errors
def edit_page(slug):
    """
    Permette la modifica di una pagina specifica del negozio.
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, lo reindirizziamo correttamente
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()

    if not shop:
        flash('Nessun negozio selezionato o negozio non trovato.', 'danger')
        return redirect(url_for('page_bp.editor_interface'))  # ✅ Redirect all'editor invece della homepage

    # Recupera la lingua selezionata (default "en")
    language = request.args.get('language', 'en')

    page = db.session.query(Page).filter_by(slug=slug, language=language, shop_name=shop_subdomain).first()

    if not page:
        flash('Pagina non trovata.', 'danger')
        return redirect(url_for('page_bp.editor_interface'))  # ✅ Redirect all'editor invece della homepage

    selected_theme_ui = db.session.query(ShopAddon).filter_by(shop_name=shop_subdomain, addon_type='theme_ui').first()
    navbar_content = get_navbar_content(shop_subdomain)

    return render_template(
        'admin/cms/function/edit.html', 
        title='Edit Page', 
        page=page, 
        username=username, 
        selected_theme_ui=selected_theme_ui,
        navbar=navbar_content
    )

# 🔹 **Salvataggio della pagina con gestione immagini**
@page_bp.route('/admin/cms/function/save', methods=['POST'])
@handle_request_errors
def save_page():
    data = request.get_json()
    page_id = data.get('id')
    content = data.get('content')
    language = data.get('language')  
    shop_subdomain = request.host.split('.')[0]

    logging.info(f"📢 Salvataggio pagina con ID: {page_id}, lingua: {language} per il negozio: {shop_subdomain}")
    
    page = db.session.query(Page).filter_by(id=page_id, shop_name=shop_subdomain).first()
    
    if page:
        # Cerca e salva immagini base64 nel contenuto
        img_tags = re.findall(r'<img.*?src=["\'](data:image/[^"\']+)["\']', content)
        for base64_img in img_tags:
            image_url = save_image(base64_img, page_id, shop_subdomain)
            if image_url:
                content = content.replace(base64_img, image_url)

        page.content = content
        page.updated_at = db.func.now()
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Pagina non trovata'}), 404

# 🔹 **Salvataggio SEO della pagina**
@page_bp.route('/admin/cms/function/save-seo', methods=['POST'])
@handle_request_errors
def save_seo_page():
    data = request.get_json()
    page_id = data.get('id')
    title = data.get('title')
    description = data.get('description')
    keywords = data.get('keywords')
    slug = data.get('slug')
    shop_subdomain = request.host.split('.')[0]  

    page = db.session.query(Page).filter_by(id=page_id, shop_name=shop_subdomain).first()
    
    if page:
        page.title = title
        page.description = description
        page.keywords = keywords
        page.slug = slug
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Pagina non trovata'}), 404

# 🔹 **Creazione di una nuova pagina**
@page_bp.route('/admin/cms/function/create', methods=['POST'])
@handle_request_errors
def create_page():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Devi effettuare il login'})

    data = request.get_json()
    shop_subdomain = request.host.split('.')[0]

    new_page = Page(
        title=data.get('title'),
        description=data.get('description'),
        keywords=data.get('keywords'),
        slug=data.get('slug'),
        content=data.get('content'),
        theme_name=data.get('theme_name'),
        paid=data.get('paid'),
        language=data.get('language'),
        published=data.get('published'),
        shop_name=shop_subdomain
    )

    db.session.add(new_page)
    db.session.commit()

    return jsonify({'success': True})

# 🔹 **Eliminazione di una pagina**
@page_bp.route('/admin/cms/function/delete', methods=['POST'])
@handle_request_errors
def delete_page():
    data = request.get_json()
    page_id = data.get('id')  
    shop_subdomain = request.host.split('.')[0]  

    page = db.session.query(Page).filter_by(id=page_id, shop_name=shop_subdomain).first()

    if page:
        db.session.delete(page)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Pagina eliminata'})
    else:
        return jsonify({'success': False, 'message': 'Pagina non trovata'}), 404

    
# SALVATAGGIO PAGINA CON CARICAMENTO IMMAGINI ----------------------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(base64_image, page_id, shop_subdomain):
    try:
        header, encoded = base64_image.split(",", 1)
        binary_data = base64.b64decode(encoded)

        # Creazione della cartella per il negozio specifico
        upload_folder = f"static/uploads/{shop_subdomain}"
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)  

        # Nome univoco per ogni immagine, ad esempio usando un UUID
        image_name = f"{page_id}_{uuid.uuid4().hex}.png"
        image_path = os.path.join(upload_folder, image_name)

        # Salva l'immagine
        with open(image_path, "wb") as f:
            f.write(binary_data)

        return f"/{upload_folder}/{image_name}"
    except Exception as e:
        logging.info(f"Error saving image: {str(e)}")
        return None
    
# Funzione per salvare un'immagine base64 generica ---------------------------------------------------------------
def save_base64_image(base64_image, upload_folder):
    try:
        header, encoded = base64_image.split(",", 1)
        binary_data = base64.b64decode(encoded)

        # Genera un nome file unico usando UUID
        unique_filename = f"{uuid.uuid4().hex}.png"
        file_path = os.path.join(upload_folder, unique_filename)

        # Salva il file sul server
        with open(file_path, "wb") as f:
            f.write(binary_data)

        return f"/static/uploads/{unique_filename}"
    except Exception as e:
        logging.info(f"Errore durante il salvataggio dell'immagine: {str(e)}")
        return None
    
# 🔹 **Visualizzazione delle impostazioni Navbar**
@page_bp.route('/admin/cms/function/navbar-settings')
@handle_request_errors
def navbar_settings():
    """
    Visualizza le impostazioni della Navbar per il negozio corrente.
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, reindirizza alla login
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_name = request.host.split('.')[0]

    navbar_links = db.session.query(NavbarLink).filter_by(shop_name=shop_name).all()
    pages = get_published_pages(shop_name)

    if not navbar_links:
        flash("Nessun link di navigazione trovato. Aggiungine uno per personalizzare la Navbar.", "info")

    if not pages:
        flash("Nessuna pagina pubblicata trovata per il negozio.", "info")

    return render_template(
        'admin/cms/function/navigation.html',
        title="Navbar Settings",
        navbar_links=navbar_links,
        pages=pages,
        username=username  # ✅ Passa il nome utente al template
    )

# 🔹 **API per ottenere i link della navbar**
@page_bp.route('/api/get-navbar-links', methods=['GET'])
@handle_request_errors
def get_navbar_links():
    shop_name = request.host.split('.')[0]
    navbar_links = db.session.query(NavbarLink).filter_by(shop_name=shop_name).all()

    return jsonify({'success': True, 'navbar_links': [link.to_dict() for link in navbar_links]})

# 🔹 **Aggiunta di un nuovo link alla navbar**
@page_bp.route('/api/add-navbar-link', methods=['POST'])
@handle_request_errors
def add_navbar_link():
    data = request.get_json()
    shop_name = request.host.split('.')[0]

    new_link = NavbarLink(
        shop_name=shop_name,
        link_text=data.get('link_text', 'New Link'),
        link_url=data.get('link_url', '/link'),
        link_type=data.get('link_type', 'standard'),
        parent_id=data.get('parent_id'),
        position=data.get('position', 1)
    )

    db.session.add(new_link)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Link aggiunto con successo'})

# 🔹 **Eliminazione di più link della navbar**
@page_bp.route('/api/delete-navbar-links', methods=['POST'])
@handle_request_errors
def delete_navbar_links():
    data = request.get_json()
    shop_name = request.host.split('.')[0]
    link_ids = data.get('ids', [])

    db.session.query(NavbarLink).filter(NavbarLink.id.in_(link_ids), NavbarLink.shop_name == shop_name).delete(synchronize_session=False)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Link eliminati con successo'})

# 🔹 **Salvataggio della navbar aggiornata**
@page_bp.route('/api/save-navbar', methods=['POST'])
@handle_request_errors
def save_navbar():
    data = request.get_json()
    navbar_links = data.get("navbar_links", [])
    shop_name = request.host.split('.')[0]

    if not navbar_links:
        return jsonify({'success': False, 'error': 'Nessun link ricevuto'}), 400

    # Elimina tutti i link esistenti
    db.session.query(NavbarLink).filter_by(shop_name=shop_name).delete()

    # Salva i nuovi link
    for link in navbar_links:
        new_link = NavbarLink(
            shop_name=shop_name,
            link_text=link.get("link_text"),
            link_url=link.get("link_url"),
            link_type=link.get("link_type"),
            parent_id=link.get("parent_id"),
            position=link.get("position")
        )
        db.session.add(new_link)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Navbar salvata con successo!'})

# 🔹 **API per ottenere le pagine pubblicate**
@page_bp.route('/api/get-pages', methods=['GET'])
@handle_request_errors
def get_pages():
    shop_name = request.host.split('.')[0]
    pages = db.session.query(Page).filter_by(shop_name=shop_name, published=True).all()

    # Converti ogni oggetto Page in un dizionario
    pages_data = [{
        'id': page.id,
        'title': page.title,
        'description': page.description,
        'slug': page.slug,
        'content': page.content,
        'theme_name': page.theme_name,
        'paid': page.paid,
        'language': page.language,
        'published': page.published,
        'created_at': page.created_at.isoformat() if page.created_at else None,
        'updated_at': page.updated_at.isoformat() if page.updated_at else None
    } for page in pages]

    return jsonify({'success': True, 'pages': pages_data})

# 🔹 **API per ottenere le visite al sito**
@page_bp.route('/api/get-site-visits', methods=['GET'])
@handle_request_errors
def get_site_visits():
    shop_name = request.host.split('.')[0]
    visits = db.session.query(SiteVisit).filter_by(shop_name=shop_name).order_by(SiteVisit.timestamp.desc()).limit(100).all()

    return jsonify({'success': True, 'visits': [visit.to_dict() for visit in visits]})
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from models.page import Page
from models.shoplist import ShopList
from models.cmsaddon import CMSAddon
from models.products import Product
from models.navbar import NavbarLink
from models.site_visits import SiteVisit
from config import Config
from datetime import datetime, timedelta
import os, uuid, re, base64, logging
from sqlalchemy.exc import SQLAlchemyError
from helpers import check_user_authentication, get_navbar_content
from models.database import db  # Importa il database SQLAlchemy

logging.basicConfig(level=logging.INFO)

# Blueprint
page_bp = Blueprint('page', __name__)

# Rotte per la gestione delle pagine

@page_bp.route('/admin/cms/pages/online-content')
def online_content():
    username = check_user_authentication()
    
    if not isinstance(username, str):
        return username

    shop_subdomain = request.host.split('.')[0]
    logging.info(f"📢 Accesso al contenuto online per: {shop_subdomain} da {request.remote_addr}")

    try:
        shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()

        if not shop:
            flash('Nessun negozio trovato per questo nome.', 'warning')
            return redirect(url_for('ui.homepage'))

        # Recupera la pagina "home"
        page = db.session.query(Page).filter_by(slug='home', shop_name=shop_subdomain).first()

        if page:
            minutes_ago = (datetime.utcnow() - page.updated_at).total_seconds() // 60
            return render_template('admin/cms/pages/content.html', 
                                   title='Online Content', 
                                   username=username, 
                                   page=page,
                                   shop=shop,
                                   minutes_ago=int(minutes_ago))
        else:
            return redirect(url_for('cmsaddon.theme_ui'))

    except SQLAlchemyError as e:
        logging.error(f"❌ Errore nel database: {str(e)}")
        flash('Errore durante l\'accesso ai dati del negozio o della pagina.', 'danger')
        return redirect(url_for('ui.homepage'))


@page_bp.route('/admin/cms/function/edit-code/<slug>')
def edit_code_page(slug):
    username = check_user_authentication()
    
    if not isinstance(username, str):
        return username

    shop_subdomain = request.host.split('.')[0]
    
    page = db.session.query(Page).filter_by(slug=slug, shop_name=shop_subdomain).first()
    pages = db.session.query(Page).filter_by(shop_name=shop_subdomain).all()

    if page:
        return render_template('admin/cms/store_editor/code_editor.html', 
                               title=page.title, 
                               pages=pages,
                               page=page, 
                               slug=slug,  
                               content=page.content, 
                               username=username)
    
    return username


@page_bp.route('/admin/cms/function/save_code', methods=['POST'])
def save_code_page():
    try:
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

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Errore nel salvataggio del codice: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@page_bp.route('/admin/cms/store_editor/editor_interface', defaults={'slug': None})
@page_bp.route('/admin/cms/store_editor/editor_interface/<slug>')
def editor_interface(slug=None):
    username = check_user_authentication()
    
    if not isinstance(username, str):
        return username

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()

    if not shop:
        flash('Nessun negozio selezionato o negozio non trovato.', 'danger')
        return redirect(url_for('ui.homepage'))

    pages = db.session.query(Page).filter_by(shop_name=shop_subdomain).all()
    page = db.session.query(Page).filter_by(slug=slug, shop_name=shop_subdomain).first() if slug else None
    page_title = page.title if page else 'CMS Interface'

    # Recupera il tema UI selezionato
    selected_theme_ui = db.session.query(CMSAddon).filter_by(shop_name=shop_subdomain, type='theme_ui').first()

    return render_template('admin/cms/store_editor/editor_interface.html', 
                           title=page_title, 
                           pages=pages, 
                           page=page,
                           slug=slug,  
                           current_url=request.path, 
                           username=username,
                           selected_theme_ui=selected_theme_ui)


@page_bp.route('/admin/cms/function/edit/<slug>')
def edit_page(slug):
    username = check_user_authentication()
    
    if not isinstance(username, str):
        return username

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()

    if not shop:
        flash('Nessun negozio selezionato o negozio non trovato.', 'danger')
        return redirect(url_for('ui.homepage'))

    # Recupera la lingua selezionata (default "en")
    language = request.args.get('language', 'en')

    page = db.session.query(Page).filter_by(slug=slug, language=language, shop_name=shop_subdomain).first()

    if not page:
        flash('Pagina non trovata.', 'danger')
        return redirect(url_for('ui.homepage'))

    selected_theme_ui = db.session.query(CMSAddon).filter_by(shop_name=shop_subdomain, type='theme_ui').first()
    
    product_references = page.get_product_references()
    products = [db.session.query(Product).get(product_id) for product_id in product_references]

    navbar_content = get_navbar_content(shop_subdomain)

    return render_template('admin/cms/function/edit.html', 
                           title='Edit Page', 
                           page=page, 
                           username=username, 
                           selected_theme_ui=selected_theme_ui,
                           products=products,
                           navbar=navbar_content)


# 🔹 **Salvataggio della pagina con gestione immagini**
@page_bp.route('/admin/cms/function/save', methods=['POST'])
def save_page():
    try:
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
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Errore nel salvataggio della pagina: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 🔹 **Salvataggio SEO della pagina**
@page_bp.route('/admin/cms/function/save-seo', methods=['POST'])
def save_seo_page():
    try:
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

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Errore nel salvataggio SEO: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 🔹 **Creazione di una nuova pagina**
@page_bp.route('/admin/cms/function/create', methods=['POST'])
def create_page():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Devi effettuare il login'})

    try:
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
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione della pagina: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 🔹 **Eliminazione di una pagina**
@page_bp.route('/admin/cms/function/delete', methods=['POST'])
def delete_page():
    try:
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
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione della pagina: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

    
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
def navbar_settings():
    shop_name = request.host.split('.')[0]

    navbar_links = db.session.query(NavbarLink).filter_by(shop_name=shop_name).all()
    pages = db.session.query(Page).filter_by(shop_name=shop_name, published=True).all()

    return render_template(
        'admin/cms/function/navigation.html',
        title="Navbar Settings",
        navbar_links=navbar_links,
        pages=pages
    )

# 🔹 **API per ottenere i link della navbar**
@page_bp.route('/api/get-navbar-links', methods=['GET'])
def get_navbar_links():
    try:
        shop_name = request.host.split('.')[0]
        navbar_links = db.session.query(NavbarLink).filter_by(shop_name=shop_name).all()

        return jsonify({'success': True, 'navbar_links': [link.to_dict() for link in navbar_links]})
    except SQLAlchemyError as e:
        logging.error(f"❌ Errore nel recupero della navbar: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 🔹 **Aggiunta di un nuovo link alla navbar**
@page_bp.route('/api/add-navbar-link', methods=['POST'])
def add_navbar_link():
    try:
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

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiunta del link navbar: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 🔹 **Eliminazione di più link della navbar**
@page_bp.route('/api/delete-navbar-links', methods=['POST'])
def delete_navbar_links():
    try:
        data = request.get_json()
        shop_name = request.host.split('.')[0]
        link_ids = data.get('ids', [])

        db.session.query(NavbarLink).filter(NavbarLink.id.in_(link_ids), NavbarLink.shop_name == shop_name).delete(synchronize_session=False)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Link eliminati con successo'})

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione dei link navbar: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 🔹 **Salvataggio della navbar aggiornata**
@page_bp.route('/api/save-navbar', methods=['POST'])
def save_navbar():
    try:
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

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Errore nel salvataggio della navbar: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 🔹 **API per ottenere le pagine pubblicate**
@page_bp.route('/api/get-pages', methods=['GET'])
def get_pages():
    try:
        shop_name = request.host.split('.')[0]
        pages = db.session.query(Page).filter_by(shop_name=shop_name, published=True).all()

        return jsonify({'success': True, 'pages': [page.to_dict() for page in pages]})
    except SQLAlchemyError as e:
        logging.error(f"❌ Errore nel recupero delle pagine: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 🔹 **API per ottenere le visite al sito**
@page_bp.route('/api/get-site-visits', methods=['GET'])
def get_site_visits():
    try:
        shop_name = request.host.split('.')[0]
        visits = db.session.query(SiteVisit).filter_by(shop_name=shop_name).order_by(SiteVisit.timestamp.desc()).limit(100).all()

        return jsonify({'success': True, 'visits': [visit.to_dict() for visit in visits]})
    except SQLAlchemyError as e:
        logging.error(f"❌ Errore nel recupero delle visite al sito: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
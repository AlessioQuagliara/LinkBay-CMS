from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from models.page import Page  # importo la classe database
from models.shoplist import ShopList
from models.cmsaddon import CMSAddon
from models.products import Products
from models.navbar import Navbar
from models.site_visits import SiteVisits 
from config import Config
from datetime import datetime, timedelta
import mysql.connector, os, uuid, re, base64, datetime
from db_helpers import DatabaseHelper
db_helper = DatabaseHelper()
from db_helpers import DatabaseHelper
from helpers import check_user_authentication, get_navbar_content 
import logging
logging.basicConfig(level=logging.INFO)


# Blueprint
page_bp = Blueprint('page', __name__)

# Rotte per la gestione

@page_bp.route('/admin/cms/pages/online-content')
def online_content():
    username = check_user_authentication()
    
    if isinstance(username, str):
        shop_subdomain = request.host.split('.')[0]  
        logging.info(f"Subdomain: {shop_subdomain}")  # Log del subdominio

        try:
            with db_helper.get_auth_db_connection() as auth_db_conn:
                shoplist_model = ShopList(auth_db_conn)
                shop = shoplist_model.get_shop_by_name(shop_subdomain)

            if shop:
                logging.info(f"Shop trovato: {shop}")  # Log per il negozio

                with db_helper.get_db_connection() as db_conn:
                    page_model = Page(db_conn)
                    page_slug = 'home'
                    # Esegui la query e leggi il risultato
                    page = page_model.get_page_by_slug(page_slug, shop_subdomain)

                    if page:
                        updated_at = page['updated_at']
                        now = datetime.datetime.now()
                        minutes_ago = (now - updated_at).total_seconds() // 60  
                        return render_template(
                            'admin/cms/pages/content.html', 
                            title='Online Content', 
                            username=username, 
                            page=page,
                            shop=shop,
                            minutes_ago=int(minutes_ago)  
                        )
                    else:
                        return redirect(url_for('cmsaddon.theme_ui'))

            else:
                print("Nessun negozio trovato.")  # Log per negozio non trovato
                flash('Nessun negozio trovato per questo nome.')
                return redirect(url_for('ui.homepage'))

        except mysql.connector.Error as e:
            logging.info(f"Errore nel database: {str(e)}")  # Log del messaggio di errore
            flash('Errore durante l\'accesso ai dati del negozio o della pagina.')
            return redirect(url_for('ui.homepage'))
    
    return username

@page_bp.route('/admin/cms/function/edit-code/<slug>')
def edit_code_page(slug):
    username = check_user_authentication()
    
    if isinstance(username, str):
        db_conn = db_helper.get_db_connection() 

        shop_subdomain = request.host.split('.')[0]  
        
        page_model = Page(db_conn)
        
        pages = page_model.get_all_pages(shop_subdomain)  
        page = page_model.get_page_by_slug(slug, shop_subdomain) 

        
        if page:
            content = page.get('content', '')  
            return render_template('admin/cms/store_editor/code_editor.html', 
                                   title=page['title'], 
                                   pages=pages,
                                   page=page, 
                                   slug=slug,  
                                   content=content, 
                                   username=username)
    
    return username

# Funzione per salvare il codice modificato
@page_bp.route('/admin/cms/function/save_code', methods=['POST'])
def save_code_page():
    try:
        data = request.get_json()  
        content = data.get('content')
        slug = data.get('slug')

        if not content or not slug:
            return jsonify({'success': False, 'error': 'Missing content or slug'}), 400

        db_conn = db_helper.get_db_connection()
        
        shop_subdomain = request.host.split('.')[0]  
        
        page_model = Page(db_conn)

        success = page_model.update_page_content_by_slug(slug, content, shop_subdomain)

        return jsonify({'success': success})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@page_bp.route('/admin/cms/store_editor/editor_interface', defaults={'slug': None})
@page_bp.route('/admin/cms/store_editor/editor_interface/<slug>')
def editor_interface(slug=None):
    username = check_user_authentication()
    
    if isinstance(username, str):
        db_conn = db_helper.get_db_connection()  
        shop_subdomain = request.host.split('.')[0]

        with db_helper.get_auth_db_connection() as auth_db_conn:
            shoplist_model = ShopList(auth_db_conn)
            shop = shoplist_model.get_shop_by_name(shop_subdomain)

        if not shop:
            flash('Nessun negozio selezionato o negozio non trovato.', 'danger')
            return redirect(url_for('ui.homepage'))

        page_model = Page(db_conn)
        pages = page_model.get_all_pages(shop_name=shop_subdomain)
        page = None
        page_title = 'CMS Interface'
        
        if slug:
            page = page_model.get_page_by_slug(slug, shop_subdomain)
            if page:
                page_title = page['title']

        # Ottenere l'addon di tipo 'theme_ui' con status 'selected' per il negozio attuale
        addon_model = CMSAddon(db_conn)
        selected_theme_ui = addon_model.get_selected_addon_for_shop(shop_subdomain, 'theme_ui')

        current_url = request.path
        return render_template('admin/cms/store_editor/editor_interface.html', 
                               title=page_title, 
                               pages=pages, 
                               page=page,
                               slug=slug,  
                               current_url=current_url, 
                               username=username,
                               selected_theme_ui=selected_theme_ui)
    return username  


@page_bp.route('/admin/cms/function/edit/<slug>')
def edit_page(slug):
    username = check_user_authentication()
    
    if isinstance(username, str):
        db_conn = db_helper.get_db_connection()  
        shop_subdomain = request.host.split('.')[0]  

        with db_helper.get_auth_db_connection() as auth_db_conn:
            shoplist_model = ShopList(auth_db_conn)
            shop = shoplist_model.get_shop_by_name(shop_subdomain)

        if not shop:
            flash('Nessun negozio selezionato o negozio non trovato.', 'danger')
            return redirect(url_for('ui.homepage'))

        # Recupera la lingua selezionata (default "en")
        language = request.args.get('language', 'en')

        page_model = Page(db_conn)
        page = page_model.get_page_by_slug_and_language(slug, language, shop_subdomain)  

        if not page:
            flash('Pagina non trovata.', 'danger')
            return redirect(url_for('ui.homepage'))

        # Recupera il tema UI selezionato per lo shop
        addon_model = CMSAddon(db_conn)
        selected_theme_ui = addon_model.get_selected_addon_for_shop(shop_subdomain, 'theme_ui')

        # Recupera i dettagli del prodotto se la pagina contiene riferimenti a prodotti
        product_model = Products(db_conn)
        product_references = page_model.get_product_references(page['id'])
        products = []
        for product_id in product_references:
            product = product_model.get_product_by_id(product_id)
            if product:
                product['images'] = product_model.get_product_images(product['id'])
                products.append(product)

        # Recupera il contenuto dinamico della navbar usando il modello e gli helper
        navbar_content = get_navbar_content(shop_subdomain)

        return render_template(
            'admin/cms/function/edit.html', 
            title='Edit Page', 
            page=page, 
            username=username, 
            selected_theme_ui=selected_theme_ui,
            products=products,
            navbar=navbar_content  # Passa il contenuto della navbar al template
        )
    
    return username

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

# Funzione per salvare il contenuto della pagina con gestione delle immagini ---------------------------------
@page_bp.route('/admin/cms/function/save', methods=['POST'])
def save_page():
    try:
        data = request.get_json()
        page_id = data.get('id')
        content = data.get('content')
        language = data.get('language')  # Aggiungiamo il parametro lingua
        shop_subdomain = request.host.split('.')[0]

        logging.info(f"Salvataggio pagina con ID: {page_id}, lingua: {language} per il negozio: {shop_subdomain}")
        
        db_conn = db_helper.get_db_connection()  
        page_model = Page(db_conn)  
        
        # Cerca immagini base64 nel contenuto
        img_tags = re.findall(r'<img.*?src=["\'](data:image/[^"\']+)["\']', content)
        for base64_img in img_tags:
            # Salva l'immagine base64
            image_url = save_image(base64_img, page_id, shop_subdomain)
            if image_url:
                # Sostituisci l'immagine base64 con l'URL dell'immagine salvata
                content = content.replace(base64_img, image_url)
        
        # Aggiorna il contenuto della pagina nel database con la lingua specifica
        success = page_model.update_or_create_page_content(page_id, content, language, shop_subdomain)
        return jsonify({'success': success})
    
    except Exception as e:
        logging.info(f"Errore durante il salvataggio della pagina: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

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

# Endpoint Flask per gestire l'upload delle immagini generiche -------------------------------------------------------
@page_bp.route('/upload-image', methods=['POST'])
def upload_image():
    data = request.get_json()
    base64_image = data.get('image')

    if not base64_image:
        return jsonify({'error': 'No image provided'}), 400

    upload_folder = "static/uploads"
    image_url = save_base64_image(base64_image, upload_folder)
    
    if image_url:
        return jsonify({'url': image_url}), 200
    else:
        return jsonify({'error': 'Failed to upload image'}), 500
    
# Upload SEO -------------------------------------------------------

# Funzione per salvare i dati SEO della pagina
@page_bp.route('/admin/cms/function/save-seo', methods=['POST'])
def save_seo_page():
    data = request.get_json()
    page_id = data.get('id')
    title = data.get('title')
    description = data.get('description')
    keywords = data.get('keywords')
    slug = data.get('slug')

    shop_subdomain = request.host.split('.')[0]  

    db_conn = db_helper.get_db_connection()  
    page_model = Page(db_conn)  

    success = page_model.update_page_seo(page_id, title, description, keywords, slug, shop_name=shop_subdomain)

    return jsonify({'success': success})


# Funzione per creare una nuova pagina per un negozio specifico
@page_bp.route('/admin/cms/function/create', methods=['POST'])
def create_page():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'You need to log in first.'})

    if request.method == 'POST':
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        keywords = data.get('keywords')
        slug = data.get('slug')
        content = data.get('content')
        theme_name = data.get('theme_name')
        paid = data.get('paid')
        language = data.get('language')
        published = data.get('published')

        shop_subdomain = request.host.split('.')[0]  

        db_conn = db_helper.get_db_connection()
        page_model = Page(db_conn)  

        success = page_model.create_page(title, description, keywords, slug, content, theme_name, paid, language, published, shop_name=shop_subdomain)

        return jsonify({'success': success})
    

# Funzione per eliminare una pagina di un negozio specifico
@page_bp.route('/admin/cms/function/delete', methods=['POST'])
def delete_page():
    data = request.get_json()
    page_id = data.get('id')  

    if not page_id:
        return jsonify({'success': False, 'message': 'ID pagina mancante.'})
    shop_subdomain = request.host.split('.')[0]  

    page_model = Page(db_helper.get_db_connection())  
    try:
        page_model.delete_page(page_id, shop_name=shop_subdomain)  
        return jsonify({'success': True, 'message': 'Pagina cancellata con successo.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f"Errore durante la cancellazione: {str(e)}"})


# ----------------------------------------------
# 📌 ROUTE: NAVBAR SETTINGS (Visualizza Impostazioni Navbar)
# ----------------------------------------------

@page_bp.route('/admin/cms/function/navbar-settings')
def navbar_settings():
    shop_name = request.host.split('.')[0]
    with db_helper.get_db_connection() as db_conn:
        navbar_model = Navbar(db_conn)
        pages_model = Page(db_conn)
        navbar_links = navbar_model.get_navbar_links(shop_name)
        pages = pages_model.get_published_pages(shop_name)
    return render_template(
        'admin/cms/function/navigation.html',
        title="Navbar Settings",
        navbar_links=navbar_links,
        pages=pages
    )

@page_bp.route('/api/get-navbar-links', methods=['GET'])
def get_navbar_links():
    shop_name = request.host.split('.')[0]
    with db_helper.get_db_connection() as db_conn:
        navbar_model = Navbar(db_conn)
        navbar_links = navbar_model.get_navbar_links(shop_name)
    return jsonify({'success': True, 'navbar_links': navbar_links})

@page_bp.route('/api/add-navbar-link', methods=['POST'])
def add_navbar_link():
    try:
        data = request.get_json()
        shop_name = request.host.split('.')[0]

        new_link = {
            'link_text': data.get('link_text', 'New Link'),
            'link_url': data.get('link_url', '/link'),
            'link_type': data.get('link_type', 'standard'),
            'parent_id': data.get('parent_id', None),
            'position': data.get('position', 1)
        }

        with db_helper.get_db_connection() as db_conn:
            navbar_model = Navbar(db_conn)
            navbar_model.create_navbar_link(shop_name, **new_link)

        return jsonify({'success': True, 'message': 'Link aggiunto con successo'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@page_bp.route('/api/delete-navbar-links', methods=['POST'])
def delete_navbar_links():
    data = request.get_json()
    shop_name = request.host.split('.')[0]
    link_ids = data.get('ids', [])
    with db_helper.get_db_connection() as db_conn:
        navbar_model = Navbar(db_conn)
        for link_id in link_ids:
            navbar_model.delete_navbar_link(link_id, shop_name)
    return jsonify({'success': True, 'message': 'Link eliminati con successo'})

@page_bp.route('/api/save-navbar', methods=['POST'])
def save_navbar():
    try:
        data = request.get_json()
        navbar_links = data.get("navbar_links", [])
        shop_name = request.host.split('.')[0]

        if not navbar_links:
            return jsonify({'success': False, 'error': 'Nessun link ricevuto'}), 400

        with db_helper.get_db_connection() as db_conn:
            navbar_model = Navbar(db_conn)
            navbar_model.delete_all_navbar_links(shop_name)  # Cancella i link esistenti
            
            # Salva i nuovi link
            for link in navbar_links:
                navbar_model.create_navbar_link(
                    shop_name=shop_name,
                    link_text=link.get("link_text"),
                    link_url=link.get("link_url"),
                    link_type=link.get("link_type"),
                    parent_id=link.get("parent_id"),
                    position=link.get("position")
                )

        return jsonify({'success': True, 'message': 'Navbar salvata con successo!'})

    except Exception as e:
        logging.error(f"Errore nel salvataggio della navbar: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@page_bp.route('/api/get-pages', methods=['GET'])
def get_pages():
    """ Recupera le pagine pubblicate per il negozio corrente """
    try:
        shop_name = request.host.split('.')[0]
        with db_helper.get_db_connection() as db_conn:
            pages_model = Page(db_conn)
            pages = pages_model.get_published_pages(shop_name)

        if pages:
            return jsonify({'success': True, 'pages': pages})
        else:
            return jsonify({'success': False, 'message': 'Nessuna pagina pubblicata trovata'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@page_bp.route('/api/get-site-visits', methods=['GET'])
def get_site_visits():
    """
    API per recuperare le visite del negozio corrente.
    """
    try:
        shop_name = request.host.split('.')[0] if request.host else None

        if not shop_name:
            return jsonify({'success': False, 'error': 'Invalid shop name'}), 400

        # Connessione al database
        with db_helper.get_db_connection() as conn:
            site_visits = SiteVisits(conn)
            visits = site_visits.get_recent_visits(shop_name, limit=100)

        return jsonify({'success': True, 'visits': visits})

    except Exception as e:
        logging.error(f"Errore in get_site_visits: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
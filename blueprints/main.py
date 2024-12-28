from flask import Blueprint, render_template, request
from helpers import get_navbar_content, get_footer_content, get_web_settings, load_page_content, get_language
from models.collections import Collections
from models.page import Page
from models.products import Products
from helpers import get_navbar_content, get_footer_content, get_web_settings, load_page_content, get_language
from db_helpers import DatabaseHelper

db_helper = DatabaseHelper()

# Crea il Blueprint per le rotte principali
main_bp = Blueprint('main', __name__)

# Rotta principale --- Per pagine standard
@main_bp.route('/', defaults={'slug': 'home'})
@main_bp.route('/<slug>')
def render_dynamic_page(slug=None):
    # ri-ottengo il sottodominio per problemi
    shop_subdomain = request.host.split('.')[0]

    page = load_page_content(slug, shop_subdomain)

    if page:
        # lingua corrente
        language = get_language()

        # navbar e il footer specifici 
        navbar_content = get_navbar_content(shop_subdomain)
        footer_content = get_footer_content(shop_subdomain)

        # dati da web_settings
        web_settings = get_web_settings(shop_subdomain)

        # 'head', 'script', e 'foot' da web_settings
        head_content = web_settings.get('head', '')
        script_content = web_settings.get('script', '')
        foot_content = web_settings.get('foot', '')

        return render_template('index.html',
                               title=page['title'], 
                               description=page['description'], 
                               keywords=page['keywords'], 
                               content=page['content'], 
                               navbar=navbar_content,  
                               footer=footer_content,  
                               language=language,
                               head=head_content,  
                               script=script_content,  
                               foot=foot_content)  
    else:
        return render_template('errors/404.html'), 404

# Rotta per pagina Collezioni
@main_bp.route('/collections/<slug>', methods=['GET'])
@main_bp.route('/collections', defaults={'slug': None}, methods=['GET'])
def render_collection(slug=None):
    shop_subdomain = request.host.split('.')[0]  # Ottieni il sottodominio
    conn = db_helper.get_db_connection()

    # Inizializza i modelli
    collection_model = Collections(conn)
    product_model = Products(conn)

    # Carica i dettagli della collezione specifica o tutte le collezioni
    if slug:
        collection = collection_model.get_collection_by_slug(slug)
        if not collection:
            return render_template('errors/404.html'), 404
        products_in_collection = collection_model.get_products_in_collection(collection['id'])
        product_images = product_model.get_images_for_products([p['id'] for p in products_in_collection])
    else:
        collection = None
        products_in_collection = product_model.get_all_products()
        product_images = product_model.get_images_for_products([p['id'] for p in products_in_collection])

    # Aggiungi immagini ai prodotti
    for product in products_in_collection:
        product['images'] = [
            img for img in product_images if img['product_id'] == product['id']
        ]

    # Carica contenuti navbar e footer
    navbar_content = get_navbar_content(shop_subdomain)
    footer_content = get_footer_content(shop_subdomain)

    # Impostazioni web del negozio
    web_settings = get_web_settings(shop_subdomain)
    head_content = web_settings.get('head', '')
    script_content = web_settings.get('script', '')
    foot_content = web_settings.get('foot', '')

    # Render della pagina
    return render_template(
        'collection.html',
        title=collection['name'] if collection else 'All Collections',
        description=collection['description'] if collection else 'Browse our collections and products.',
        collection=collection,
        products=products_in_collection,
        navbar=navbar_content,
        footer=footer_content,
        head=head_content,
        script=script_content,
        foot=foot_content
    )
    
# Rotta per pagina Prodotti
@main_bp.route('/products/<slug>', methods=['GET'])
def render_product(slug):
    shop_subdomain = request.host.split('.')[0]  # Ottieni il sottodominio
    conn = db_helper.get_db_connection()

    # Carica i dettagli del prodotto
    product_model = Products(conn)
    product = product_model.get_product_by_slug(slug, shop_subdomain)

    # Carica i dettagli della pagina
    page_model = Page(conn)
    page = page_model.get_page_by_slug('products', shop_subdomain)

    if product:
        # Recupera le immagini del prodotto
        product_images = product_model.get_product_images(product['id'])

        # Carica contenuti navbar e footer
        navbar_content = get_navbar_content(shop_subdomain)
        footer_content = get_footer_content(shop_subdomain)

        # Impostazioni web del negozio
        web_settings = get_web_settings(shop_subdomain)
        head_content = web_settings.get('head', '')
        script_content = web_settings.get('script', '')
        foot_content = web_settings.get('foot', '')

        # Render della pagina
        return render_template(
            'product.html',
            title=product['name'],
            description=product['short_description'],
            product=product,
            page=page['content'],
            images=product_images,  # Passa le immagini al template
            navbar=navbar_content,
            footer=footer_content,
            head=head_content,
            script=script_content,
            foot=foot_content
        )
    else:
        return render_template('errors/404.html'), 404
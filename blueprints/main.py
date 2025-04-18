from flask import Blueprint, render_template, request, jsonify
from flask import g
from models.database import db
from models.collections import Collection
from models.page import Page
from models.products import Product, ProductImage
from models.cookiepolicy import CookiePolicy
from helpers import (
    get_navbar_content, get_footer_content, get_web_settings, 
    load_page_content, get_language, get_cookie_policy_content, 
    render_theme_styles
)
import logging

# 📌 Configurazione del logger
logging.basicConfig(level=logging.INFO)

# 📌 Blueprint per le rotte principali
main_bp = Blueprint('main', __name__)

# 🔹 **Rotta principale per pagine standard**
@main_bp.route("/", defaults={"slug": "home"})
@main_bp.route("/<slug>")
def render_dynamic_page(slug=None):
    """
    Renderizza una pagina dinamica basata sullo slug.
    """
    shop_subdomain = g.shop_name
    page = load_page_content(slug, shop_subdomain)

    if page:
        language = get_language()

        # 🔹 Recupera contenuto e stili della navbar
        navbar_page = load_page_content("navbar", shop_subdomain)
        navbar_content = navbar_page.content if navbar_page else ""
        navbar_styles = navbar_page.styles if navbar_page and navbar_page.styles else ""

        # 🔹 Recupera contenuto e stili del footer
        footer_page = load_page_content("footer", shop_subdomain)
        footer_content = footer_page.content if footer_page else ""
        footer_styles = footer_page.styles if footer_page and footer_page.styles else ""

        web_settings = get_web_settings(shop_subdomain)
        cookie_policy_banner = get_cookie_policy_content(shop_subdomain)

        return render_template(
            "index.html",
            title=page.title,
            description=page.description,
            keywords=page.keywords,
            content=page.content,
            styles=page.styles if page.styles else "",  # 🔹 Stili specifici della pagina
            navbar=navbar_content,  # ✅ Contenuto della navbar
            navbar_styles=navbar_styles,  # ✅ Stili della navbar
            footer=footer_content,  # ✅ Contenuto del footer
            footer_styles=footer_styles,  # ✅ Stili del footer
            cookie_policy_banner=cookie_policy_banner,
            language=language,
            head=web_settings.head if web_settings else "",
            script=web_settings.script if web_settings else "",
            foot=web_settings.foot if web_settings else "",
        )

    return render_template("errors/404.html"), 404

# 🔹 **Rotta per le collezioni**
@main_bp.route('/collections/<slug>', methods=['GET'])
@main_bp.route('/collections', defaults={'slug': None}, methods=['GET'])
def render_collection(slug=None):
    """
    Renderizza la pagina di una collezione o la lista di tutte le collezioni.
    """
    shop_subdomain = g.shop_name

    if slug:
        collection = Collection.query.filter_by(slug=slug, shop_name=shop_subdomain).first()
        if not collection:
            return render_template('errors/404.html'), 404

        products_in_collection = Product.query.filter(Product.collections.any(id=collection.id)).all()
    else:
        collection = None
        products_in_collection = Product.query.filter_by(shop_name=shop_subdomain).all()

    # Recupera immagini dei prodotti
    product_ids = [product.id for product in products_in_collection]
    product_images = ProductImage.query.filter(ProductImage.product_id.in_(product_ids)).all()

    # Assegna immagini ai prodotti
    product_image_map = {img.product_id: img.image_url for img in product_images}
    for product in products_in_collection:
        product.image_url = product_image_map.get(product.id, None)

    # Recupera i contenuti del negozio
    navbar_content = get_navbar_content(shop_subdomain)
    footer_content = get_footer_content(shop_subdomain)
    render_theme = render_theme_styles(shop_subdomain)
    web_settings = get_web_settings(shop_subdomain)

    return render_template(
        'collection.html',
        title=collection.name if collection else 'All Collections',
        description=collection.description if collection else 'Browse our collections and products.',
        collection=collection,
        products=products_in_collection,
        navbar=navbar_content,
        render_theme=render_theme,
        footer=footer_content,
        head=web_settings.get('head', ''),
        script=web_settings.get('script', ''),
        foot=web_settings.get('foot', '')
    )

# 🔹 **Rotta per la pagina di un singolo prodotto**
@main_bp.route('/products/<slug>', methods=['GET'])
def render_product(slug):
    """
    Renderizza la pagina di un singolo prodotto basandosi sullo slug.
    """
    shop_subdomain = g.shop_name

    # Recupera il prodotto
    product = Product.query.filter_by(slug=slug, shop_name=shop_subdomain).first()

    if not product:
        return render_template('errors/404.html'), 404

    # Recupera le immagini associate al prodotto
    product_images = ProductImage.query.filter_by(product_id=product.id).all()

    # Recupera i contenuti della pagina 'products'
    page = Page.query.filter_by(slug='products', shop_name=shop_subdomain).first()

    # Recupera i contenuti del negozio
    navbar_content = get_navbar_content(shop_subdomain)
    footer_content = get_footer_content(shop_subdomain)
    render_theme = render_theme_styles(shop_subdomain)
    web_settings = get_web_settings(shop_subdomain)

    # Verifica il contenuto della pagina, se esiste
    page_content = page.content if page else ""

    # Sostituzione dinamica dei placeholder
    if page_content:
        page_content = page_content.replace('{{ product.name }}', product.name)
        page_content = page_content.replace('{{ product.price }}', str(product.price))
        page_content = page_content.replace('{{ product.short_description }}', product.short_description or "")
        page_content = page_content.replace('{{ product.description }}', product.description or "")
        page_content = page_content.replace('{{ product.stock_quantity }}', str(product.stock_quantity))
        page_content = page_content.replace('{{ product.discount_price }}', str(product.discount_price) if product.discount_price else '')

    return render_template(
        'product.html',
        title=product.name,
        description=product.short_description,
        product=product,
        page=page_content,  
        images=product_images,
        navbar=navbar_content,
        render_theme=render_theme,
        footer=footer_content,
        head=web_settings.get('head', ''),
        script=web_settings.get('script', ''),
        foot=web_settings.get('foot', '')
    )
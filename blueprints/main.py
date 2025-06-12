from flask import Blueprint, render_template, request, jsonify
from flask import g
from models.database import db
from models.products import Collection, CollectionProduct
from models.page import Page
from models.products import Product, ProductImage
from models.cookiepolicy import CookiePolicy
from helpers import (
    get_navbar_content, get_footer_content, get_web_settings, 
    load_page_content, get_language, get_cookie_policy_content, 
    render_theme_styles
)
import logging
from models.websettings import WebSettings

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

        web_settings = WebSettings.query.filter_by(shop_name=g.shop_name).first()
        theme_name = web_settings.theme_name if web_settings and web_settings.theme_name else 'default'

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
            theme_name=theme_name,
        )

    return render_template("errors/404.html"), 404

# 🔹 **Rotta per le Collezioni**
@main_bp.route("/collections")
def render_collections():
    shop_subdomain = g.shop_name
    language = get_language()

    collections = Collection.query.filter_by(shop_name=shop_subdomain, is_active=True).all()

    # Navbar
    navbar_page = load_page_content("navbar", shop_subdomain)
    navbar_content = navbar_page.content if navbar_page else ""
    navbar_styles = navbar_page.styles if navbar_page and navbar_page.styles else ""

    # Footer
    footer_page = load_page_content("footer", shop_subdomain)
    footer_content = footer_page.content if footer_page else ""
    footer_styles = footer_page.styles if footer_page and footer_page.styles else ""

    web_settings = get_web_settings(shop_subdomain)
    cookie_policy_banner = get_cookie_policy_content(shop_subdomain)

    return render_template(
        "collections.html",
        title="Collections",
        description="All collections",
        keywords="collections",
        collections=collections,
        navbar=navbar_content,
        navbar_styles=navbar_styles,
        footer=footer_content,
        footer_styles=footer_styles,
        cookie_policy_banner=cookie_policy_banner,
        language=language,
        head=web_settings.get("head", ""),
        script=web_settings.get("script", ""),
        foot=web_settings.get("foot", "")
    )

# 🔹 **Rotta per i Prodotti**
@main_bp.route("/products")
def render_products():
    shop_subdomain = g.shop_name
    language = get_language()

    products = Product.query.filter_by(shop_name=shop_subdomain, is_active=True).all()

    # Navbar
    navbar_page = load_page_content("navbar", shop_subdomain)
    navbar_content = navbar_page.content if navbar_page else ""
    navbar_styles = navbar_page.styles if navbar_page and navbar_page.styles else ""

    # Footer
    footer_page = load_page_content("footer", shop_subdomain)
    footer_content = footer_page.content if footer_page else ""
    footer_styles = footer_page.styles if footer_page and footer_page.styles else ""

    web_settings = get_web_settings(shop_subdomain)
    cookie_policy_banner = get_cookie_policy_content(shop_subdomain)

    return render_template(
        "products.html",
        title="Products",
        description="All products",
        keywords="products",
        products=products,
        navbar=navbar_content,
        navbar_styles=navbar_styles,
        footer=footer_content,
        footer_styles=footer_styles,
        cookie_policy_banner=cookie_policy_banner,
        language=language,
        head=web_settings.get("head", ""),
        script=web_settings.get("script", ""),
        foot=web_settings.get("foot", "")
    )

# 🔹 **Rotta per il singolo Prodotto**
@main_bp.route("/product/<slug>")
def render_single_product(slug):
    shop_subdomain = g.shop_name
    language = get_language()

    product = Product.query.filter_by(slug=slug, shop_name=shop_subdomain).first()

    if not product:
        return render_template("errors/404.html"), 404

    # Navbar
    navbar_page = load_page_content("navbar", shop_subdomain)
    navbar_content = navbar_page.content if navbar_page else ""
    navbar_styles = navbar_page.styles if navbar_page and navbar_page.styles else ""

    # Footer
    footer_page = load_page_content("footer", shop_subdomain)
    footer_content = footer_page.content if footer_page else ""
    footer_styles = footer_page.styles if footer_page and footer_page.styles else ""

    web_settings = get_web_settings(shop_subdomain)
    cookie_policy_banner = get_cookie_policy_content(shop_subdomain)

    return render_template(
        "product.html",
        title=product.name,
        description=product.description,
        keywords=product.name,
        product=product,
        navbar=navbar_content,
        navbar_styles=navbar_styles,
        footer=footer_content,
        footer_styles=footer_styles,
        cookie_policy_banner=cookie_policy_banner,
        language=language,
        head=web_settings.get("head", ""),
        script=web_settings.get("script", ""),
        foot=web_settings.get("foot", "")
    )

# 🔹 **Rotta per il Carrello**
@main_bp.route("/cart")
def render_cart():
    shop_subdomain = g.shop_name
    language = get_language()

    # Navbar
    navbar_page = load_page_content("navbar", shop_subdomain)
    navbar_content = navbar_page.content if navbar_page else ""
    navbar_styles = navbar_page.styles if navbar_page and navbar_page.styles else ""

    # Footer
    footer_page = load_page_content("footer", shop_subdomain)
    footer_content = footer_page.content if footer_page else ""
    footer_styles = footer_page.styles if footer_page and footer_page.styles else ""

    web_settings = get_web_settings(shop_subdomain)
    cookie_policy_banner = get_cookie_policy_content(shop_subdomain)

    return render_template(
        "cart.html",
        title="Your Cart",
        description="Items in your cart",
        keywords="cart",
        navbar=navbar_content,
        navbar_styles=navbar_styles,
        footer=footer_content,
        footer_styles=footer_styles,
        cookie_policy_banner=cookie_policy_banner,
        language=language,
        head=web_settings.get("head", ""),
        script=web_settings.get("script", ""),
        foot=web_settings.get("foot", "")
    )

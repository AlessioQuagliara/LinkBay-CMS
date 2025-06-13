from flask import Blueprint, render_template, request, jsonify, Response, flash, redirect, url_for
from models.database import db
from models.products import Product, ProductVariant, ProductImage, Category, Collection, CollectionImage, CollectionProduct
import os, uuid, csv, io, base64, logging
from helpers import check_user_authentication
from sqlalchemy.exc import SQLAlchemyError
from models.shoplist import ShopList
from models.user import User
from datetime import datetime
from models.products import Product
from flask import flash
from PIL import Image

logging.basicConfig(level=logging.INFO)

# Blueprint

products_bp = Blueprint('products', __name__)

def compress_image(image_file, output_path, max_size=(800, 800), quality=75):
    try:
        img = Image.open(image_file)
        img.thumbnail(max_size)
        img.save(output_path, optimize=True, quality=quality)
        return True
    except Exception as e:
        logging.error(f"Errore durante la compressione immagine: {e}")
        return False

# RENDERING PRODOTTI -------------------------------------------------------------------------------------------------------------

@products_bp.route("/admin/cms/pages/products", methods=["GET"])
def render_products_table():
    username = check_user_authentication()

    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    logging.info(f"📢 Accesso alla tabella prodotti per: {shop_subdomain} da {request.remote_addr}")

    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash('Nessun negozio trovato per questo nome.', 'warning')
        return redirect(url_for('ui.homepage'))

    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        # Product.query.filter_by(shop_id=shop.id) is compatible if Product model no longer has stock_quantity
        products = Product.query.filter_by(shop_id=shop.id).paginate(page=page, per_page=per_page)
        categories = Category.query.all()
        return render_template(
            "admin/cms/pages/products.html", 
            products=products, 
            categories=categories,
            username=username,
            shop=shop,
            title="Gestione Prodotti"
        )
    except SQLAlchemyError as e:
        logging.error(f"❌ Errore nel recupero dei prodotti: {str(e)}")
        flash("Errore nel recupero dei dati", "danger")
        return redirect(url_for("ui.homepage"))


# CREAZIONE PRODOTTI -------------------------------------------------------------------------------------------------------------

@products_bp.route("/admin/cms/products/create", methods=["GET", "POST"])
def create_product():
    username = check_user_authentication()

    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    logging.info(f"📢 Accesso alla creazione prodotto per: {shop_subdomain} da {request.remote_addr}")

    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash('Nessun negozio trovato per questo nome.', 'warning')
        return redirect(url_for('ui.homepage'))

    if request.method == "POST":
        try:
            name = request.form.get("name")
            slug = request.form.get("slug")
            short_description = request.form.get("short_description")
            price = request.form.get("price")
            discount_price = request.form.get("discount_price") or None
            description = request.form.get("description")
            is_active = request.form.get("is_active") == "true"
            is_digital = request.form.get("is_digital") == "true"
            sku = request.form.get("sku")
            ean_code = request.form.get("ean_code")

            new_product = Product(
                shop_id=shop.id,
                name=name,
                slug=slug,
                short_description=short_description,
                price=price,
                discount_price=discount_price,
                description=description,
                is_active=is_active,
                is_digital=is_digital,
                sku=sku,
                ean_code=ean_code,
            )

            db.session.add(new_product)
            db.session.commit()

            flash("Prodotto creato con successo!", "success")
            return redirect(url_for("products.manage_product_images", product_id=new_product.id))
        except Exception as e:
            logging.error(f"❌ Errore durante la creazione del prodotto: {str(e)}")
            db.session.rollback()
            flash("Errore durante la creazione del prodotto.", "danger")

    categories = Category.query.all()
    return render_template("admin/cms/products/create_product.html", title="Crea Prodotto", product=None, username=username, shop=shop, categories=categories)


# MODIFICA PRODOTTI -------------------------------------------------------------------------------------------------------------


@products_bp.route("/admin/cms/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    username = check_user_authentication()

    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash('Nessun negozio trovato per questo nome.', 'warning')
        return redirect(url_for('ui.homepage'))

    product = db.session.query(Product).filter_by(id=product_id, shop_id=shop.id).first()
    if not product:
        flash("Prodotto non trovato o non appartenente a questo negozio.", "danger")
        return redirect(url_for("products.render_products_table"))

    if request.method == "POST":
        try:
            product.name = request.form.get("name")
            product.slug = request.form.get("slug")
            product.short_description = request.form.get("short_description")
            product.price = request.form.get("price")
            product.discount_price = request.form.get("discount_price") or None
            product.description = request.form.get("description")
            product.is_active = request.form.get("is_active") == "true"
            product.is_digital = request.form.get("is_digital") == "true"
            product.sku = request.form.get("sku")
            product.ean_code = request.form.get("ean_code")

            db.session.commit()

            flash("Prodotto aggiornato con successo!", "success")
            return redirect(url_for("products.manage_product_images", product_id=product.id))
        except Exception as e:
            logging.error(f"❌ Errore durante l'aggiornamento del prodotto: {str(e)}")
            db.session.rollback()
            flash("Errore durante la modifica del prodotto.", "danger")

    categories = Category.query.all()
    return render_template("admin/cms/products/edit_product.html", title="Modifica Prodotto", product=product, username=username, shop=shop, categories=categories)

# GESTIONE IMMAGINI PRODOTTI -------------------------------------------------------------------------------------------------------------

@products_bp.route("/admin/cms/products/images/<int:product_id>", methods=["GET"])
def manage_product_images(product_id):
    username = check_user_authentication()

    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash('Nessun negozio trovato per questo nome.', 'warning')
        return redirect(url_for('ui.homepage'))

    product = db.session.query(Product).filter_by(id=product_id, shop_id=shop.id).first()
    if not product:
        flash("Prodotto non trovato o non appartenente a questo negozio.", "danger")
        return redirect(url_for("products.render_products_table"))

    images = product.images

    print(f"Immagini recuperate per il prodotto {product.id}: {[img.url for img in images]}")

    return render_template(
        "admin/cms/products/manage_images.html",
        title="Immagini Prodotto",
        product=product,
        images=images,
        username=username,
        shop=shop
    )


# AGGIUNTA IMMAGINI PRODOTTI -------------------------------------------------------------------------------------------------------------


@products_bp.route("/admin/cms/products/upload_image/<int:product_id>", methods=["POST"])
def upload_product_image(product_id):
    username = check_user_authentication()
    if not username:
        return jsonify({"success": False, "error": "Sessione scaduta."}), 401

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        return jsonify({"success": False, "error": "Negozio non trovato."}), 404

    product = db.session.query(Product).filter_by(id=product_id, shop_id=shop.id).first()
    if not product:
        return jsonify({"success": False, "error": "Prodotto non trovato."}), 404

    if 'images[]' not in request.files:
        return jsonify({"success": False, "error": "Nessun file inviato."}), 400

    files = request.files.getlist("images[]")
    uploaded_images = []

    for image in files:
        if image.filename == '':
            continue
        try:
            ext = image.filename.rsplit('.', 1)[1].lower()
            random_str = uuid.uuid4().hex
            filename = f"{shop.id}.{product.id}.{random_str}.{ext}"
            upload_folder = os.path.join("static", "uploads", "products")
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)

            compress_image(image, file_path)

            url = f"/static/uploads/products/{filename}"
            new_image = ProductImage(product_id=product.id, url=url)
            db.session.add(new_image)
            uploaded_images.append({
                "id": new_image.id,
                "url": url,
                "is_main": new_image.is_main
            })
        except Exception as e:
            logging.error(f"❌ Errore upload immagine: {str(e)}")

    db.session.commit()

    return jsonify({"success": True, "images": uploaded_images})

# GESTIONE VARIANTI PRODOTTO -------------------------------------------------------------------------------------------------------------

@products_bp.route("/admin/cms/products/variants/<int:product_id>", methods=["GET", "POST"])
def manage_product_variants(product_id):
    username = check_user_authentication()

    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        flash("Negozio non trovato", "danger")
        return redirect(url_for('ui.homepage'))

    product = db.session.query(Product).filter_by(id=product_id, shop_id=shop.id).first()
    if not product:
        flash("Prodotto non trovato", "danger")
        return redirect(url_for("products.render_products_table"))

    if request.method == "POST":
        try:
            sku = request.form.get("sku")
            name = request.form.get("name")
            ean_code = request.form.get("ean_code")
            price_modifier = request.form.get("price_modifier", 0)
            is_default = request.form.get("is_default") == "true"

            # Se viene impostata una variante come default, rimuovi il flag dalle altre
            if is_default:
                ProductVariant.query.filter_by(product_id=product.id).update({"is_default": False})

            new_variant = ProductVariant(
                product_id=product.id,
                name=name,
                sku=sku,
                ean_code=ean_code,
                price_modifier=price_modifier,
                is_default=is_default
            )
            db.session.add(new_variant)
            db.session.commit()
            flash("Variante aggiunta con successo!", "success")
            return redirect(url_for("products.manage_product_variants", product_id=product.id))
        except Exception as e:
            logging.error(f"❌ Errore durante la creazione variante: {str(e)}")
            db.session.rollback()
            flash("Errore durante la creazione della variante.", "danger")

    variants = ProductVariant.query.filter_by(product_id=product.id).all()
    return render_template(
        "admin/cms/products/manage_variants.html",
        title="Gestione Varianti",
        product=product,
        variants=variants,
        username=username,
        shop=shop
    )
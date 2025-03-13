from flask import Blueprint, render_template, request, jsonify, Response, flash, redirect, url_for
from models.database import db
from models.products import Product, ProductImage, create_new_product
from models.categories import Category
import os, uuid, csv, io, base64, logging
from helpers import check_user_authentication
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO)

# Blueprint
products_bp = Blueprint('products', __name__)

# 🔹 **Pagina di gestione prodotti con paginazione**
@products_bp.route('/admin/cms/pages/products')
def products():
    """
    Visualizza la lista dei prodotti con paginazione.
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, reindirizza alla login
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]
    
    # 🔄 Recupera il numero della pagina dalla query string (default = 1)
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Imposta il numero di prodotti per pagina

    try:
        # 📦 Recupera i prodotti con paginazione
        products_paginated = Product.query.filter_by(shop_name=shop_subdomain).paginate(page=page, per_page=per_page, error_out=False)
        categories = Category.query.filter_by(shop_name=shop_subdomain).all()

        if not products_paginated.items:
            flash("Nessun prodotto trovato. Aggiungi un nuovo prodotto per iniziare.", "info")

        if not categories:
            flash("Nessuna categoria disponibile. Crea una categoria per organizzare i prodotti.", "info")

        return render_template(
            'admin/cms/pages/products.html', 
            title='Products', 
            username=username, 
            categories=categories,
            products=products_paginated.items,  # 🔹 Solo i prodotti della pagina corrente
            pagination=products_paginated  # 🔹 Passiamo l'oggetto di paginazione al template
        )

    except SQLAlchemyError as e:
        logging.error(f"❌ Errore nel caricamento dei prodotti: {str(e)}")
        flash("Si è verificato un errore nel caricamento dei prodotti.", "danger")
        return render_template(
            'admin/cms/pages/error.html', 
            title="Errore", 
            message="Non è stato possibile caricare i prodotti."
        ), 500

# 🔹 **Gestione singolo prodotto (GET per visualizzare, POST per modificare)**
@products_bp.route('/admin/cms/pages/product/<int:product_id>', methods=['GET', 'POST'])
@products_bp.route('/admin/cms/pages/product', methods=['GET', 'POST'])
def manage_product(product_id=None):
    """
    Permette la gestione di un prodotto (creazione/modifica).
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, reindirizza alla login
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]

    if request.method == 'POST':
        try:
            data = request.form.to_dict()

            if product_id:
                product = Product.query.filter_by(id=product_id, shop_name=shop_subdomain).first()
                if not product:
                    return jsonify({'status': 'error', 'message': 'Product not found'}), 404
                
                # 🔄 Aggiorna dinamicamente i campi del prodotto
                for key, value in data.items():
                    setattr(product, key, value)
            else:
                new_product = Product(shop_name=shop_subdomain, **data)
                db.session.add(new_product)

            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Product saved successfully'})

        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"❌ Error managing product: {str(e)}")
            return jsonify({'status': 'error', 'message': 'An error occurred'}), 500

    try:
        product = Product.query.filter_by(id=product_id, shop_name=shop_subdomain).first() if product_id else None
        images = product.images if product else []
        categories = Category.query.filter_by(shop_name=shop_subdomain).all()

        if product_id and not product:
            flash("Il prodotto specificato non è stato trovato.", "warning")
            return redirect(url_for('products'))

        return render_template(
            'admin/cms/pages/manage_product.html',
            title='Manage Product',
            username=username,
            product=product,
            images=images,
            categories=categories,
            shop_subdomain=shop_subdomain
        )

    except SQLAlchemyError as e:
        logging.error(f"❌ Errore nel caricamento del prodotto: {str(e)}")
        flash("Si è verificato un errore nel caricamento del prodotto.", "danger")
        return render_template(
            'admin/cms/pages/error.html',
            title="Errore",
            message="Non è stato possibile caricare il prodotto."
        ), 500
    
@products_bp.route('/admin/cms/export_products', methods=['GET'])
def export_products():
    shop_name = request.host.split('.')[0]  # Sottodominio per identificare il negozio

    try:
        # Recupera tutti i prodotti per il negozio specifico
        products = db.session.query(Product).filter_by(shop_name=shop_name).all()

        if not products:
            return jsonify({'success': False, 'message': 'No products found for this shop.'}), 404

        # Creazione del file CSV in memoria
        output = io.StringIO()
        writer = csv.writer(output)

        # Intestazioni
        headers = [
            "ID", "Name", "Description", "Short Description", "Price", "Discount Price",
            "Stock", "SKU", "Category", "Brand", "Weight", "Dimensions", "Color",
            "Material", "Image URL", "Slug", "Is Active", "Created At", "Updated At"
        ]
        writer.writerow(headers)

        # Righe dei dati
        for product in products:
            writer.writerow([
                product.id,
                product.name,
                product.description,
                product.short_description,
                product.price,
                product.discount_price,
                product.stock_quantity,
                product.sku,
                product.category_id or '',
                product.brand_id or '',
                product.weight,
                product.dimensions,
                product.color,
                product.material,
                product.image_url,
                product.slug,
                'Yes' if product.is_active else 'No',
                product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                product.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        # Generazione del file CSV
        output.seek(0)
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=products.csv"}
        )

    except SQLAlchemyError as e:
        logging.error(f"❌ Database error: {str(e)}")
        return jsonify({'success': False, 'message': 'Database error occurred.'}), 500
    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
    
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
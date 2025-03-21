from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from models.database import db  # Database SQLAlchemy
from models.collections import Collection, CollectionProduct, CollectionImage  # Modello delle collezioni
from models.products import Product  # Modello dei prodotti
from helpers import check_user_authentication
import os, logging, uuid, re, base64

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione delle collezioni
collections_bp = Blueprint('collections' , __name__)

# 📌 Route per visualizzare la pagina delle collezioni con paginazione
@collections_bp.route('/admin/cms/pages/collections')
def collections():
    username = check_user_authentication()
    
    if not username:  # ✅ Se l'utente non è autenticato, lo reindirizziamo correttamente
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))
    
    shop_name = request.host.split('.')[0]  # ✅ Questa riga era indentata male

    page = request.args.get('page', 1, type=int)  # ✅ Ottieni il numero della pagina dalla query string
    per_page = 8  # ✅ Numero di collezioni per pagina

    pagination = Collection.query.filter_by(shop_name=shop_name).paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'admin/cms/pages/collections.html', 
        title='Collections', 
        username=username, 
        collections=pagination.items,  # ✅ Elementi della pagina corrente
        pagination=pagination  # ✅ Oggetto paginazione
    )


# 📌 Route per visualizzare/modificare una collezione specifica
@collections_bp.route('/admin/cms/pages/collection/<int:collection_id>', methods=['GET', 'POST'])
@collections_bp.route('/admin/cms/pages/collection', methods=['GET', 'POST'])
def manage_collection(collection_id=None):
    """
    API per gestire (visualizzare/modificare) una collezione specifica.
    """
    username = check_user_authentication()
    
    if not username:  # ✅ Se la sessione è scaduta, reindirizza subito
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    try:
        if request.method == 'POST':
            data = request.get_json()
            if collection_id:  # Se la collezione esiste, aggiorniamo
                collection = Collection.query.get(collection_id)
                if not collection:
                    return jsonify({'status': 'error', 'message': 'Collection not found'}), 404

                # Aggiorna solo i campi forniti nella richiesta
                collection.name = data.get('name', collection.name)
                collection.description = data.get('description', collection.description)
                collection.image_url = data.get('image_url', collection.image_url)
                collection.is_active = data.get('is_active', collection.is_active)

                db.session.commit()
                return jsonify({'status': 'success', 'message': 'Collection updated successfully.'})

            else:  # Creazione nuova collezione
                new_collection = Collection(
                    name=data.get('name', 'New Collection'),
                    slug=f"{re.sub(r'[^\w\s-]', '', data.get('name', 'New Collection')).replace(' ', '-').lower()}-{uuid.uuid4().hex[:8]}",
                    description=data.get('description', 'Detailed description'),
                    image_url=data.get('image_url', '/static/images/default.png'),
                    is_active=data.get('is_active', False),
                    shop_name=request.host.split('.')[0]
                )

                db.session.add(new_collection)
                db.session.commit()

                return jsonify({'status': 'success', 'message': 'Collection created successfully.', 'collection_id': new_collection.id})

        # Se GET, restituiamo i dettagli della collezione
        collection = Collection.query.get(collection_id) if collection_id else None

        return render_template(
            'admin/cms/pages/manage_collection.html',
            title='Manage Collection',
            username=username,
            collection=collection,
            shop_subdomain=request.host.split('.')[0]  # Passa il sottodominio al template
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error managing collection: {e}")
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'}), 500

# 📌 Route per la gestione della lista delle collezioni
@collections_bp.route('/admin/cms/pages/collection-list/<int:collection_id>', methods=['GET', 'POST'])
@collections_bp.route('/admin/cms/pages/collection-list/', methods=['GET', 'POST'])
def manage_collection_list(collection_id=None):
    """
    Visualizza e gestisce una lista di collezioni con i prodotti associati.
    """
    username = check_user_authentication()
    
    if not username:  # ✅ Se la sessione è scaduta, reindirizza alla login
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_name = request.host.split('.')[0]  # ✅ Recupera il nome del negozio solo se autenticato

    try:
        collection = Collection.query.filter_by(id=collection_id, shop_name=shop_name).first() if collection_id else None

        # Recupera tutti i prodotti associati alla collezione
        products_in_collection = (
            db.session.query(Product)
            .join(CollectionProduct, CollectionProduct.product_id == Product.id)
            .filter(CollectionProduct.collection_id == collection_id)
            .all()
            if collection_id
            else []
        )

        return render_template(
            'admin/cms/pages/manage_collection_list.html',
            title='Manage Collection List',
            username=username,
            collection=collection,
            products=products_in_collection,  # Passa i dettagli completi dei prodotti al template
            shop_subdomain=shop_name
        )

    except Exception as e:
        logging.error(f"Error retrieving collection list: {e}")
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'}), 500
    
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
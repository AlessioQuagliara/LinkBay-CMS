from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.database import db  # Importa il database SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from models.shippingmethods import ShippingMethod  # Importa il modello della tabella
from helpers import check_user_authentication
import logging

logging.basicConfig(level=logging.INFO)

# 📌 Blueprint per la gestione dei metodi di spedizione
shipping_methods_bp = Blueprint('shipping_methods' , __name__)

# 🔹 **Pagina di gestione dei metodi di spedizione**
@shipping_methods_bp.route('/admin/cms/pages/shipping-methods')
def shipping_methods():
    """
    Visualizza i metodi di spedizione configurati per il negozio corrente.
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, reindirizza alla login
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_name = request.host.split('.')[0]  # Ottieni il nome del negozio dal sottodominio

    try:
        # Recupera tutti i metodi di spedizione per lo shop
        methods_list = ShippingMethod.query.filter_by(shop_name=shop_name).all()

        if not methods_list:
            flash("Nessun metodo di spedizione configurato. Aggiungine uno nelle impostazioni.", "info")

        return render_template(
            'admin/cms/pages/shipping.html',
            title='Shipping Methods',
            username=username,
            methods=methods_list
        )

    except SQLAlchemyError as e:
        logging.error(f"❌ Errore nel caricamento dei metodi di spedizione: {str(e)}")
        flash("Si è verificato un errore nel caricamento dei metodi di spedizione.", "danger")
        return render_template(
            'admin/cms/pages/error.html',
            title="Errore",
            message="Non è stato possibile caricare i metodi di spedizione."
        ), 500


# 🔹 **Creazione di un nuovo metodo di spedizione**
@shipping_methods_bp.route('/admin/cms/create_shipping_method', methods=['POST'])
def create_shipping_method():
    try:
        data = request.get_json()
        shop_name = request.host.split('.')[0]  # Identifica il negozio

        # Creazione del nuovo metodo di spedizione
        new_method = ShippingMethod(
            shop_name=shop_name,
            name=data.get("name", "Standard Shipping"),
            description=data.get("description", "Default shipping method"),
            country=data.get("country", "Worldwide"),
            region=data.get("region"),
            cost=float(data.get("cost", 0.0)),
            estimated_delivery_time=data.get("estimated_delivery_time", "5-7 business days"),
            is_active=data.get("is_active", True)
        )

        db.session.add(new_method)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Shipping method created successfully.', 'method_id': new_method.id})
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Error creating shipping method: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500


# 🔹 **Eliminazione di uno o più metodi di spedizione**
@shipping_methods_bp.route('/admin/cms/delete_shippings', methods=['POST'])
def delete_shippings():
    try:
        data = request.get_json()
        shipping_ids = data.get('shipping_ids')

        if not shipping_ids or not isinstance(shipping_ids, list):
            return jsonify({'success': False, 'message': 'No shipping IDs provided or invalid format.'}), 400

        # Eliminazione multipla con SQLAlchemy ORM
        db.session.query(ShippingMethod).filter(ShippingMethod.id.in_(shipping_ids)).delete(synchronize_session=False)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Selected shipping methods deleted successfully.'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Error deleting shipping methods: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500


# 🔹 **Gestione di un singolo metodo di spedizione (Creazione e Modifica)**
@shipping_methods_bp.route('/admin/cms/pages/shipping-method/<int:method_id>', methods=['GET', 'POST'])
@shipping_methods_bp.route('/admin/cms/pages/shipping-method', methods=['GET', 'POST'])
def manage_shipping_method(method_id=None):
    """
    Permette la gestione di un metodo di spedizione (creazione/modifica).
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, reindirizza alla login
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]  # Identifica il negozio

    if request.method == 'POST':
        try:
            data = request.get_json()

            if not data:
                return jsonify({'status': 'error', 'message': 'Invalid data format.'}), 400

            if method_id:
                # Modifica del metodo di spedizione esistente
                shipping_method = ShippingMethod.query.filter_by(id=method_id, shop_name=shop_subdomain).first()
                if not shipping_method:
                    return jsonify({'status': 'error', 'message': 'Shipping method not found'}), 404

                # 🔄 Aggiorna dinamicamente i campi del metodo di spedizione
                for key, value in data.items():
                    setattr(shipping_method, key, value)
            else:
                # Creazione di un nuovo metodo di spedizione
                new_method = ShippingMethod(shop_name=shop_subdomain, **data)
                db.session.add(new_method)

            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Shipping method saved successfully'})

        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"❌ Error managing shipping method: {str(e)}")
            return jsonify({'status': 'error', 'message': 'An error occurred.'}), 500

    try:
        # Recupera il metodo di spedizione se esiste
        shipping_method = ShippingMethod.query.filter_by(id=method_id, shop_name=shop_subdomain).first() if method_id else None

        if method_id and not shipping_method:
            flash("Il metodo di spedizione specificato non è stato trovato.", "warning")
            return redirect(url_for('shipping_methods'))

        return render_template(
            'admin/cms/pages/manage_shipping.html',
            title='Manage Shipping Method',
            username=username,
            method=shipping_method,
            shop_subdomain=shop_subdomain
        )

    except SQLAlchemyError as e:
        logging.error(f"❌ Errore nel caricamento del metodo di spedizione: {str(e)}")
        flash("Si è verificato un errore nel caricamento del metodo di spedizione.", "danger")
        return render_template(
            'admin/cms/pages/error.html',
            title="Errore",
            message="Non è stato possibile caricare il metodo di spedizione."
        ), 500


# 🔹 **Aggiornamento di un metodo di spedizione**
@shipping_methods_bp.route('/admin/cms/update_shipping_method', methods=['POST'])
def update_shipping_method():
    username = check_user_authentication()
    if isinstance(username, str):
        try:
            form_data = request.form
            shipping_id = form_data.get('id')
            shop_name = request.host.split('.')[0]  # Identifica il negozio

            if not shipping_id:
                return jsonify({'success': False, 'message': 'Shipping ID is required.'}), 400

            # Recupera il metodo di spedizione esistente
            shipping_method = ShippingMethod.query.filter_by(id=shipping_id, shop_name=shop_name).first()
            if not shipping_method:
                return jsonify({'success': False, 'message': 'Shipping method not found.'}), 404

            # Aggiorna i campi del metodo di spedizione
            shipping_method.name = form_data.get('name')
            shipping_method.description = form_data.get('description')
            shipping_method.country = form_data.get('country')
            shipping_method.region = form_data.get('region')
            shipping_method.cost = float(form_data.get('cost', 0))
            shipping_method.estimated_delivery_time = form_data.get('estimated_delivery_time')
            shipping_method.is_active = form_data.get('is_active') == '1'  # Converti a boolean

            db.session.commit()

            return jsonify({'success': True, 'message': 'Shipping method updated successfully.'})
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"❌ Error updating shipping method: {str(e)}")
            return jsonify({'success': False, 'message': 'An error occurred.'}), 500
    return username
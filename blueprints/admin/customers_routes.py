from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from models.database import db
from models.customers import Customer  # Importa il modello SQLAlchemy
from helpers import check_user_authentication
import uuid
import logging

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione dei clienti
customers_bp = Blueprint('customers', __name__)

# 📌 Route per visualizzare i clienti nel pannello admin
@customers_bp.route('/admin/cms/pages/customers', methods=['GET'])
def customers():
    """
    Mostra la lista dei clienti del negozio con paginazione e ricerca.
    """
    username = check_user_authentication()

    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_name = request.host.split('.')[0]  # Nome del negozio

    # Recupera i parametri di ricerca
    search_query = request.args.get('search', type=str, default='')

    # Recupera il numero della pagina
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Numero di clienti per pagina

    try:
        # Costruisce la query con la ricerca
        query = Customer.query.filter(Customer.shop_name == shop_name)

        if search_query:
            query = query.filter(
                (Customer.name.ilike(f"%{search_query}%")) | 
                (Customer.email.ilike(f"%{search_query}%"))
            )

        # Conta il totale dei clienti filtrati
        total_customers = query.count()

        # Applica la paginazione
        customers_paginated = query.order_by(Customer.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

        # Creiamo un oggetto per la paginazione
        class Pagination:
            def __init__(self, total, per_page, page):
                self.total = total
                self.per_page = per_page
                self.page = page
                self.pages = (total + per_page - 1) // per_page
                self.has_prev = page > 1
                self.has_next = page < self.pages
                self.prev_num = page - 1 if self.has_prev else None
                self.next_num = page + 1 if self.has_next else None

            def iter_pages(self):
                return range(1, self.pages + 1)

        pagination = Pagination(total_customers, per_page, page)

        return render_template(
            'admin/cms/pages/customers.html',
            title='Customers',
            username=username,
            customers=customers_paginated,
            pagination=pagination,
            search_query=search_query
        )

    except Exception as e:
        logging.error(f"❌ Errore nel caricamento dei clienti: {str(e)}")
        flash("Si è verificato un errore nel caricamento dei clienti.", "danger")
        return render_template(
            'admin/cms/pages/error.html',
            title="Errore",
            message="Non è stato possibile caricare i clienti."
        ), 500


# 📌 Route per gestire un cliente (visualizzazione o modifica)
@customers_bp.route('/admin/cms/pages/customer/<int:customer_id>', methods=['GET', 'POST'])
def manage_customer(customer_id):
    """
    Modifica o visualizza i dettagli di un cliente.
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, reindirizza alla login
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_name = request.host.split('.')[0]  # ✅ Recupera il nome del negozio solo se autenticato
    
    # Recupera il cliente dal database
    customer = Customer.query.filter_by(id=customer_id, shop_name=shop_name).first()

    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404

    if request.method == 'POST':
        try:
            data = request.get_json()
            for key, value in data.items():
                setattr(customer, key, value)  # Aggiorna i campi dinamicamente

            db.session.commit()
            return jsonify({'success': True, 'message': 'Customer updated successfully'})

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating customer: {e}")
            return jsonify({'success': False, 'message': 'An error occurred'}), 500

    return render_template(
        'admin/cms/pages/manage_customer.html',
        title='Manage Customer',
        username=username,
        customer=customer
    )

# 📌 Route per aggiornare un cliente
@customers_bp.route('/api/update_customer', methods=['POST'])
def update_customer():
    """
    Aggiorna le informazioni di un cliente esistente.
    """
    try:
        data = request.form.to_dict()
        customer_id = data.get('id')

        if not customer_id or not customer_id.isdigit():
            return jsonify({'success': False, 'message': 'Invalid or missing Customer ID.'}), 400

        shop_name = request.host.split('.')[0]

        # Recupera il cliente
        customer = Customer.query.filter_by(id=int(customer_id), shop_name=shop_name).first()

        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found'}), 404

        # Aggiorna i dati
        for key, value in data.items():
            setattr(customer, key, value)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Customer updated successfully'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating customer: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred'}), 500

# 📌 Route per eliminare più clienti
@customers_bp.route('/admin/cms/delete_customers', methods=['POST'])
def delete_customers():
    """
    Elimina uno o più clienti dal database.
    """
    try:
        data = request.get_json()
        customer_ids = data.get('customer_ids')

        if not customer_ids:
            return jsonify({'success': False, 'message': 'No customer IDs provided.'}), 400

        shop_name = request.host.split('.')[0]

        # Elimina i clienti specificati
        customers_deleted = Customer.query.filter(Customer.id.in_(customer_ids), Customer.shop_name == shop_name).delete(synchronize_session=False)
        db.session.commit()

        if customers_deleted > 0:
            return jsonify({'success': True, 'message': 'Selected customers deleted successfully.'})
        else:
            return jsonify({'success': False, 'message': 'No customers were deleted.'}), 500

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting customers: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500

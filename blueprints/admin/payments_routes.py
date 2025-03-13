from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models.database import db
from models.payments import Payment
from models.payment_methods import PaymentMethod
from helpers import check_user_authentication
import logging
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO)

payments_bp = Blueprint('payments', __name__)

# 🔹 **Renderizzazione della pagina dei metodi di pagamento**
@payments_bp.route('/admin/cms/pages/payments', methods=['GET'])
def payments():
    """
    Renderizza la pagina dei metodi di pagamento.
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, reindirizza alla login
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_name = request.host.split('.')[0]

    try:
        active_methods = PaymentMethod.query.filter_by(shop_name=shop_name).all()

        # Lista dei metodi attivi in formato dizionario
        active_methods_dict = {method.method_name: method.to_dict() for method in active_methods} if active_methods else {}

        if not active_methods:
            flash("Nessun metodo di pagamento attivo. Aggiungine uno nelle impostazioni.", "info")

        return render_template(
            'admin/cms/pages/payments.html',
            active_methods=active_methods_dict,
            shop_name=shop_name,
            title='Payments',
            username=username  # ✅ Passiamo il nome utente al template
        )

    except SQLAlchemyError as e:
        logging.error(f"❌ Errore nel rendering della pagina dei pagamenti: {str(e)}")
        flash("Si è verificato un errore nel caricamento dei metodi di pagamento.", "danger")
        return render_template('admin/cms/pages/error.html', title='Error 500', message="Unable to load payment methods"), 500

# 🔹 **Renderizzazione della configurazione di un metodo di pagamento**
@payments_bp.route('/admin/cms/pages/manage_payments/<method_name>', methods=['GET'])
def configure_payment_method(method_name):
    """
    Permette la configurazione di un metodo di pagamento specifico.
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, reindirizza alla login
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_name = request.host.split('.')[0]

    try:
        method = PaymentMethod.query.filter_by(shop_name=shop_name, method_name=method_name).first()

        if not method:
            flash(f"Il metodo di pagamento '{method_name}' non è stato trovato. Puoi configurarne uno nuovo.", "info")

        return render_template(
            'admin/cms/pages/manage_payments.html',
            shop_name=shop_name,
            method=method.to_dict() if method else {"method_name": method_name},  # ✅ Assicura che il template non riceva un valore nullo
            title="Manage Payment",
            username=username  # ✅ Passiamo il nome utente al template
        )

    except SQLAlchemyError as e:
        logging.error(f"❌ Errore nella configurazione del metodo di pagamento: {str(e)}")
        flash("Si è verificato un errore nel caricamento della configurazione del metodo di pagamento.", "danger")
        return render_template(
            'admin/cms/pages/error.html',
            title='Error 500',
            message="Unable to load payment method configuration"
        ), 500
    

# 🔹 **Aggiornamento di un metodo di pagamento**
@payments_bp.route('/admin/cms/pages/update_payment_method', methods=['POST'])
def update_payment_method():
    try:
        data = request.form.to_dict()
        method_name = data.get('method_name')

        if not method_name:
            return jsonify({'success': False, 'message': 'Invalid or missing method_name.'}), 400

        shop_name = request.host.split('.')[0]

        existing_method = PaymentMethod.query.filter_by(shop_name=shop_name, method_name=method_name).first()

        if not existing_method:
            return jsonify({'success': False, 'message': f'Payment method "{method_name}" not found.'}), 404

        # Aggiorna i dati del metodo di pagamento
        existing_method.api_key = data.get('api_key')
        existing_method.api_secret = data.get('api_secret')
        existing_method.extra_info = data.get('extra_info')

        db.session.commit()
        return jsonify({'success': True, 'message': f'Payment method "{method_name}" updated successfully!'})

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento del metodo di pagamento: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
    

# 🔹 **Restituisce i metodi di pagamento configurati per un negozio**
@payments_bp.route('/payment-methods/<shop_name>', methods=['GET'])
def get_payment_methods(shop_name):
    try:
        methods = PaymentMethod.query.filter_by(shop_name=shop_name).all()
        return jsonify({'methods': [method.method_name for method in methods]})
    
    except SQLAlchemyError as e:
        logging.error(f"❌ Errore nel recupero dei metodi di pagamento: {str(e)}")
        return jsonify({'success': False, 'error': 'Errore interno del server'}), 500

# 🔹 **Restituisce i metodi di pagamento attivi per lo shop**
@payments_bp.route('/admin/cms/pages/payments/get_active_methods', methods=['GET'])
def get_active_payment_methods():
    shop_name = request.host.split('.')[0]

    try:
        active_methods = PaymentMethod.query.filter_by(shop_name=shop_name).all()

        methods_info = [
            {
                'method_name': method.method_name,
                'is_active': True,
                'api_key': method.api_key,
                'api_secret': method.api_secret,
                'extra_info': method.extra_info,
            }
            for method in active_methods
        ]

        return jsonify({'success': True, 'methods': methods_info}), 200

    except SQLAlchemyError as e:
        logging.error(f"❌ Errore nel recupero dei metodi di pagamento attivi: {str(e)}")
        return jsonify({'success': False, 'error': 'Errore interno del server'}), 500

# 🔹 **Aggiunge un nuovo metodo di pagamento**
@payments_bp.route('/admin/cms/pages/add_payment_method', methods=['POST'])
def add_payment_method():
    try:
        data = request.json
        method_name = data.get('method_name')
        shop_name = data.get('shop_name')

        if not method_name or not shop_name:
            return jsonify({'success': False, 'message': 'Invalid or missing data.'}), 400

        existing_method = PaymentMethod.query.filter_by(shop_name=shop_name, method_name=method_name).first()

        if existing_method:
            return jsonify({'success': False, 'message': f'{method_name} is already configured.'}), 400

        # Creazione del nuovo metodo di pagamento
        new_method = PaymentMethod(
            shop_name=shop_name,
            method_name=method_name,
            api_key='',
            api_secret='',
            extra_info=''
        )

        db.session.add(new_method)
        db.session.commit()

        return jsonify({'success': True, 'message': f'{method_name} configured successfully.'})

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiunta del metodo di pagamento: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
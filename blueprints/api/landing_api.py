from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models.database import db
from models.shoplist import ShopList
from models.user import User 
from models.stores_info import StoreInfo
from models.userstoreaccess import UserStoreAccess
from models.orders import Order
from models.support_tickets import SupportTicket
from sqlalchemy import func
from flask import session
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_fields(*fields):
    return all(field for field in fields)

landing_api = Blueprint('landingApi', __name__, url_prefix='/api/')

@landing_api.route('/create_shop', methods=['POST'])
def create_shop():
    shop_name = request.form.get('shop_name', '').strip().lower()
    shop_type = request.form.get('themeOptions', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()

    if not validate_fields(shop_name, shop_type, email, password):
        return jsonify(success=False, message="Tutti i campi sono obbligatori"), 400

    logger.info(f"🛠️ Tentativo di creazione shop: '{shop_name}' per email: {email}")

    if User.query.filter_by(email=email).first():
        logger.warning(f"⛔ Email già registrata: {email}")
        return jsonify(success=False, message="Email già registrata"), 409

    if ShopList.query.filter_by(shop_name=shop_name).first():
        logger.warning(f"⛔ Nome shop già in uso: {shop_name}")
        return jsonify(success=False, message="Nome negozio già utilizzato"), 409

    try:
        generated_name = f"new_user_{str(int.from_bytes(os.urandom(3), 'big'))}"
        random_cognome = "default"
        random_telefono = f"+39{str(int.from_bytes(os.urandom(3), 'big'))[:9]}"
        is_female = generated_name.endswith(('0', '2', '4', '6', '8'))
        profilo_foto = (
            "https://www.svgrepo.com/show/382097/female-avatar-girl-face-woman-user-9.svg"
            if is_female else
            "https://www.svgrepo.com/show/382103/male-avatar-boy-face-man-user-2.svg"
        )
        new_user = User(
            email=email,
            password=generate_password_hash(password),
            nome=generated_name,
            cognome=random_cognome,
            telefono=random_telefono,
            profilo_foto=profilo_foto
        )
        db.session.add(new_user)
        db.session.flush()

        domain = f"{shop_name}.yoursite-linkbay-cms.com"

        new_shop = ShopList(
            shop_name=shop_name,
            shop_type=shop_type,
            domain=domain,
            user_id=new_user.id
        )
        db.session.add(new_shop)
        db.session.flush()

        # 🔐 Collega come ADMIN del negozio
        access = UserStoreAccess(
            user_id=new_user.id,
            shop_id=new_shop.id,
            access_level='admin'
        )
        db.session.add(access)

        db.session.commit()

        logger.info(f"✅ Shop '{shop_name}' creato con ID utente: {new_user.id}")
        return jsonify(success=True, message="Negozio creato con successo!")
    except Exception as e:
        db.session.rollback()
        logger.error(f"🔥 Errore durante la creazione dello shop: {e}")
        return jsonify(success=False, message="Errore nella creazione del negozio. Riprova più tardi."), 500

@landing_api.route('/create_shop_access', methods=['POST'])
def create_shop_access():

    shop_name = request.form.get('shop_name', '').strip().lower()
    shop_type = request.form.get('themeOptions', '').strip()

    user_id = session.get('user_id')
    if not user_id or not validate_fields(shop_name, shop_type):
        return jsonify(success=False, message="Dati mancanti o utente non autenticato"), 400

    logger.info(f"🛠️ Creazione shop access per utente ID {user_id} con nome shop: '{shop_name}'")

    if ShopList.query.filter_by(shop_name=shop_name).first():
        return jsonify(success=False, message="Nome negozio già in uso"), 409

    try:
        domain = f"{shop_name}.yoursite-linkbay-cms.com"

        new_shop = ShopList(
            shop_name=shop_name,
            shop_type=shop_type,
            domain=domain,
            user_id=user_id
        )
        db.session.add(new_shop)
        db.session.flush()

        access = UserStoreAccess(
            user_id=user_id,
            shop_id=new_shop.id,
            access_level='admin'  # livello forzato a 'admin'
        )
        db.session.add(access)
        logger.warning(f"👀 Access level impostato: {access.access_level}")
        db.session.commit()
        db.session.refresh(access)
        logger.warning(f"🧪 Access level da DB dopo commit: {access.access_level}")

        logger.info(f"✅ Nuovo shop '{shop_name}' creato da utente ID {user_id}")
        return jsonify(success=True, message="Negozio creato con successo!")
    except Exception as e:
        db.session.rollback()
        logger.error(f"🔥 Errore durante la creazione shop_access: {e}")
        return jsonify(success=False, message="Errore durante la creazione del negozio"), 500

@landing_api.route('/check_email', methods=['GET'])
def check_email():
    email = request.args.get('email', '').strip().lower()
    
    if not email:
        return jsonify(status='error', message='Email non fornita'), 400

    exists = User.query.filter_by(email=email).first() is not None
    return jsonify(status='exists' if exists else 'available')

@landing_api.route('/check_shopname', methods=['GET'])
def check_shopname():
    shop_name = request.args.get('shop_name', '').strip().lower()

    if not shop_name:
        return jsonify(status='error', message='Nome negozio non fornito'), 400

    exists = ShopList.query.filter_by(shop_name=shop_name).first() is not None
    return jsonify(status='exists' if exists else 'available')

@landing_api.route('/delete_shop', methods=['DELETE'])
def delete_shop():
    try:
        data = request.get_json()
        shop_id = data.get('shop_id')

        if not shop_id:
            return jsonify(success=False, message="ID negozio mancante"), 400

        shop = ShopList.query.get(shop_id)

        if not shop:
            return jsonify(success=False, message="Negozio non trovato"), 404

        # Elimina accessi utente associati al negozio
        from models.userstoreaccess import UserStoreAccess
        UserStoreAccess.query.filter_by(shop_id=shop_id).delete()

        # Elimina le impostazioni web associate
        from models.websettings import WebSettings
        WebSettings.query.filter_by(shop_name=shop.shop_name).delete()

        # Elimina le informazioni dello store
        from models.stores_info import StoreInfo
        StoreInfo.query.filter_by(shop_name=shop.shop_name).delete()

        # Elimina eventuali domini associati
        from models.domain import Domain
        Domain.query.filter_by(shop_id=shop.id).delete()

        # Ora elimina il negozio
        db.session.delete(shop)
        db.session.commit()
        logger.info(f"🗑️ Negozio con ID {shop_id} eliminato correttamente.")
        return jsonify(success=True, message="Negozio eliminato con successo!")
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Errore durante l'eliminazione del negozio: {e}")
        return jsonify(success=False, message="Errore durante l'eliminazione del negozio."), 500

@landing_api.route('/user_shops_sales', methods=['GET'])
def get_user_shops_sales():
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    user_id = session['user_id']

    # Ricava gli ID dei negozi in cui l'utente è admin
    admin_access = UserStoreAccess.query.filter_by(user_id=user_id, access_level='admin').all()
    shop_ids = [entry.shop_id for entry in admin_access]

    if not shop_ids:
        return jsonify(success=True, data=[])

    shops = ShopList.query.filter(ShopList.id.in_(shop_ids)).all()
    results = []

    for shop in shops:
        completed_orders = Order.query.filter_by(shop_name=shop.shop_name, status='Complete').all()
        total_revenue = sum(order.total_amount for order in completed_orders)
        total_orders = len(completed_orders)

        results.append({
            'shop_id': shop.id,
            'shop_name': shop.shop_name,
            'shop_type': shop.shop_type,
            'total_orders': total_orders,
            'total_revenue': total_revenue
        })

    return jsonify(success=True, data=results)

@landing_api.route('/create_ticket', methods=['POST'])
def create_ticket():
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    user_id = session.get('user_id')
    data = request.get_json() or {}
    shop_name = data.get('shop_name', '').strip()
    title = data.get('title', '').strip()
    category = data.get('category', '').strip()
    message = data.get('message', '').strip()
    priority = data.get('priority', 'normal').strip()

    if not validate_fields(shop_name, title, category, message):
        return jsonify(success=False, message="Tutti i campi sono obbligatori"), 400

    # Controlla se lo shop esiste ed è associato all'utente
    shop = ShopList.query.filter_by(shop_name=shop_name).first()
    if not shop:
        return jsonify(success=False, message="Negozio non trovato"), 404

    try:
        new_ticket = SupportTicket(
            shop_name=shop_name,
            user_id=user_id,
            title=title,
            category=category,
            message=message,
            priority=priority
        )
        db.session.add(new_ticket)
        db.session.commit()
        return jsonify(success=True, message="Ticket creato con successo")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Errore durante la creazione del ticket: {e}")
        return jsonify(success=False, message="Errore durante la creazione del ticket"), 500

@landing_api.route('/my_tickets', methods=['GET'])
def get_my_tickets():
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    user_id = session['user_id']
    tickets = SupportTicket.query.filter_by(user_id=user_id).order_by(SupportTicket.id.desc()).all()
    results = [{
        'id': ticket.id,
        'shop_name': ticket.shop_name,
        'title': ticket.title,
        'category': ticket.category,
        'message': ticket.message,
        'priority': ticket.priority,
        'status': ticket.status,
        'created_at': ticket.created_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.created_at else None
    } for ticket in tickets]

    return jsonify(success=True, data=results)

@landing_api.route('/delete_ticket/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    try:
        user_id = session['user_id']
        ticket = SupportTicket.query.get(ticket_id)

        if not ticket:
            return jsonify(success=False, message="Ticket non trovato"), 404

        if ticket.user_id != user_id:
            return jsonify(success=False, message="Non sei autorizzato a cancellare questo ticket"), 403

        # Cancella prima i messaggi collegati
        from models.ticket_messages import TicketMessage
        TicketMessage.query.filter_by(ticket_id=ticket_id).delete()

        # Ora puoi cancellare il ticket
        db.session.delete(ticket)
        db.session.commit()

        logger.info(f"🗑️ Ticket {ticket_id} eliminato dall'utente {user_id}")
        return jsonify(success=True, message="Ticket eliminato con successo.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Errore durante l'eliminazione del ticket: {e}")
        return jsonify(success=False, message="Errore durante l'eliminazione del ticket"), 500

@landing_api.route('/ticket_messages/<int:ticket_id>', methods=['GET'])
def get_ticket_messages(ticket_id):
    from models.ticket_messages import TicketMessage

    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    try:
        messages = TicketMessage.query.filter_by(ticket_id=ticket_id).order_by(TicketMessage.created_at.asc()).all()
        results = [{
            'id': m.id,
            'message': m.message,
            'sender_id': m.sender_id,
            'sender_role': m.sender_role,
            'created_at': m.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for m in messages]

        return jsonify(success=True, data=results)
    except Exception as e:
        logger.error(f"Errore nel recupero dei messaggi per il ticket {ticket_id}: {e}")
        return jsonify(success=False, message="Errore durante il recupero dei messaggi"), 500

@landing_api.route('/ticket_messages/<int:ticket_id>', methods=['POST'])
def post_ticket_message(ticket_id):
    from models.ticket_messages import TicketMessage

    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    data = request.get_json() or {}
    message = data.get('message', '').strip()

    if not message:
        return jsonify(success=False, message="Il messaggio non può essere vuoto"), 400

    try:
        new_msg = TicketMessage(
            ticket_id=ticket_id,
            sender_id=session['user_id'],
            sender_role='user',
            message=message
        )
        db.session.add(new_msg)
        db.session.commit()
        return jsonify(success=True, message="Messaggio inviato con successo")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Errore nell'invio del messaggio per il ticket {ticket_id}: {e}")
        return jsonify(success=False, message="Errore durante l'invio del messaggio"), 500

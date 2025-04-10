from flask import Blueprint, request, jsonify, redirect, current_app, flash, url_for
from werkzeug.security import generate_password_hash
from models.database import db
from models.shoplist import ShopList
from models.user import User 
from models.stores_info import StoreInfo
from models.userstoreaccess import UserStoreAccess
from models.orders import Order
from models.message import ChatMessage
from models.cmsaddon import CMSAddon
from models.support_tickets import SupportTicket
from models.storepayment import StorePayment
from models.subscription import Subscription
from public.stripe_connect import create_connect_account
from sqlalchemy import func
from flask import session
import stripe
import logging
import os
from datetime import datetime, timedelta

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

        freemium = Subscription(
            shop_name=new_shop.shop_name,
            user_id=new_user.id,
            plan_name='Freemium',
            price=0.00,
            currency='EUR',
            features='{"max_products":50}',
            limits='{"max_visits":1000}',
            status='active',
            payment_gateway='free',
            payment_reference=None,
            renewal_date=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(freemium)
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

        freemium = Subscription(
            shop_name=new_shop.shop_name,
            user_id=user_id,
            plan_name='Freemium',
            price=0.00,
            currency='EUR',
            features='{"max_products":50}',
            limits='{"max_visits":1000}',
            status='active',
            payment_gateway='free',
            payment_reference=None,
            renewal_date=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(freemium)
        db.session.commit()

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
        from models.page import Page
        Page.query.filter_by(shop_name=shop.shop_name).delete()
        from models.domain import Domain
        Domain.query.filter_by(shop_id=shop.id).delete()

        # Elimina la subscription associata
        from models.subscription import Subscription
        Subscription.query.filter_by(shop_name=shop.shop_name).delete()

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



@landing_api.route('/available_themes', methods=['GET'])
def get_available_themes():
    try:
        themes = CMSAddon.query.filter_by(addon_type='themes').order_by(CMSAddon.created_at.desc()).all()
        data = [{
            'id': theme.id,
            'name': theme.name,
            'description': theme.description,
            'price': theme.price,
            'preview_image': theme.preview_image,
            'is_theme_json': theme.is_theme_json
        } for theme in themes]

        return jsonify(success=True, data=data)
    except Exception as e:
        logger.error(f"Errore nel recupero dei temi disponibili: {e}")
        return jsonify(success=False, message="Errore durante il recupero dei temi"), 500
    



@landing_api.route('/chat/send', methods=['POST'])
def send_chat_message():
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    data = request.get_json() or {}
    sender_id = session['user_id']
    receiver_id = data.get('receiver_id')
    message = data.get('message', '').strip()
    attachment_url = data.get('attachment_url')  # opzionale

    if not receiver_id or not message:
        return jsonify(success=False, message="Dati mancanti"), 400

    try:
        new_message = ChatMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message,
            attachment_url=attachment_url
        )
        db.session.add(new_message)
        db.session.commit()
        return jsonify(success=True, message="Messaggio inviato")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Errore nell'invio del messaggio: {e}")
        return jsonify(success=False, message="Errore durante l'invio del messaggio"), 500

@landing_api.route('/chat/messages', methods=['GET'])
def get_chat_messages():
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    user_id = session['user_id']
    target_id = request.args.get('user_id')

    if not target_id:
        return jsonify(success=False, message="ID utente destinatario mancante"), 400

    try:
        messages = ChatMessage.query.filter(
            ((ChatMessage.sender_id == user_id) & (ChatMessage.receiver_id == target_id)) |
            ((ChatMessage.sender_id == target_id) & (ChatMessage.receiver_id == user_id))
        ).order_by(ChatMessage.created_at.asc()).all()

        return jsonify(success=True, data=[msg.to_dict() for msg in messages])
    except Exception as e:
        logger.error(f"Errore nel recupero messaggi: {e}")
        return jsonify(success=False, message="Errore durante il recupero dei messaggi"), 500
    



    

@landing_api.route('/checkout/subscribe', methods=['GET'])
def checkout_subscribe():
    if 'user_id' not in session:
        return redirect('/login')
    
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']  # <-- deve esistere nel tuo config.py

    shop_name = request.args.get('shop_name')
    plan = request.args.get('plan')
    user_id = session['user_id']

    if not shop_name or not plan:
        return jsonify(success=False, message="Parametri mancanti"), 400

    environment = os.getenv('ENVIRONMENT', 'development')

    if environment == 'production':
        plans = {
            "allisready": {
                "label": "AllIsReady",
                "price": 18,
                "price_id": "price_1RC23wLbvfE9v2XlYWS1fTtS"
            },
            "professionaldesk": {
                "label": "ProfessionalDesk",
                "price": 36,
                "price_id": "price_1RC24VLbvfE9v2XlDtrNqxHg"
            }
        }
    else:
        plans = {
            "allisready": {
                "label": "AllIsReady",
                "price": 18,
                "price_id": "price_1RC3XtPteJOX9ukrGj97iGom"
            },
            "professionaldesk": {
                "label": "ProfessionalDesk",
                "price": 36,
                "price_id": "price_1RC3Y6PteJOX9ukrratINEP1"
            }
        }

    if plan not in plans:
        return jsonify(success=False, message="Piano non valido"), 400

    plan_data = plans[plan]

    try:
        session_stripe = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{
                "price": plan_data["price_id"],
                "quantity": 1
            }],
            metadata={
                "shop_name": shop_name,
                "user_id": str(user_id),
                "plan_name": plan
            },
            success_url=f"{request.host_url}subscription/success?shop={shop_name}",
            cancel_url=f"{request.host_url}subscription/cancel?shop={shop_name}"
        )
        return redirect(session_stripe.url, code=303)

    except Exception as e:
        logger.error(f"❌ Errore nella creazione della sessione Stripe: {e}")
        return jsonify(success=False, message="Errore nella creazione della sessione"), 500
    
@landing_api.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify(success=False, message="Utente non trovato"), 404

    data = request.form
    user.nome = data.get('nome', user.nome)
    user.cognome = data.get('cognome', user.cognome)
    user.telefono = data.get('telefono', user.telefono)
    user.profilo_foto = data.get('profilo_foto', user.profilo_foto)

    # 🔁 Upload dell'immagine dal PC (drag o selezione)
    if 'immagine_locale' in request.files:
        immagine = request.files['immagine_locale']
        if immagine.filename:
            from werkzeug.utils import secure_filename
            filename = secure_filename(f"user_{user.id}_{datetime.utcnow().timestamp()}.{immagine.filename.rsplit('.', 1)[-1]}")
            upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'users')
            os.makedirs(upload_path, exist_ok=True)
            immagine.save(os.path.join(upload_path, filename))
            user.profilo_foto = f"/static/uploads/users/{filename}"

    try:
        db.session.commit()
        return jsonify(success=True, message="Profilo aggiornato con successo", user=user.to_dict())
    except Exception as e:
        db.session.rollback()
        logger.error(f"Errore aggiornamento profilo: {e}")
        return jsonify(success=False, message="Errore durante l'aggiornamento"), 500
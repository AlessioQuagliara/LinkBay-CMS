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
from models.domain import Domain
from public.godaddy_api import GoDaddyAPI
from models.websettings import WebSettings
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

# 🏪 Crea un nuovo negozio (registrazione iniziale) ---------------------------------------------------------------------------------------------------
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

#+ 🔑 Crea accesso per negozio esistente ---------------------------------------------------------------------------------------------------
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

#+ 📧 Verifica se l'email è già registrata ---------------------------------------------------------------------------------------------------
@landing_api.route('/check_email', methods=['GET'])
def check_email():
    email = request.args.get('email', '').strip().lower()
    
    if not email:
        return jsonify(status='error', message='Email non fornita'), 400

    exists = User.query.filter_by(email=email).first() is not None
    return jsonify(status='exists' if exists else 'available')

#+ 🏷️ Controlla la disponibilità del nome negozio ---------------------------------------------------------------------------------------------------
@landing_api.route('/check_shopname', methods=['GET'])
def check_shopname():
    shop_name = request.args.get('shop_name', '').strip().lower()

    if not shop_name:
        return jsonify(status='error', message='Nome negozio non fornito'), 400

    exists = ShopList.query.filter_by(shop_name=shop_name).first() is not None
    return jsonify(status='exists' if exists else 'available')

#+ 🗑️ Elimina un negozio esistente ---------------------------------------------------------------------------------------------------
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

#+ 📊 Ottieni le vendite dei negozi dell'utente ---------------------------------------------------------------------------------------------------
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

#+ 🎫 Crea un nuovo ticket di supporto ---------------------------------------------------------------------------------------------------
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

#+ 📋 Recupera i ticket dell'utente ---------------------------------------------------------------------------------------------------
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

#+ ❌ Elimina un ticket di supporto ---------------------------------------------------------------------------------------------------
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

#+ 💬 Recupera i messaggi di un ticket ---------------------------------------------------------------------------------------------------
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

#+ ✉️ Invia un messaggio per un ticket ---------------------------------------------------------------------------------------------------
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



#+ 🎨 Ottieni i temi disponibili ---------------------------------------------------------------------------------------------------
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
    

#+ 📤 Invia un messaggio chat ---------------------------------------------------------------------------------------------------
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

#+ 📥 Recupera i messaggi chat ---------------------------------------------------------------------------------------------------
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
    
#+ ✅ Segna i messaggi come letti nella chat ---------------------------------------------------------------------------------------------------
@landing_api.route('/chat/mark-read', methods=['POST'])
def mark_messages_as_read():
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    try:
        user_id = session['user_id']
        data = request.get_json() or {}
        sender_id = data.get('sender_id')

        if not sender_id:
            return jsonify(success=False, message="ID mittente mancante"), 400

        updated = ChatMessage.query.filter_by(
            sender_id=sender_id,
            receiver_id=user_id,
            is_read=False
        ).update({"is_read": True})

        db.session.commit()
        return jsonify(success=True, updated=updated)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Errore durante l'aggiornamento dei messaggi come letti: {e}")
        return jsonify(success=False, message="Errore interno"), 500

#+ 🔔 Conta i messaggi chat non letti ---------------------------------------------------------------------------------------------------
@landing_api.route('/chat/unread-count', methods=['GET'])
def get_unread_chat_count():
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    try:
        user_id = session['user_id']
        from models.message import ChatMessage
        unread_count = ChatMessage.query.filter_by(receiver_id=user_id, is_read=False).count()
        return jsonify(success=True, unread_count=unread_count)
    except Exception as e:
        logger.error(f"Errore nel recupero dei messaggi non letti: {e}")
        return jsonify(success=False, message="Errore nel recupero dei messaggi"), 500
    

#+ 💳 Gestisci la sottoscrizione tramite checkout Stripe ---------------------------------------------------------------------------------------------------
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

    if environment == 'production' or environment == 'staging':
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
    
#+ 🔁 Aggiorna il profilo utente ---------------------------------------------------------------------------------------------------
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
    if 'avatar' in request.files:
        immagine = request.files['avatar']
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
    
#+ 🌍 Api per gestione Dominio ---------------------------------------------------------------------------------------------------

    # 📌 Controlla l'esistenza di un dominio
@landing_api.route('/domains/check', methods=['GET'])
def check_domain_availability():
    domain = request.args.get('domain', '').strip().lower()
    if not domain:
        return jsonify(success=False, message="Dominio non fornito"), 400

    try:
        api = GoDaddyAPI()
        result = api.search_domain(domain)
        if "error" in result:
            return jsonify(success=False, message=result["error"]), 500

        output = []

        # Inserisce il dominio richiesto come primo elemento della lista
        price = result.get("price", 1499000) / 1000000
        output.append({
            "domain": domain,
            "available": result.get("available", False),
            "price_eur": round(price + 5, 2)
        })

        # Aggiunge altri suggerimenti, se presenti
        suggestions = result.get("domains", [])
        for item in suggestions[:5]:
            name = item.get("domain", "")
            available = item.get("available", False)
            price = item.get("price", 1499000) / 1000000
            output.append({
                "domain": name,
                "available": available,
                "price_eur": round(price + 5, 2)
            })

        return jsonify(success=True, results=output)
    except Exception as e:
        logger.error(f"Errore verifica dominio: {e}")
        return jsonify(success=False, message="Errore nella verifica del dominio"), 500

# 📌 Crea una sessione Stripe Checkout per acquistare un dominio
@landing_api.route('/domains/checkout_session', methods=['POST'])
def create_domain_checkout_session():
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    data = request.get_json() or {}
    domain = data.get("domain", "").strip().lower()
    shop_name = data.get("shop_name", "").strip().lower()

    if not domain or not shop_name:
        return jsonify(success=False, message="Dati mancanti"), 400

    user = User.query.get(session['user_id'])
    shop = ShopList.query.filter_by(shop_name=shop_name).first()
    if not shop or shop.user_id != user.id:
        return jsonify(success=False, message="Accesso negato"), 403

    try:
        # Verifica disponibilità dominio
        api = GoDaddyAPI()
        check = api.search_domain(domain)
        if not check.get("available"):
            return jsonify(success=False, message="Dominio non disponibile"), 409

        # Calcolo prezzo con margine
        base_price = check.get("price", 1499000) / 1000000
        final_price = round(base_price + 5, 2)

        stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

        session_stripe = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": f"Acquisto dominio {domain}",
                    },
                    "unit_amount": int(final_price * 100),
                },
                "quantity": 1,
            }],
            metadata={
                "domain": domain,
                "shop_name": shop_name,
                "user_id": str(user.id)
            },
            success_url=f"{request.host_url}dashboard/domains/{shop_name}?success=true&domain={domain}",
            cancel_url=f"{request.host_url}dashboard/domains/{shop_name}?canceled=true&domain={domain}"
        )

        # ⚠️ Non salvare ancora nel DB, il dominio sarà salvato solo dopo il pagamento effettivo tramite webhook o endpoint separato
        return jsonify(success=True, url=session_stripe.url)
    except Exception as e:
        logger.error(f"Errore creazione sessione Stripe per dominio: {e}")
        return jsonify(success=False, message="Errore nella creazione del pagamento Stripe"), 500


    # 📌 Aggiungi i record manualmente nel database
@landing_api.route('/domains/manual', methods=['POST'])
def add_manual_domain():
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    data = request.get_json() or {}
    domain = data.get("domain", "").strip().lower()
    shop_name = data.get("shop_name", "").strip().lower()
    provider = data.get("dns_provider", "").strip()

    if not domain or not shop_name:
        return jsonify(success=False, message="Dati incompleti"), 400

    shop = ShopList.query.filter_by(shop_name=shop_name).first()
    if not shop or shop.user_id != session['user_id']:
        return jsonify(success=False, message="Accesso non autorizzato"), 403

    if Domain.query.filter_by(domain=domain).first():
        return jsonify(success=False, message="Dominio già presente"), 409

    new_domain = Domain(
        shop_id=shop.id,
        domain=domain,
        dns_provider=provider,
        record_a=data.get("record_a"),
        record_cname=data.get("record_cname"),
        record_mx=data.get("record_mx"),
        record_txt=data.get("record_txt"),
        record_ns=data.get("record_ns"),
        record_aaaa=data.get("record_aaaa"),
        record_srv=data.get("record_srv"),
        status="manual"
    )

    db.session.add(new_domain)
    db.session.commit()
    return jsonify(success=True, message="Dominio salvato manualmente", domain=domain)


    # 📌 Acquista il nuovo dominio
@landing_api.route('/domains/purchase', methods=['POST'])       
def purchase_domain():
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    data = request.get_json() or {}
    domain = data.get("domain", "").strip().lower()
    shop_name = data.get("shop_name", "").strip().lower()
    stripe_token = data.get("payment_source")

    if not domain or not shop_name or not stripe_token:
        return jsonify(success=False, message="Dati mancanti"), 400

    user = User.query.get(session['user_id'])
    shop = ShopList.query.filter_by(shop_name=shop_name).first()
    if not shop or shop.user_id != user.id:
        return jsonify(success=False, message="Accesso negato"), 403

    try:
        # 🔍 Verifica disponibilità dominio
        api = GoDaddyAPI()
        check = api.search_domain(domain)
        if not check.get("available"):
            return jsonify(success=False, message="Dominio non disponibile"), 409

        # 💰 Calcolo del prezzo totale con margine
        price = check.get("price", 1499000) / 1000000
        total_price = round(price + 5, 2)  # aggiungi il margine

        # 💳 Pagamento con Stripe
        stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
        charge = stripe.Charge.create(
            amount=int(total_price * 100),  # in centesimi
            currency="eur",
            description=f"Acquisto dominio {domain}",
            source=stripe_token,
            receipt_email=user.email
        )

        if not charge or charge.status != "succeeded":
            return jsonify(success=False, message="Pagamento non riuscito"), 402

        # ✅ Procedi con l'acquisto su GoDaddy
        contact = {
            "nameFirst": user.nome or "Utente",
            "nameLast": user.cognome or "",
            "email": user.email,
            "phone": user.telefono or "+390000000000"
        }

        result = api.purchase_domain(domain, {
            "domain": domain,
            "consent": {
                "agreementKeys": ["DNRA"],
                "agreedBy": request.remote_addr or "127.0.0.1",
                "agreedAt": datetime.utcnow().isoformat()
            },
            "contactAdmin": contact,
            "contactRegistrant": contact,
            "contactTech": contact
        })

        if "error" in result:
            return jsonify(success=False, message=result["error"]), 500

        # ℹ️ Salvataggio definitivo del dominio effettuato qui dopo il pagamento Stripe completato
        new_domain = Domain(
            shop_id=shop.id,
            domain=domain,
            dns_provider="GoDaddy",
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_domain)
        db.session.commit()

        return jsonify(success=True, message="Dominio acquistato con successo", domain=domain)
    except Exception as e:
        logger.error(f"Errore acquisto dominio: {e}")
        db.session.rollback()
        return jsonify(success=False, message="Errore durante l'acquisto del dominio"), 500
    
    # 📌 Disattiva rinnovo dominio (soft delete)
@landing_api.route('/domains/<int:domain_id>/disable-renewal', methods=['POST'])
def disable_domain_renewal(domain_id):
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    domain = Domain.query.get(domain_id)
    if not domain:
        return jsonify(success=False, message="Dominio non trovato"), 404

    shop = ShopList.query.get(domain.shop_id)
    if not shop or shop.user_id != session['user_id']:
        return jsonify(success=False, message="Accesso negato"), 403

    domain.renewal_enabled = False
    db.session.commit()
    return jsonify(success=True, message="Rinnovo disattivato correttamente.")

# 📧 Invia una email di conferma acquisto dominio
@landing_api.route('/domains/send-success-email', methods=['POST'])
def send_success_email():
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    data = request.get_json() or {}
    domain = data.get("domain", "").strip().lower()

    if not domain:
        return jsonify(success=False, message="Dominio mancante"), 400

    from flask_mail import Message
    from extensions import mail
    user = User.query.get(session['user_id'])

    try:
        msg = Message(
            subject="✅ Dominio acquistato con successo",
            sender="noreply@linkbay-cms.com",
            recipients=[user.email]
        )
        msg.body = f"Ciao {user.nome},\n\nIl tuo dominio '{domain}' è stato acquistato con successo."
        msg.html = f"""
        <h2 style="color:#333;">Dominio acquistato con successo!</h2>
        <p>Ciao {user.nome},</p>
        <p>Il tuo dominio personalizzato <strong>{domain}</strong> è stato acquistato con successo e sarà configurato entro pochi minuti.</p>
        <p>Grazie per aver scelto <strong>LinkBay-CMS</strong>!</p>
        <hr/>
        <p>🔗 <a href="https://linkbay-cms.com">Visita LinkBay-CMS</a></p>
        """
        mail.send(msg)
        return jsonify(success=True, message="Email inviata con successo")
    except Exception as e:
        logger.error(f"Errore invio email dominio: {e}")
        return jsonify(success=False, message="Errore durante l'invio della email"), 500
    

#+ 📢 Api per gestione Rotte Analytics ---------------------------------------------------------------------------------------------------

    # 📌 Salvataggio Google Analytics
@landing_api.route('/integrations/google_analytics/<shop_name>', methods=['POST'])
def saveGoogle(shop_name):
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401
    
    websettings = WebSettings.query.filter_by(shop_name=shop_name)
    
    try:
        db.session.commit()
        return jsonify(success=True, message="Google aggiornato con successo")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Errore aggiornamento Google: {e}")
        return jsonify(success=False, message="Errore durante l'aggiornamento"), 500
    
#+ 📢 Api per gestione Utenti ---------------------------------------------------------------------------------------------------

    # 📌 Aggiunta collaboratore
@landing_api.route('/dashboard/users/add', methods=['POST'])
def add_shop_user():
    """Aggiunge un utente esistente a uno shop come collaboratore."""
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    data = request.get_json(silent=True) or request.form.to_dict()
    email = (data.get('email') or '').strip().lower()
    access_level = (data.get('access_level') or 'viewer').strip().lower()
    shop_name = (data.get('shop_name')
                 or request.args.get('shop_name')
                 or _extract_shop_from_referrer(request.referrer))

    if not email or not shop_name:
        return jsonify(success=False, message="Parametri mancanti"), 400

    shop = ShopList.query.filter_by(shop_name=shop_name).first()
    if not shop:
        return jsonify(success=False, message="Negozio non trovato"), 404

    if not _user_is_owner_or_admin(session['user_id'], shop):
        return jsonify(success=False, message="Permessi insufficienti"), 403

    target_user = User.query.filter_by(email=email).first()
    if not target_user:
        return jsonify(success=False, message="Utente non trovato"), 404

    if UserStoreAccess.query.filter_by(user_id=target_user.id, shop_id=shop.id).first():
        return jsonify(success=False, message="Utente già autorizzato"), 409

    try:
        db.session.add(UserStoreAccess(
            user_id=target_user.id,
            shop_id=shop.id,
            access_level=access_level,
        ))
        db.session.commit()
        return jsonify(success=True, message="Utente aggiunto con successo")
    except Exception:
        db.session.rollback()
        return jsonify(success=False, message="Errore interno"), 500
    
    # 📌 Modifica permessi collaboratore
@landing_api.route('/dashboard/users/edit/<int:user_id>', methods=['POST'])
def edit_shop_user(user_id):
    """Aggiorna il livello di accesso di un collaboratore."""
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    data = request.get_json(silent=True) or request.form.to_dict()
    new_level = (data.get('access_level') or '').strip().lower()
    if new_level not in ('viewer', 'editor', 'admin'):
        return jsonify(success=False, message="Ruolo non valido"), 400

    shop_name = (data.get('shop_name')
                 or request.args.get('shop_name')
                 or _extract_shop_from_referrer(request.referrer))
    if not shop_name:
        return jsonify(success=False, message="shop_name mancante"), 400

    shop = ShopList.query.filter_by(shop_name=shop_name).first()
    if not shop:
        return jsonify(success=False, message="Negozio non trovato"), 404

    if not _user_is_owner_or_admin(session['user_id'], shop):
        return jsonify(success=False, message="Permessi insufficienti"), 403

    access_row = UserStoreAccess.query.filter_by(user_id=user_id, shop_id=shop.id).first()
    if not access_row:
        return jsonify(success=False, message="Accesso non trovato"), 404

    access_row.access_level = new_level
    db.session.commit()
    return jsonify(success=True, message="Permessi aggiornati")

    # 📌 Rimozione collaboratore
@landing_api.route('/dashboard/users/delete/<int:user_id>', methods=['POST'])
def delete_shop_user(user_id):
    """Rimuove un collaboratore dallo shop."""
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    shop_name = (request.form.get('shop_name')
                 or request.args.get('shop_name')
                 or _extract_shop_from_referrer(request.referrer))
    if not shop_name:
        return jsonify(success=False, message="shop_name mancante"), 400

    shop = ShopList.query.filter_by(shop_name=shop_name).first()
    if not shop:
        return jsonify(success=False, message="Negozio non trovato"), 404

    if not _user_is_owner_or_admin(session['user_id'], shop):
        return jsonify(success=False, message="Permessi insufficienti"), 403

    if shop.user_id == user_id:
        return jsonify(success=False, message="Impossibile rimuovere il proprietario"), 409

    access_row = UserStoreAccess.query.filter_by(user_id=user_id, shop_id=shop.id).first()
    if not access_row:
        return jsonify(success=False, message="Accesso non trovato"), 404

    db.session.delete(access_row)
    db.session.commit()
    return jsonify(success=True, message="Utente rimosso con successo")

# --------------------------------------------------------------------------------------------
# Helper
# --------------------------------------------------------------------------------------------
def _extract_shop_from_referrer(ref):
    """Estrae lo shop_name dall'URL /dashboard/users/<shop_name> presente nel referrer."""
    if not ref:
        return None
    marker = '/dashboard/users/'
    if marker in ref:
        tail = ref.split(marker, 1)[-1]
        return tail.split('?')[0].split('#')[0]
    return None


def _user_is_owner_or_admin(user_id, shop):
    """True se user_id è il proprietario o admin per quello shop."""
    if shop.user_id == user_id:
        return True
    return UserStoreAccess.query.filter_by(
        shop_id=shop.id, user_id=user_id, access_level='admin'
    ).first() is not None
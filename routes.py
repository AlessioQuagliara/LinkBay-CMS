from flask import render_template, redirect, url_for, request, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import User, ShopList, Page, WebSettings, CookiePolicy
from app import app, get_db_connection, get_auth_db_connection
from datetime import datetime
from creators import capture_screenshot
import base64, os, uuid, re, mysql.connector


# Se non trova la pagina va in 404 ------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Funzione per controllare se l'utente è autenticato -----------------------------------
def check_user_authentication():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    return session['username']

# Admin Routes -------------------------------------------------------------------------
@app.route('/admin/sign-in', methods=['GET', 'POST'])
def signin():
    db_conn = get_db_connection()  
    user_model = User(db_conn)  

    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        store_name = request.form.get('store_name')
        email = request.form.get('email')
        password = request.form.get('password')


        existing_user = user_model.get_user_by_email(email)
        if existing_user:
            flash('Email address already exists')
            return redirect(url_for('signin'))

        user_model.create_user(name, surname, email, password)
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('/admin/sign-in.html', title='LinkBay - Sign-in')

# Middleware per il debug delle sessioni
@app.before_request
def log_session_info():
    print(f"Request path: {request.path}")
    print(f"Session data: {session}")
    print(f"Cookies: {request.cookies}")

# Funzione di login -------------------------------------------------
@app.route('/admin/', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    auth_db_conn = get_auth_db_connection()  
    user_model = User(auth_db_conn)  

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = user_model.get_user_by_email(email)

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['nome']
            session['surname'] = user['cognome']
            session['email'] = user['email']
            session['phone'] = user['telefono']
            session['profile_photo'] = user['profilo_foto']

            print(f"Session after login: {session}")

            if user['is_2fa_enabled']:
                session['otp_secret'] = user['otp_secret']
                return redirect(url_for('verify_otp'))  
            else:
                return redirect(url_for('homepage'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
            return redirect(url_for('login'))

    return render_template('admin/login.html', title='Login')


@app.route('/admin/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return render_template('admin/logout.html', title='Logout')

@app.route('/admin/restore')
def restore():
    return render_template('/admin/restore.html', title='LinkBay - Restore')


# Verifica autenticazione utente -----------------------------------
def check_user_authentication():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    
    print(f"User authenticated: {session.get('username')}")
    return session['username']

# CMS Routes -------------------------------------------------------------------------
@app.route('/admin/cms/interface/')
@app.route('/admin/cms/interface/render')
def render_interface():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/interface/render.html', title='CMS Interface', username=username)
    return username  

# Rotta per la homepage del CMS
@app.route('/admin/cms/pages/homepage')
def homepage():
    username = check_user_authentication()
    print(f"Session in homepage: {session}")
    if isinstance(username, str):
        return render_template('admin/cms/pages/home.html', title='HomePage', username=username)
    return username

@app.route('/admin/cms/pages/orders')
def orders():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/orders.html', title='Orders', username=username)
    return username

@app.route('/admin/cms/pages/products')
def products():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/products.html', title='Products', username=username)
    return username

@app.route('/admin/cms/pages/customers')
def customers():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/customers.html', title='Customers', username=username)
    return username

@app.route('/admin/cms/pages/marketing')
def marketing():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/marketing.html', title='Marketing', username=username)
    return username

@app.route('/admin/cms/pages/online-content')
def online_content():
    username = check_user_authentication()
    
    if isinstance(username, str):
        shop_subdomain = request.host.split('.')[0]  
        print(f"Subdomain: {shop_subdomain}")  # Log del subdominio

        try:
            with get_auth_db_connection() as auth_db_conn:
                shoplist_model = ShopList(auth_db_conn)
                shop = shoplist_model.get_shop_by_name(shop_subdomain)

            if shop:
                print(f"Shop trovato: {shop}")  # Log per il negozio

                with get_db_connection() as db_conn:
                    page_model = Page(db_conn)
                    page_slug = 'home'
                    # Esegui la query e leggi il risultato
                    page = page_model.get_page_by_slug(page_slug, shop_subdomain)

                    if page:
                        updated_at = page['updated_at']
                        now = datetime.now()
                        minutes_ago = (now - updated_at).total_seconds() // 60  
                        return render_template(
                            'admin/cms/pages/content.html', 
                            title='Online Content', 
                            username=username, 
                            page=page,
                            shop=shop,
                            minutes_ago=int(minutes_ago)  
                        )
                    else:
                        flash('Contenuto della pagina non trovato.')
                        return redirect(url_for('homepage'))

            else:
                print("Nessun negozio trovato.")  # Log per negozio non trovato
                flash('Nessun negozio trovato per questo nome.')
                return redirect(url_for('homepage'))

        except mysql.connector.Error as e:
            print(f"Errore nel database: {str(e)}")  # Log del messaggio di errore
            flash('Errore durante l\'accesso ai dati del negozio o della pagina.')
            return redirect(url_for('homepage'))
    
    return username

@app.route('/admin/cms/pages/domain')
def domain():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/domain.html', title='Domain', username=username)
    return username

@app.route('/admin/cms/pages/shipping')
def shipping():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/shipping.html', title='Shipping', username=username)
    return username

# Editor Store Content ---------------------------------------------------------------------------------------------

# Editor code ----------------------------------------------------------------

@app.route('/admin/cms/function/edit-code/<slug>')
def edit_code_page(slug):
    username = check_user_authentication()
    
    if isinstance(username, str):
        db_conn = get_db_connection() 

        shop_subdomain = request.host.split('.')[0]  
        
        page_model = Page(db_conn)
        
        pages = page_model.get_all_pages(shop_subdomain)  
        page = page_model.get_page_by_slug(slug, shop_subdomain) 
        
        if page:
            content = page.get('content', '')  
            return render_template('admin/cms/store_editor/code_editor.html', 
                                   title=page['title'], 
                                   pages=pages, 
                                   page=page, 
                                   slug=slug,  
                                   content=content, 
                                   username=username)
    
    return username

# Funzione per salvare il codice modificato
@app.route('/admin/cms/function/save_code', methods=['POST'])
def save_code_page():
    try:
        data = request.get_json()  
        content = data.get('content')
        slug = data.get('slug')

        if not content or not slug:
            return jsonify({'success': False, 'error': 'Missing content or slug'}), 400

        db_conn = get_db_connection()
        
        shop_subdomain = request.host.split('.')[0]  
        
        page_model = Page(db_conn)

        success = page_model.update_page_content_by_slug(slug, content, shop_subdomain)

        return jsonify({'success': success})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
# Editor Script ----------------------------------------------------------------

@app.route('/admin/web_settings/edit')
def edit_web_settings():
    username = check_user_authentication()

    if isinstance(username, str):
        db_conn = get_db_connection()
        shop_subdomain = request.host.split('.')[0]  
        web_settings_model = WebSettings(db_conn)
        web_settings = web_settings_model.get_web_settings(shop_subdomain)  

        if web_settings:
            return render_template(
                'admin/cms/store_editor/script_editor.html',
                title='Edit Web Settings',
                username=username,
                web_settings=web_settings 
            )
        else:
            flash('Web settings not found for this shop.', 'danger')
            return redirect(url_for('homepage'))
        
    return redirect(url_for('login'))  

# Funzione per aggiornare le impostazioni web
@app.route('/admin/web_settings/update', methods=['POST'])
def update_web_settings():
    try:
        data = request.get_json()
        head_content = data.get('head')
        script_content = data.get('script')
        foot_content = data.get('foot')

        if not head_content or not script_content or not foot_content:
            return jsonify({'success': False, 'error': 'Missing content'}), 400

        db_conn = get_db_connection()
        shop_subdomain = request.host.split('.')[0]  
        web_settings_model = WebSettings(db_conn)
        success = web_settings_model.update_web_settings(shop_subdomain, head_content, script_content, foot_content)

        return jsonify({'success': success})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Editor block -------------------------------------------------------------------------------------------------------------------

@app.route('/admin/cms/store_editor/editor_interface', defaults={'slug': None})
@app.route('/admin/cms/store_editor/editor_interface/<slug>')
def editor_interface(slug=None):
    username = check_user_authentication()
    
    if isinstance(username, str):
        db_conn = get_db_connection()  
        shop_subdomain = request.host.split('.')[0]

        with get_auth_db_connection() as auth_db_conn:
            shoplist_model = ShopList(auth_db_conn)
            shop = shoplist_model.get_shop_by_name(shop_subdomain)

        if not shop:
            flash('Nessun negozio selezionato o negozio non trovato.', 'danger')
            return redirect(url_for('homepage'))

        page_model = Page(db_conn)
        pages = page_model.get_all_pages(shop_name=shop_subdomain)
        page = None
        page_title = 'CMS Interface'
        
        if slug:
            page = page_model.get_page_by_slug(slug, shop_subdomain)
            if page:
                page_title = page['title']

        current_url = request.path
        return render_template('admin/cms/store_editor/editor_interface.html', 
                               title=page_title, 
                               pages=pages, 
                               page=page, 
                               slug=slug,  
                               current_url=current_url, 
                               username=username)
    return username  


@app.route('/admin/cms/function/edit/<slug>')
def edit_page(slug):
    username = check_user_authentication()
    
    if isinstance(username, str):
        db_conn = get_db_connection()  
        shop_subdomain = request.host.split('.')[0]  

        with get_auth_db_connection() as auth_db_conn:
            shoplist_model = ShopList(auth_db_conn)
            shop = shoplist_model.get_shop_by_name(shop_subdomain)

        if not shop:
            flash('Nessun negozio selezionato o negozio non trovato.', 'danger')
            return redirect(url_for('homepage'))

        # Recupera la lingua selezionata
        language = request.args.get('language', 'en')  # Default "en" se non è specificata

        page_model = Page(db_conn)
        page = page_model.get_page_by_slug_and_language(slug, language, shop_subdomain)  

        if not page:
            flash('Pagina non trovata.', 'danger')
            return redirect(url_for('homepage'))

        return render_template('admin/cms/function/edit.html', title='Edit Page', page=page, username=username)
    
    return username

# SALVATAGGIO PAGINA CON CARICAMENTO IMMAGINI ----------------------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(base64_image, page_id, shop_subdomain):
    try:
        header, encoded = base64_image.split(",", 1)
        binary_data = base64.b64decode(encoded)

        # Creazione della cartella per il negozio specifico
        upload_folder = f"static/uploads/{shop_subdomain}"
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)  

        # Nome univoco per ogni immagine, ad esempio usando un UUID
        image_name = f"{page_id}_{uuid.uuid4().hex}.png"
        image_path = os.path.join(upload_folder, image_name)

        # Salva l'immagine
        with open(image_path, "wb") as f:
            f.write(binary_data)

        return f"/{upload_folder}/{image_name}"
    except Exception as e:
        print(f"Error saving image: {str(e)}")
        return None

# Funzione per salvare il contenuto della pagina con gestione delle immagini ---------------------------------
@app.route('/admin/cms/function/save', methods=['POST'])
def save_page():
    try:
        data = request.get_json()
        page_id = data.get('id')
        content = data.get('content')
        language = data.get('language')  # Aggiungiamo il parametro lingua
        shop_subdomain = request.host.split('.')[0]

        print(f"Salvataggio pagina con ID: {page_id}, lingua: {language} per il negozio: {shop_subdomain}")
        
        db_conn = get_db_connection()  
        page_model = Page(db_conn)  
        
        # Cerca immagini base64 nel contenuto
        img_tags = re.findall(r'<img.*?src=["\'](data:image/[^"\']+)["\']', content)
        for base64_img in img_tags:
            # Salva l'immagine base64
            image_url = save_image(base64_img, page_id, shop_subdomain)
            if image_url:
                # Sostituisci l'immagine base64 con l'URL dell'immagine salvata
                content = content.replace(base64_img, image_url)
        
        # Aggiorna il contenuto della pagina nel database con la lingua specifica
        success = page_model.update_or_create_page_content(page_id, content, language, shop_subdomain)
        return jsonify({'success': success})
    
    except Exception as e:
        print(f"Errore durante il salvataggio della pagina: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Funzione per salvare un'immagine base64 generica ---------------------------------------------------------------
def save_base64_image(base64_image):
    try:
        header, encoded = base64_image.split(",", 1)
        binary_data = base64.b64decode(encoded)

        # Genera un nome file unico usando UUID
        unique_filename = f"{uuid.uuid4().hex}.png"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        # Salva il file sul server
        with open(file_path, "wb") as f:
            f.write(binary_data)

        return f"/static/uploads/{unique_filename}"
    except Exception as e:
        print(f"Errore durante il salvataggio dell'immagine: {str(e)}")
        return None

# Endpoint Flask per gestire l'upload delle immagini generiche -------------------------------------------------------
@app.route('/upload-image', methods=['POST'])
def upload_image():
    data = request.get_json()
    base64_image = data.get('image')

    if not base64_image:
        return jsonify({'error': 'No image provided'}), 400

    image_url = save_base64_image(base64_image)
    
    if image_url:
        return jsonify({'url': image_url}), 200
    else:
        return jsonify({'error': 'Failed to upload image'}), 500
    
# Upload SEO -------------------------------------------------------

# Funzione per salvare i dati SEO della pagina
@app.route('/admin/cms/function/save-seo', methods=['POST'])
def save_seo_page():
    data = request.get_json()
    page_id = data.get('id')
    title = data.get('title')
    description = data.get('description')
    keywords = data.get('keywords')
    slug = data.get('slug')

    shop_subdomain = request.host.split('.')[0]  

    db_conn = get_db_connection()  
    page_model = Page(db_conn)  

    success = page_model.update_page_seo(page_id, title, description, keywords, slug, shop_name=shop_subdomain)

    return jsonify({'success': success})


# Funzione per creare una nuova pagina per un negozio specifico
@app.route('/admin/cms/function/create', methods=['POST'])
def create_page():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'You need to log in first.'})

    if request.method == 'POST':
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        keywords = data.get('keywords')
        slug = data.get('slug')
        content = data.get('content')
        theme_name = data.get('theme_name')
        paid = data.get('paid')
        language = data.get('language')
        published = data.get('published')

        shop_subdomain = request.host.split('.')[0]  

        db_conn = get_db_connection()
        page_model = Page(db_conn)  

        success = page_model.create_page(title, description, keywords, slug, content, theme_name, paid, language, published, shop_name=shop_subdomain)

        return jsonify({'success': success})
    

# Funzione per eliminare una pagina di un negozio specifico
@app.route('/admin/cms/function/delete', methods=['POST'])
def delete_page():
    data = request.get_json()
    page_id = data.get('id')  

    if not page_id:
        return jsonify({'success': False, 'message': 'ID pagina mancante.'})
    shop_subdomain = request.host.split('.')[0]  

    page_model = Page(get_db_connection())  
    try:
        page_model.delete_page(page_id, shop_name=shop_subdomain)  
        return jsonify({'success': True, 'message': 'Pagina cancellata con successo.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f"Errore durante la cancellazione: {str(e)}"})

# SCRIPT PAGE --------------------------------------------------------------------------------------------------------

# NEGOZIO ONLINE -----------------------------------------------------------------------------------------------------
@app.route('/capture-screenshot', methods=['POST'])
def capture_screenshot_route():
    try:
        capture_screenshot('http://127.0.0.1:5000/', 'static/images/screenshot_result.png')
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Addons e Componenti a pagamento aggiuntive

@app.route('/store-components')
def store_components():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/store-components/shop_page.html', title='UI Kit', username=username)
    return username

@app.route('/admin/cms/function/cookie-policy', methods=['GET', 'POST'])
def cookie_setting():
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_name = request.host.split('.')[0]

    with get_db_connection() as db_conn:
        cookie_model = CookiePolicy(db_conn)

        if request.method == 'POST':
            # Verifica se la richiesta è di tipo JSON
            if request.is_json:
                # Ottieni i dati dalla richiesta JSON
                data = request.json
                title = data.get('title')
                text_content = data.get('text_content')
                button_text = data.get('button_text')
                background_color = data.get('background_color')
                button_color = data.get('button_color')
                button_text_color = data.get('button_text_color')
                text_color = data.get('text_color')
                entry_animation = data.get('animation')

                # Controlla se esiste già una configurazione per questo negozio
                existing_setting = cookie_model.get_policy_by_shop(shop_name)

                # Aggiorna o crea la configurazione interna
                if existing_setting:
                    success = cookie_model.update_internal_policy(
                        shop_name, title, text_content, button_text,
                        background_color, button_color, button_text_color,
                        text_color, entry_animation
                    )
                else:
                    success = cookie_model.create_internal_policy(
                        shop_name, title, text_content, button_text,
                        background_color, button_color, button_text_color,
                        text_color, entry_animation
                    )

                # Ritorna il risultato come JSON per il feedback AJAX
                return jsonify({'success': success})

            # Ritorna errore se la richiesta non è JSON
            return jsonify({'success': False, 'error': 'Invalid request format'})

        else:
            # Recupera le impostazioni esistenti, se presenti
            cookie_settings = cookie_model.get_policy_by_shop(shop_name)

            return render_template(
                'admin/cms/function/cookie-policy.html',
                title='Cookie Bar Settings',
                username=username,
                cookie_settings=cookie_settings
            )


@app.route('/admin/cms/function/cookie-policy-third-party', methods=['GET', 'POST'])
def cookie_setting_third_party():
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_name = request.host.split('.')[0]

    with get_db_connection() as db_conn:
        cookie_model = CookiePolicy(db_conn)

        if request.method == 'POST':
            data = request.get_json()  # Modifica per accettare JSON
            if not data:
                return jsonify({'status': 'error', 'message': 'Invalid JSON data.'}), 400

            # Dati dal JSON per la configurazione di terze parti
            use_third_party = data.get('use_third_party', False)
            third_party_cookie = data.get('third_party_cookie', '')
            third_party_privacy = data.get('third_party_privacy', '')
            third_party_terms = data.get('third_party_terms', '')
            third_party_consent = data.get('third_party_consent', '')

            # Aggiorna o crea la configurazione di terze parti
            existing_setting = cookie_model.get_policy_by_shop(shop_name)
            if existing_setting:
                success = cookie_model.update_third_party_policy(
                    shop_name, use_third_party, third_party_cookie, 
                    third_party_privacy, third_party_terms, third_party_consent
                )
            else:
                success = cookie_model.create_third_party_policy(
                    shop_name, use_third_party, third_party_cookie, 
                    third_party_privacy, third_party_terms, third_party_consent
                )

            # Risposte JSON per richiesta AJAX
            if success:
                return jsonify({'status': 'success', 'message': 'Third-party cookie settings updated successfully!'})
            else:
                return jsonify({'status': 'error', 'message': 'Error updating third-party cookie settings.'}), 500

        # Recupera le impostazioni esistenti, se presenti
        cookie_settings = cookie_model.get_policy_by_shop(shop_name)

        return render_template(
            'admin/cms/function/cookie-policy-third-party.html',
            title='Third-Party Cookie Settings',
            username=username,
            cookie_settings=cookie_settings
        )
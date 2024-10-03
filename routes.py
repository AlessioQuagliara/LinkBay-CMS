from flask import render_template, redirect, url_for, request, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, ShopList, Page
from app import app, get_db_connection, get_auth_db_connection
from datetime import datetime

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

        # Controlla se l'email esiste già nel database
        existing_user = user_model.get_user_by_email(email)
        if existing_user:
            flash('Email address already exists')
            return redirect(url_for('signin'))

        # Crea un nuovo utente nel database
        user_model.create_user(name, surname, email, password)
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('/admin/sign-in.html', title='LinkBay - Sign-in')

@app.route('/admin/', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    auth_db_conn = get_auth_db_connection()  # Usa la connessione separata per CMS_INDEX
    user_model = User(auth_db_conn)  # Usa il modello User con la connessione al database di autenticazione

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Cerca l'utente nel database CMS_INDEX usando il modello User
        user = user_model.get_user_by_email(email)

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['nome']  # Usa 'nome' invece di 'name'
            session['surname'] = user['cognome']  # Usa 'cognome' invece di 'surname'
            session['email'] = user['email']
            session['phone'] = user['telefono']  # Aggiungi numero di telefono alla sessione
            session['profile_photo'] = user['profilo_foto']  # Aggiungi foto profilo alla sessione

            # Gestione del 2FA (autenticazione a due fattori)
            if user['is_2fa_enabled']:
                session['otp_secret'] = user['otp_secret']
                return redirect(url_for('verify_otp'))  # Reindirizza a una schermata per inserire OTP
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


# Controllo autenticazione (helper function)
def check_user_authentication():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    return session['username']

# CMS Routes -------------------------------------------------------------------------
@app.route('/admin/cms/interface/')
@app.route('/admin/cms/interface/render')
def render_interface():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/interface/render.html', title='CMS Interface', username=username)
    return username  

@app.route('/admin/cms/pages/homepage')
def homepage():
    username = check_user_authentication()
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
        # Recuperare i dati da ShopList
        with get_auth_db_connection() as auth_db_conn:
            shoplist_model = ShopList(auth_db_conn)
            shop_name = 'erboristeria'
            shop = shoplist_model.get_shop_by_name(shop_name)
        
        # Recupera i dati da page
        with get_db_connection() as db_conn:
            page_model = Page(db_conn)
            page_slug = 'home'
            page = page_model.get_page_by_slug(page_slug)
        
        if shop:
            # Calcolare i minuti dalla data di aggiornamento
            updated_at = page['updated_at']
            now = datetime.now()
            minutes_ago = (now - updated_at).total_seconds() // 60  # Differenza in minuti
            
            return render_template(
                'admin/cms/pages/content.html', 
                title='Online Content', 
                username=username, 
                page=page,
                shop=shop,
                minutes_ago=int(minutes_ago)  # Passa i minuti al template
            )
        else:
            flash('Nessun negozio trovato.')
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

# Editor Store Content -------------------------------------------------------------------------

# Editor code ----------------------------------------------------------------

@app.route('/admin/cms/function/edit-code/<slug>')
def edit_code_page(slug):
    username = check_user_authentication()
    
    if isinstance(username, str):
        db_conn = get_db_connection()  # Ottieni la connessione al DB
        
        # Crea un'istanza di Page passando la connessione al database
        page_model = Page(db_conn)
        
        pages = page_model.get_all_pages()  # Usa il modello Page per ottenere tutte le pagine
        page = None

        # Usa il modello Page per ottenere la pagina
        page = page_model.get_page_by_slug(slug)
        
        if page:
            content = page.get('content', '')  # Assicurati che 'content' esista e passalo al template
            return render_template('admin/cms/store_editor/code_editor.html', 
                                   title=page['title'], 
                                   pages=pages, 
                                   page=page, 
                                   content=content, 
                                   username=username)
    
    return username  # Se non autenticato, reindirizza al login

@app.route('/admin/cms/function/save_code', methods=['POST'])
def save_code_page():
    content = request.form.get('content')
    page_id = request.form.get('page_id')

    # Aggiungi un log per vedere cosa viene passato
    print(f"Received content for page {page_id}: {content[:100]}...")  # Log del contenuto (i primi 100 caratteri)
    
    # Se il contenuto è vuoto, lo stampiamo nel log per capire il problema
    if not content:
        print("Errore: Il contenuto è vuoto.")
        flash('Errore durante il salvataggio del contenuto. Il contenuto è vuoto.', 'danger')
        return redirect(url_for('edit_code_page', slug=page_id))

    db_conn = get_db_connection()  # Ottieni la connessione al DB
    page_model = Page(db_conn)  # Inizializza il modello Page con la connessione

    # Prova a salvare il contenuto
    success = page_model.update_page_code_content(page_id, content)

    if success:
        flash('Contenuto aggiornato con successo.', 'success')
    else:
        flash('Errore durante il salvataggio del contenuto.', 'danger')

    return redirect(url_for('edit_code_page', slug=page_id))

# Editor block ----------------------------------------------------------------

@app.route('/admin/cms/store_editor/editor_interface', defaults={'slug': None})
@app.route('/admin/cms/store_editor/editor_interface/<slug>')
def editor_interface(slug=None):
    username = check_user_authentication()
    
    if isinstance(username, str):
        db_conn = get_db_connection()  # Ottieni la connessione al DB
        
        # Crea un'istanza di Page passando la connessione al database
        page_model = Page(db_conn)
        
        pages = page_model.get_all_pages()  # Usa il modello Page per ottenere tutte le pagine
        page = None
        page_title = 'CMS Interface'
        
        if slug:
            page = page_model.get_page_by_slug(slug)
            if page:
                page_title = page['title']

        current_url = request.path
        return render_template('admin/cms/store_editor/editor_interface.html', 
                               title=page_title, 
                               pages=pages, 
                               page=page, 
                               current_url=current_url, 
                               username=username)
    return username  # Se non autenticato, reindirizza al login

@app.route('/admin/cms/function/edit/<slug>')
def edit_page(slug):
    username = check_user_authentication()
    
    if isinstance(username, str):
        db_conn = get_db_connection()  # Ottieni la connessione al DB
        
        # Crea un'istanza di Page passando la connessione al database
        page_model = Page(db_conn)
        
        # Usa il modello Page per ottenere la pagina
        page = page_model.get_page_by_slug(slug)
        
        return render_template('admin/cms/function/edit.html', title='Edit Page', page=page, username=username)
    
    return username  # Se non autenticato, reindirizza al login

@app.route('/admin/cms/function/save', methods=['POST'])
def save_page():
    data = request.get_json()
    page_id = data.get('id')
    content = data.get('content')

    db_conn = get_db_connection()  # Ottieni la connessione al DB
    page_model = Page(db_conn)  # Inizializza il modello Page con la connessione

    success = page_model.update_page_content(page_id, content)

    return jsonify({'success': success})

@app.route('/admin/cms/function/save-seo', methods=['POST'])
def save_seo_page():
    data = request.get_json()
    page_id = data.get('id')
    title = data.get('title')
    description = data.get('description')
    keywords = data.get('keywords')
    slug = data.get('slug')

    db_conn = get_db_connection()  # Ottieni la connessione al DB
    page_model = Page(db_conn)  # Passa la connessione al modello

    success = page_model.update_page_seo(page_id, title, description, keywords, slug)

    return jsonify({'success': success})

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

        db_conn = get_db_connection()  # Ottieni la connessione al DB
        page_model = Page(db_conn)  # Passa la connessione al modello

        success = page_model.create_page(title, description, keywords, slug, content, theme_name, paid, language, published)

        return jsonify({'success': success})
    
@app.route('/admin/cms/function/delete', methods=['POST'])
def delete_page():
    data = request.get_json()  # Riceve i dati dal frontend
    page_id = data.get('id')  # Estrae l'ID della pagina

    if not page_id:
        return jsonify({'success': False, 'message': 'ID pagina mancante.'})

    page_model = Page(get_db_connection())  # Usa la connessione al database
    try:
        page_model.delete_page(page_id)  # Cancella la pagina
        return jsonify({'success': True, 'message': 'Pagina cancellata con successo.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f"Errore durante la cancellazione: {str(e)}"})



# NEGOZIO ONLINE

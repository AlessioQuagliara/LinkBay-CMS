from flask import render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, get_db_connection

# Store Routes -------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html', title='home')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
# Admin Routes -------------------------------------------------------------------------
@app.route('/admin/sign-in', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        store_name = request.form.get('store_name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            flash('Email address already exists')
            return redirect(url_for('signin'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        cursor.execute('INSERT INTO user (name, surname, store_name, email, password) VALUES (%s, %s, %s, %s, %s)',
                       (name, surname, store_name, email, hashed_password))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    return render_template('/admin/sign-in.html', title='LinkBay - Sign-in')

@app.route('/admin/', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['name']
            session['surname'] = user['surname']
            session['email'] = user['email']
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

# CMS Routes -------------------------------------------------------------------------
@app.route('/admin/cms/interface/')
@app.route('/admin/cms/interface/render')
def render_interface():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    username = session['username']
    return render_template('admin/cms/interface/render.html', title='CMS Interface', username=username)

@app.route('/admin/cms/pages/homepage')
def homepage():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    username = session['username']
    return render_template('admin/cms/pages/home.html', title='HomePage', username=username)

@app.route('/admin/cms/pages/orders')
def orders():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    username = session['username']
    return render_template('admin/cms/pages/orders.html', title='Orders', username=username)

@app.route('/admin/cms/pages/products')
def products():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    username = session['username']
    return render_template('admin/cms/pages/products.html', title='Products', username=username)

@app.route('/admin/cms/pages/customers')
def customers():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    username = session['username']
    return render_template('admin/cms/pages/customers.html', title='Customers', username=username)

@app.route('/admin/cms/pages/marketing')
def marketing():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    username = session['username']
    return render_template('admin/cms/pages/marketing.html', title='Marketing', username=username)

@app.route('/admin/cms/pages/online-content')
def online_content():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    username = session['username']
    return render_template('admin/cms/pages/content.html', title='Online Content', username=username)

@app.route('/admin/cms/pages/domain')
def domain():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    username = session['username']
    return render_template('admin/cms/pages/domain.html', title='Domain', username=username)

@app.route('/admin/cms/pages/shipping')
def shipping():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    username = session['username']
    return render_template('admin/cms/pages/shipping.html', title='Shipping', username=username)


# Client Store Routes --------------------------------------------------------------------------------------------------------------
 # Funzione per ottenere la lingua preferita
def get_preferred_language():
    return request.accept_languages.best_match(['en', 'it'])

@app.route('/admin/pages')
def view_pages():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM pages")
    pages = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/cms/function/view_table.html', pages=pages)

@app.route('/admin/create-page', methods=['GET', 'POST'])
def create_page():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        keywords = request.form['keywords']
        slug = request.form['slug']
        content = request.form['content']
        theme_name = request.form['theme_name']
        language = request.form['language']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO pages (title, description, keywords, slug, content, theme_name, language) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (title, description, keywords, slug, content, theme_name, language))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        flash('Page created successfully!', 'success')
        return redirect(url_for('view_pages'))
    
    return render_template('admin/cms/function/create_page.html')


@app.route('/set-language/<language>')
def set_language(language):
    session['language'] = language
    return redirect(request.referrer or url_for('index'))
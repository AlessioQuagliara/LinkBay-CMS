from flask import Flask, render_template, redirect, url_for, request
from app import app

# Store Routes -------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html', title='home')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
# Admin Routes -------------------------------------------------------------------------
@app.route('/admin/')
@app.route('/admin/login')
def login():
    return render_template('/admin/login.html', title='LinkBay - Login')

@app.route('/admin/logout')
def logout():
    return render_template('/admin/logout.html', title='LinkBay - Logout')

@app.route('/admin/restore')
def restore():
    return render_template('/admin/restore.html', title='LinkBay - Restore')

@app.route('/admin/cms/interface/')
@app.route('/admin/cms/interface/render')
def render_interface():
    return render_template('/admin/cms/interface/render.html', title='LinkBay - CMS')

# CMS Routes -------------------------------------------------------------------------

@app.route('/admin/cms/pages/')
@app.route('/admin/cms/pages/homepage')
def homepage():
    return render_template('/admin/cms/pages/home.html', title='HomePage')

@app.route('/admin/cms/pages/orders')
def orders():
    return render_template('/admin/cms/pages/orders.html', title='Orders')

@app.route('/admin/cms/pages/products')
def products():
    return render_template('/admin/cms/pages/products.html', title='Products')

@app.route('/admin/cms/pages/customers')
def customers():
    return render_template('/admin/cms/pages/customers.html', title='Customers')

@app.route('/admin/cms/pages/marketing')
def marketing():
    return render_template('/admin/cms/pages/marketing.html', title='Marketing')

@app.route('/admin/cms/pages/online-content')
def online_content():
    return render_template('/admin/cms/pages/content.html', title='Online Content')

@app.route('/admin/cms/pages/domain')
def domain():
    return render_template('/admin/cms/pages/domain.html', title='Domain')

@app.route('/admin/cms/pages/shipping')
def shipping():
    return render_template('/admin/cms/pages/shipping.html', title='Shipping')
from flask import Flask, render_template, redirect, url_for
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

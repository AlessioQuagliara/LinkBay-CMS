from flask import Flask, render_template, redirect, url_for
from app import app

# Store Routes -------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')
# Admin Routes -------------------------------------------------------------------------
@app.route('/admin/')
def login():
    return render_template('/admin/login.html')
@app.route('/admin/logout')
def logout():
    return render_template('/admin/logout.html')
@app.route('/admin/restore')
def restore():
    return render_template('/admin/restore.html')
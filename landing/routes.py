from flask import render_template
from . import landing_bp

@landing_bp.route('/home')
def home():
    return render_template('landing/landing_home.html')
@landing_bp.route('/partner')
def partner():
    return render_template('landing/partner.html')
@landing_bp.route('/price')
def prices():
    return render_template('landing/price.html')
@landing_bp.route('/integration')
def integration():
    return render_template('landing/integration.html')
@landing_bp.route('/login')
def login():
    return render_template('landing/login.html')
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.database import db
from models import (
    SuperAdmin, SuperPages, SuperMedia, SuperInvoice, SuperMessages, SuperSupport
)
from werkzeug.security import check_password_hash, generate_password_hash
import os, json
import logging
from datetime import datetime, timedelta
from flask_wtf.csrf import CSRFProtect

admin_landing_bp = Blueprint('admin_landing', __name__)
csrf = CSRFProtect()

@admin_landing_bp.route('/editor/<content_type>', methods=['GET'])
def editor(content_type):
    return render_template("admin/editor.html", content_type=content_type)

@admin_landing_bp.route('/dashboard', methods=['GET'])
def admin_dashboard():
    return render_template("admin/dashboard.html")

@admin_landing_bp.route('/billing', methods=['GET'])
def admin_billing():
    return render_template("admin/billing.html")

@admin_landing_bp.route('/billing-user', methods=['GET'])
def admin_billing_user():
    return render_template("admin/billing_user.html")

@admin_landing_bp.route('/sales', methods=['GET'])
def admin_sales():
    return render_template("admin/sales.html")

@admin_landing_bp.route('/save_content/<content_type>', methods=['POST'])
def save_content(content_type):
    data = request.get_json()
    filename = data.get('filename', 'default')
    delta = data.get('delta')

    save_path = os.path.join("static", "json_content", content_type)
    os.makedirs(save_path, exist_ok=True)

    with open(os.path.join(save_path, f"{filename}.json"), "w") as f:
        json.dump(delta, f)

    return jsonify({"status": "success", "message": "Contenuto salvato"})

@admin_landing_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')

        admin = SuperAdmin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            session['admin_name'] = admin.full_name
            session['admin_role'] = admin.role
            session['last_activity'] = str(datetime.utcnow())

            logging.info(f"✅ Login superadmin {admin.email} ({admin.role})")
            return redirect(url_for('admin_landing.admin_dashboard'))

        logging.warning(f"❌ Tentativo fallito login superadmin: {email}")
        return render_template("admin/login.html", error="Credenziali non valide")
    return render_template("admin/login.html")

@admin_landing_bp.route('/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_landing.admin_login'))

# Protezione esempio per tutte le route sensibili
@admin_landing_bp.before_request
def require_login():
    allowed_routes = ['admin_landing.admin_login']
    if not session.get('admin_logged_in') and request.endpoint not in allowed_routes:
        return redirect(url_for('admin_landing.admin_login'))

    # Timeout per inattività: 30 minuti
    session.permanent = True
    admin_landing_bp.permanent_session_lifetime = timedelta(minutes=30)
    if 'last_activity' in session:
        now = datetime.utcnow()
        last_active = session['last_activity']
        if isinstance(last_active, str):
            last_active = datetime.strptime(last_active, '%Y-%m-%d %H:%M:%S.%f')
        if (now - last_active).total_seconds() > 1800:
            session.clear()
            return redirect(url_for('admin_landing.admin_login'))
    session['last_activity'] = str(datetime.utcnow())

@admin_landing_bp.route('/superadmins', methods=['GET'])
def view_superadmins():
    admins = SuperAdmin.query.all()
    return render_template("admin/superadmins.html", admins=admins)

@admin_landing_bp.route('/superpages', methods=['GET'])
def view_superpages():
    pages = SuperPages.query.order_by(SuperPages.created_at.desc()).all()
    return render_template("admin/superpages.html", pages=pages)

@admin_landing_bp.route('/supermedia', methods=['GET'])
def view_supermedia():
    media = SuperMedia.query.order_by(SuperMedia.created_at.desc()).all()
    return render_template("admin/supermedia.html", media=media)

@admin_landing_bp.route('/superinvoices', methods=['GET'])
def view_superinvoices():
    invoices = SuperInvoice.query.order_by(SuperInvoice.issued_at.desc()).all()
    return render_template("admin/superinvoices.html", invoices=invoices)

@admin_landing_bp.route('/supermessages', methods=['GET'])
def view_supermessages():
    messages = SuperMessages.query.order_by(SuperMessages.created_at.desc()).all()
    return render_template("admin/supermessages.html", messages=messages)

@admin_landing_bp.route('/supersupport', methods=['GET'])
def view_supersupport():
    tickets = SuperSupport.query.order_by(SuperSupport.created_at.desc()).all()
    return render_template("admin/supersupport.html", tickets=tickets)

@admin_landing_bp.route('/superadmins/new', methods=['GET', 'POST'])
def create_superadmin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'superadmin')

        hashed_pw = generate_password_hash(password)

        new_admin = SuperAdmin(
            email=email,
            password_hash=hashed_pw,
            full_name=full_name,
            role=role
        )
        db.session.add(new_admin)
        db.session.commit()
        return redirect(url_for('admin_landing.view_superadmins'))

    return render_template("admin/create_superadmin.html")
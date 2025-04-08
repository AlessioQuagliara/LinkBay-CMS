from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from models.database import db  # Importiamo il database SQLAlchemy
from models.cmsaddon import CMSAddon  # Modello per gli add-on
from models.page import Page  # Modello per la gestione delle pagine
from models.websettings import WebSettings  # Modello per le impostazioni web
from helpers import check_user_authentication
import os
import json
import logging

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione degli add-on del CMS
cmsaddon_bp = Blueprint('cmsaddon' , __name__)

# 📌 Route per applicare un tema -----------------------------------------------------------------------------------------------------------------------------------------------
@cmsaddon_bp.route('/api/apply-theme', methods=['POST'])
def apply_theme_api():
    try:
        data = request.get_json()
        shop_name = request.host.split('.')[0]
        theme_name = data.get("theme_name")

        if not theme_name:
            return jsonify({'status': 'error', 'message': 'Theme name is required'}), 400

        # 📌 Applica il tema
        success = apply_theme(theme_name, shop_name)

        if success:
            return jsonify({'status': 'success', 'message': f"Theme '{theme_name}' applied successfully"})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to apply theme'}), 500

    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Error applying theme '{theme_name}': {e}")
        return jsonify({'status': 'error', 'message': 'Unexpected error occurred'}), 500


# 📌 Funzione per applicare il tema dal file JSON -----------------------------------------------------------------------------------------------------------------------------
def apply_theme(theme_name, shop_name):
    theme_path = os.path.join("themes", f"{theme_name}.json")

    if not os.path.exists(theme_path):
        logging.error(f"❌ Theme file '{theme_path}' not found.")
        return False

    try:
        with open(theme_path, "r") as theme_file:
            theme_data = json.load(theme_file)

        # 📌 Aggiorna `web_settings`
        web_settings = WebSettings.query.filter_by(shop_name=shop_name).first()

        if web_settings:
            web_settings.theme_name = theme_name
            web_settings.head = theme_data.get("head", "")
            web_settings.foot = theme_data.get("foot", "")
            web_settings.script = theme_data.get("script", "")
        else:
            new_web_settings = WebSettings(
                shop_name=shop_name,
                theme_name=theme_name,
                head=theme_data.get("head", ""),
                foot=theme_data.get("foot", ""),
                script=theme_data.get("script", ""),
            )
            db.session.add(new_web_settings)

        # 📌 Aggiorna o inserisce le pagine
        for page in theme_data["pages"]:
            existing_page = Page.query.filter_by(slug=page["slug"], shop_name=shop_name).first()

            if existing_page:
                existing_page.content = page.get("content", "")
                existing_page.updated_at = datetime.utcnow()
            else:
                new_page = Page(
                    title=page.get("title", ""),
                    description=page.get("description"),
                    keywords=page.get("keywords"),
                    slug=page.get("slug", ""),
                    content=page.get("content"),
                    styles=page.get("styles"),
                    theme_name=page.get("theme_name"),
                    paid=page.get("paid", "No"),
                    language=page.get("language"),
                    published=bool(page.get("published", False)),
                    shop_name=shop_name,
                )
                db.session.add(new_page)

        db.session.commit()
        logging.info(f"✅ Tema '{theme_name}' applicato con successo a {shop_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'applicazione del tema '{theme_name}': {e}")
        return False
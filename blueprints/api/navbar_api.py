from flask import Blueprint, jsonify, request, send_file
from datetime import datetime, timedelta
from models.database import db
from models.navbar import NavbarLink
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

logging.basicConfig(level=logging.INFO)

def extract_shop_name(shop_subdomain):
    return shop_subdomain.split('.')[0] if '.' in shop_subdomain else shop_subdomain

navbar_bp = Blueprint('navbar', __name__, url_prefix='/api/')

@navbar_bp.route('navbar', methods=['GET'])
def get_navbar_links():
    """API per ottenere i link della navbar in base al sottodominio del negozio."""
    try:
        shop_subdomain = request.host.split(':')[0]  # Estrae il sottodominio dall'host
        shop_name = extract_shop_name(shop_subdomain)
        
        navbar_links = NavbarLink.query.filter_by(shop_name=shop_name).order_by(NavbarLink.position).all()
        
        def build_menu(links, parent_id=None):
            menu = []
            for link in links:
                if link.parent_id == parent_id:
                    submenu = build_menu(links, link.id)
                    menu.append({
                        "id": link.id,
                        "link_text": link.link_text,
                        "link_url": link.link_url,
                        "link_type": link.link_type,
                        "position": link.position,
                        "created_at": link.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        "updated_at": link.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                        "submenu": submenu if submenu else None
                    })
            return menu
        
        navbar_structure = build_menu(navbar_links)
        return jsonify({"shop_name": shop_name, "navbar": navbar_structure}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

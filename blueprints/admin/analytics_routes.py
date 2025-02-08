from flask import Blueprint, request, jsonify, session
from datetime import datetime
from db_helpers import DatabaseHelper
from models.site_visits import SiteVisits 
import logging
logging.basicConfig(level=logging.INFO)

db_helper = DatabaseHelper()
analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/api/track-visit', methods=['POST'])
def track_visit():
    """
    API per tracciare le visite degli utenti su una pagina.
    """
    try:
        # Ottieni il nome del negozio dal sottodominio
        shop_name = request.host.split('.')[0] if request.host else None
        if not shop_name:
            return jsonify({'success': False, 'error': 'Invalid shop name'}), 400

        # Ottieni i dati della richiesta JSON
        data = request.get_json()
        page_url = data.get("page_url", "/")

        # Ottieni informazioni aggiuntive dalla richiesta
        ip_address = request.remote_addr
        user_agent = request.headers.get("User-Agent", "Unknown")
        referrer = request.headers.get("Referer", "Direct")

        # Connessione al database e registrazione della visita
        with db_helper.get_db_connection() as conn:
            site_visits = SiteVisits(conn)
            site_visits.log_visit(shop_name, ip_address, user_agent, referrer, page_url)

        return jsonify({'success': True, 'message': 'Visit tracked successfully!'})

    except Exception as e:
        logging.error(f"Errore nel tracking della visita: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
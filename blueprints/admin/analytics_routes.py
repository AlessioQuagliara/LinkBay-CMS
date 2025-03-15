from flask import Blueprint, request, jsonify
import requests
from datetime import datetime
from models.database import db
from models.site_visits import SiteVisit
import logging

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per l'analytics
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

        # Ottieni i dati dalla richiesta JSON
        data = request.get_json()
        page_url = data.get("page_url", "/")

        # Ottieni informazioni aggiuntive
        ip_address = request.remote_addr
        user_agent = request.headers.get("User-Agent", "Unknown")
        referrer = request.headers.get("Referer", "Direct")

        # Creazione di una nuova visita nel database
        new_visit = SiteVisit(
            shop_name=shop_name,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            page_url=page_url,
            visit_time=datetime.utcnow()
        )

        # Salva la visita nel database
        db.session.add(new_visit)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Visit tracked successfully!'})

    except Exception as e:
        logging.error(f"Errore nel tracking della visita: {e}")
        db.session.rollback()  # Rollback in caso di errore
        return jsonify({'success': False, 'error': str(e)}), 500
    
@analytics_bp.route('/api/get-site-visits', methods=['GET'])
def get_site_visits():
    try:
        visits = SiteVisit.query.order_by(SiteVisit.visit_time.desc()).limit(50).all()
        visits_data = [
            {
                "ip_address": visit.ip_address,
                "page_url": visit.page_url,
                "visit_time": visit.visit_time.strftime("%Y-%m-%d %H:%M:%S"),
                "latitude": visit.latitude,
                "longitude": visit.longitude
            }
            for visit in visits
        ]
        return jsonify({"success": True, "visits": visits_data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
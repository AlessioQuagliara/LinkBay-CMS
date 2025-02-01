from flask import Blueprint, request, jsonify, session
from datetime import datetime
from db_helpers import DatabaseHelper

db_helper = DatabaseHelper()
analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/api/track-visit', methods=['POST'])
def track_visit():
    try:
        shop_name = request.host.split('.')[0]  # Ottieni il negozio dal sottodominio
        ip_address = request.remote_addr  # Ottieni l'IP dell'utente
        user_agent = request.headers.get('User-Agent', 'Unknown')  # Browser e device info
        referrer = request.referrer or 'Direct'  # Da dove proviene l'utente
        page_url = request.json.get('page_url', '/')

        # Verifica se l'utente ha già una sessione di visita
        if 'last_visit' in session and session['last_visit'] == page_url:
            return jsonify({'success': False, 'message': 'Already tracked this visit'}), 200
        
        # Salva la visita nel database
        with db_helper.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO site_visits (shop_name, ip_address, user_agent, referrer, page_url, visit_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (shop_name, ip_address, user_agent, referrer, page_url, datetime.utcnow()))
            conn.commit()

        session['last_visit'] = page_url  # Previene conteggi duplicati

        return jsonify({'success': True, 'message': 'Visit recorded'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
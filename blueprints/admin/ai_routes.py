from flask import Blueprint, request, jsonify
from models.stores_info import StoreInfo
from db_helpers import DatabaseHelper
from helpers import check_user_authentication
import logging, traceback, openai
logging.basicConfig(level=logging.INFO)

db_helper = DatabaseHelper()

ai_bp = Blueprint('ai', __name__)
    


@ai_bp.route('/assistant', methods=['POST'])
def assistant():
    try:
        # Leggi i dati inviati dal client
        data = request.json
        user_query = data.get('query', '').strip()
        shop_name = request.host.split('.')[0]

        if not user_query:
            return jsonify({"error": "No query provided"}), 400

        with db_helper.get_db_connection() as db_conn:
            store_info_model = StoreInfo(db_conn)
            store_info = store_info_model.get_store_by_shop_name(shop_name)

        # Prepara le informazioni di contesto
        industry = store_info['industry'] if store_info else "Unknown"
        description = store_info['description'] if store_info else "No description available"
        website_url = store_info['website_url'] if store_info else "No competitor provided"

        # Prompt migliorato per GPT-4
        prompt = (
            f"Sei un assistente AI per e-commerce. L'utente gestisce un negozio chiamato '{shop_name}', "
            f"che opera nel settore '{industry}'. Descrizione: '{description}'. "
            f"Il competitor segnalato è: {website_url}. \n\n"
            f"Il CMS è multitenant, si chiama LinkBay, tu sei la LinkBay AI. \n\n "
            f"Il CMS è orientato solo ad e-commerce, e le funzionalità a cui può accedere sono: /home = homepage, /products = sezione per gestire e creare prodotti, /orders = sezione per gestire gli ordini, /customers = sezione per gestire i clienti registati, /online_content = sezione per modificare drag & drop il tema e il codice, /domain = gestire e comprare un solo dominio, /shipping_methods = gestire e creare metodi di spedizione, /subscription = sottoscrivere l'abbonamento del cms che sono il basic da 28€ mensili, il pro da 79€ mensili ed il enterprise da 149€ mensili. \n\n "
            f"Il sito web da consultare del CMS è https://www.linkbay-cms.com/ e il software CMS è nel link 'https://{shop_name}'.yoursite-linkbay-cms.com sotto lo slash /admin/ ci sono tutte le sue rotte di funzione. \n\n"
            f"Rispondi in modo breve e preciso. \n\n"
            f"Domanda dell'utente: {user_query}."
        )

        # Chiamata API a GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sei un assistente esperto di e-commerce e strategie di business."},
                {"role": "user", "content": prompt}
            ]
        )

        # Estrai la risposta generata
        ai_response = response['choices'][0]['message']['content']

        return jsonify({"response": ai_response}), 200

    except Exception as e:
        logging.error("Errore durante la richiesta a GPT-4:")
        logging.error(traceback.format_exc())
        return jsonify({"error": "Errore interno al server."}), 500
    
@ai_bp.route('/api/analyze-store', methods=['GET'])
def analyze_store():
    try:
        shop_name = request.host.split('.')[0]

        with db_helper.get_db_connection() as db_conn:
            store_info_model = StoreInfo(db_conn)
            store_info = store_info_model.get_store_by_shop_name(shop_name)

        if not store_info:
            return jsonify({'suggestion': 'No data available for analysis.'}), 400

        industry = store_info.get('industry', 'Unknown')
        description = store_info.get('description', 'No description available')
        website_url = store_info.get('website_url', 'No competitor provided')

        prompt = (
            f"Negozio '{shop_name}', settore '{industry}'. Descrizione: '{description}'. "
            f"Competitor: {website_url}. "
            f"Fornisci un consiglio molto breve e sintetizzato per migliorare il business."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sei un esperto di e-commerce."},
                {"role": "user", "content": prompt}
            ]
        )

        suggestion = response['choices'][0]['message']['content']

        return jsonify({'suggestion': suggestion}), 200

    except Exception as e:
        logging.error(f"Errore nell'analisi AI dello store '{shop_name}': {e}")
        return jsonify({'error': 'Errore interno al server.'}), 500
from flask import Blueprint, request, jsonify
from models.database import db
from models.stores_info import StoreInfo
import logging
import traceback
import openai
from config import Config 

# 📌 Configurazione logging
logging.basicConfig(level=logging.INFO)

# 📌 Inizializza il Blueprint
ai_bp = Blueprint('ai', __name__)

# 📌 Configura OpenAI con la chiave API
client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

# 🚀 **API /assistant - Risponde alle domande degli utenti**
@ai_bp.route('/assistant', methods=['POST'])
def assistant():
    """
    API che utilizza OpenAI per rispondere alle domande dell'utente sul CMS LinkBay.
    """
    try:
        # 📌 Ottieni il nome del negozio dal sottodominio
        shop_name = request.host.split('.')[0] if request.host else None
        if not shop_name:
            return jsonify({"error": "Invalid shop name"}), 400

        # 📌 Ottieni la query dell'utente
        data = request.json
        user_query = data.get("query", "").strip()
        if not user_query:
            return jsonify({"error": "No query provided"}), 400

        # 📌 Recupera le informazioni del negozio dal database
        store_info = StoreInfo.query.filter_by(shop_name=shop_name).first()

        # 📌 Estrai le informazioni del negozio o imposta valori di default
        industry = store_info.industry if store_info else "Unknown"
        description = store_info.description if store_info else "No description available"
        website_url = store_info.website_url if store_info else "No competitor provided"

        # 📌 Costruzione del prompt AI per GPT-4
        prompt = (
            f"Sei un assistente AI specializzato nel CMS LinkBay. Il negozio '{shop_name}' opera nel settore '{industry}'.\n"
            f"Descrizione: '{description}'. Il competitor segnalato è: {website_url}.\n\n"
            f"LinkBayCMS è un CMS multitenant per e-commerce, con funzionalità avanzate:\n"
            f"  • /products: Gestione prodotti, immagini, prezzi, categorie, tag.\n"
            f"  • /orders: Gestione ordini, tracking spedizioni, pagamenti.\n"
            f"  • /customers: Analisi clienti, storico acquisti, preferenze.\n"
            f"  • /online_content: Personalizzazione interfaccia con drag & drop.\n"
            f"  • /domain: Gestione e acquisto domini personalizzati.\n"
            f"  • /subscription: Abbonamenti mensili (Basic, Pro, Enterprise).\n\n"
            f"Fornisci risposte chiare, pratiche e mirate alle domande dell'utente.\n\n"
            f"Domanda dell'utente: {user_query}."
        )

        # 📌 Chiamata API a OpenAI (GPT-4)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sei un esperto di strategia e-commerce."},
                {"role": "user", "content": prompt}
            ]
        )

        # 📌 Estrai la risposta generata
        if not response.choices:
            raise ValueError("Risposta AI non valida.")

        ai_response = response.choices[0].message.content

        return jsonify({"response": ai_response}), 200

    except Exception as e:
        logging.error(f"❌ Errore durante la richiesta a GPT-4: {e}")
        logging.error(traceback.format_exc())
        return jsonify({"error": "Errore interno al server. Riprova più tardi."}), 500
    


@ai_bp.route('/api/analyze-store', methods=['GET'])
def analyze_store():
    try:
        shop_name = request.host.split('.')[0] if request.host else None
        if not shop_name:
            return jsonify({"error": "Invalid shop name"}), 400

        store_info = StoreInfo.query.filter_by(shop_name=shop_name).first()
        if not store_info:
            return jsonify({'error': 'No store data available for analysis.'}), 400

        industry = store_info.industry or "Unknown"
        description = store_info.description or "No description available"
        website_url = store_info.website_url or "No competitor provided"

        prompt = (
            f"Sei un esperto di strategia di marketing. Analizza il negozio '{shop_name}', che opera nel settore '{industry}'.\n"
            f"Descrizione del negozio: {description}.\n"
            f"Competitor: {website_url}.\n\n"
            f"1. Elabora un'analisi SWOT (Punti di Forza, Debolezza, Opportunità, Minacce).\n"
            f"2. Fornisci una breve analisi del Marketing Mix (Prodotto, Prezzo, Punto vendita, Promozione).\n\n"
            f"Sii preciso, pratico, professionale e sintetico."
        )

        # **Aggiungi la chiave API direttamente al client**
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sei un esperto di e-commerce."},
                {"role": "user", "content": prompt}
            ]
        )

        if not response.choices:
            raise ValueError("Risposta AI non valida.")

        suggestion = response.choices[0].message.content

        return jsonify({'suggestion': suggestion}), 200

    except Exception as e:
        logging.error(f"❌ Errore nell'analisi AI dello store '{shop_name}': {e}")
        return jsonify({'error': 'Errore interno al server. Riprova più tardi.'}), 500
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

# 📌 Configura DeepSeek con la chiave API
client = openai.OpenAI(api_key=Config.DEEPSEEK_API_KEY)

# 🚀 **API /assistant - Risponde alle domande degli utenti con DeepSeek R1**
@ai_bp.route('/assistant', methods=['POST'])
def assistant():
    """
    API che utilizza DeepSeek R1 per rispondere alle domande dell'utente sul CMS LinkBay-CMS
    """
    try:
        # 📌 Ottieni il nome del negozio dal sottodominio
        shop_name = request.host.split('.')[0] if request.host else None
        if not shop_name:
            return jsonify({"error": "Nome negozio non valido"}), 400

        # 📌 Ottieni la query dell'utente
        data = request.get_json(silent=True) or {}
        user_query = data.get("query", "").strip()
        if not user_query:
            return jsonify({"error": "Nessuna query fornita"}), 400

        # 📌 Recupera le informazioni del negozio dal database
        store_info = StoreInfo.query.filter_by(shop_name=shop_name).first()

        # 📌 Estrai le informazioni del negozio o imposta valori di default
        industry = store_info.industry if store_info else "Sconosciuto"
        description = store_info.description if store_info else "Nessuna descrizione disponibile"
        website_url = store_info.website_url if store_info else "Nessun competitor indicato"

        # 📌 Costruzione del prompt ottimizzato per DeepSeek R1
        prompt = (
            f"Sei un assistente specializzato nel CMS LinkBay-CMS per e-commerce. "
            f"Stai aiutando il negozio '{shop_name}' nel settore '{industry}'.\n\n"
            f"### Contesto negozio:\n"
            f"- Descrizione: {description}\n"
            f"- Competitor principale: {website_url}\n\n"
            f"### Caratteristiche principali di LinkBay-CMS:\n"
            f"1. Gestione avanzata catalogo (varianti, SEO, categorie)\n"
            f"2. Sistema ordini con stato avanzato e gestione rimborsi\n"
            f"3. Anagrafica clienti con segmentazione\n"
            f"4. Editor drag & drop per contenuti\n"
            f"5. Gestione domini personalizzati\n"
            f"6. Piani di abbonamento scalabili\n"
            f"7. Moduli WMS per logistica\n"
            f"8. Integrazione Stripe per pagamenti\n"
            f"9. Moduli AI per analisi e assistenza\n\n"
            f"### Istruzioni:\n"
            f"1. Rispondi in modo tecnico ma chiaro\n"
            f"2. Se la domanda riguarda configurazioni, fornisci passaggi concreti\n"
            f"3. Per domande strategiche, suggerisci azioni basate sul settore '{industry}'\n"
            f"4. Mantieni le risposte concise (max 300 parole)\n\n"
            f"### Domanda utente:\n{user_query}"
        )

        # 📌 Configurazione client DeepSeek
        client = openai.OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1",
            timeout=20  # Timeout per evitare attese prolungate
        )

        # 🚀 Chiamata API a DeepSeek R1
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system", 
                    "content": "Sei un esperto del CMS LinkBay-CMS specializzato in e-commerce."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.3,  # Più preciso per risposte tecniche
            max_tokens=1024,   # Lunghezza controllata
            top_p=0.95,
            frequency_penalty=0.5
        )

        # 📌 Gestione della risposta
        if not response.choices or not response.choices[0].message.content:
            logging.error("❌ Risposta vuota da DeepSeek API")
            return jsonify({"error": "Nessuna risposta dall'assistente AI"}), 500

        ai_response = response.choices[0].message.content.strip()

        # ⏱️ Log della lunghezza della risposta
        token_count = len(ai_response.split())
        logging.info(f"✅ Risposta generata: {token_count} token per '{shop_name}'")

        return jsonify({
            "response": ai_response,
            "model": "deepseek-r1",
            "tokens": token_count
        }), 200

    except Exception as e:
        logging.error(f"❌ Errore durante la richiesta a DeepSeek: {str(e)}")
        logging.error(traceback.format_exc())
        
        # Messaggi di errore più specifici
        error_msg = "Servizio AI temporaneamente non disponibile"
        if "timeout" in str(e).lower():
            error_msg = "Timeout nella risposta dell'assistente AI"
            
        return jsonify({"error": error_msg}), 500
    


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

        # 🔧 Configurazione client DeepSeek con endpoint corretto
        client = openai.OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,  # Assicurati che questa variabile contenga la tua chiave DeepSeek
            base_url="https://api.deepseek.com/v1"  # Endpoint specifico per DeepSeek
        )

        # 🚀 Richiesta a DeepSeek invece di GPT-4
        response = client.chat.completions.create(
            model="deepseek-chat",  # Modello DeepSeek R1
            messages=[
                {"role": "system", "content": "Sei un esperto di e-commerce."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Opzionale: controlla la creatività
            max_tokens=2000    # Opzionale: controlla la lunghezza della risposta
        )

        if not response.choices or not response.choices[0].message.content:
            raise ValueError("Risposta AI non valida o vuota.")

        suggestion = response.choices[0].message.content

        return jsonify({'suggestion': suggestion}), 200

    except Exception as e:
        logging.error(f"❌ Errore nell'analisi AI dello store '{shop_name}': {str(e)}")
        return jsonify({'error': 'Errore interno al server. Riprova più tardi.'}), 500
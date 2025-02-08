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

        # Prompt migliorato per GPT-4 con maggiori dettagli sul CMS
        prompt = (
            f"Sei un assistente AI per e-commerce specializzato nel CMS LinkBay. L'utente gestisce un negozio chiamato '{shop_name}', "
            f"che opera nel settore '{industry}'. Descrizione: '{description}'. Il competitor segnalato è: {website_url}.\n\n"
            f"Il CMS LinkBay è un sistema multitenant dedicato esclusivamente ad e-commerce, con un'ampia gamma di funzionalità, "
            f"tra cui:\n"
            f"  • /home: Homepage del sito.\n"
            f"  • /products: Sezione per creare, gestire e modificare prodotti, con supporto per caricare immagini, specificare prezzi, "
            f"categorie, tag e altre informazioni rilevanti.\n"
            f"  • /orders: Gestione completa degli ordini, incluso il tracking delle spedizioni e l'integrazione con sistemi di pagamento.\n"
            f"  • /customers: Gestione dei clienti registrati, con informazioni sugli acquisti, preferenze e storico ordini.\n"
            f"  • /online_content: Modifica drag & drop del tema e del codice, per personalizzare l'interfaccia utente senza conoscenze tecniche avanzate.\n"
            f"  • /domain: Gestione e acquisto di un dominio, garantendo un indirizzo univoco e personalizzato per il negozio.\n"
            f"  • /shipping_methods: Creazione e gestione dei metodi di spedizione, per definire tariffe, aree di consegna e tempi di spedizione.\n"
            f"  • /subscription: Gestione degli abbonamenti, con diverse opzioni (Basic da 28€ mensili, Pro da 79€ mensili, Enterprise da 149€ mensili).\n\n"
            f"In aggiunta, il CMS offre funzionalità avanzate come reportistica, analisi delle performance, integrazione con API di pagamenti e "
            f"spedizioni e strumenti di marketing per ottimizzare le vendite.\n\n"
            f"Il servizio clienti è contattabile dal numero +39 389 965 7115, dalle 9 alle 17 dal lunedì al venerdì, in alternativa si può inviare una email a info@linkbay.it, tuttavia si consiglia nel pannello admin di associare ad una agenzia marketing in negozio per un supporto più preciso ed efficace.\n\n"
            f"Il sito ufficiale del CMS è https://www.linkbay-cms.com/ e il pannello di amministrazione si trova su "
            f"'https://{shop_name}.yoursite-linkbay-cms.com/admin/'.\n\n"
            f"Rispondi in modo breve, preciso e pratico, fornendo informazioni specifiche che aiutino l'utente a sfruttare al meglio il CMS.\n\n"
            f"Domanda dell'utente: {user_query}."
        )

        # Chiamata API a GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sei un assistente esperto di e-commerce e strategie di business, con una profonda conoscenza del CMS LinkBay."},
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

        # Prompt potenziato per addestrare meglio l'AI
        prompt = (
            f"Negozio: '{shop_name}'\n"
            f"Settore: '{industry}'\n"
            f"Descrizione: '{description}'\n"
            f"Competitor: {website_url}\n\n"
            f"Il negozio utilizza il CMS LinkBay, una piattaforma multitenant per e-commerce che offre funzionalità avanzate quali:\n"
            f"  • Gestione e creazione prodotti, con supporto per immagini, prezzi, categorie e tag.\n"
            f"  • Gestione degli ordini, inclusi tracking, integrazione con sistemi di pagamento e spedizioni.\n"
            f"  • Gestione dei clienti, con storico degli acquisti e analisi delle preferenze.\n"
            f"  • Personalizzazione del sito tramite drag & drop per modificare tema e codice.\n"
            f"  • Gestione dominio personalizzato.\n"
            f"  • Creazione e gestione dei metodi di spedizione.\n"
            f"  • Gestione degli abbonamenti (Basic, Pro, Enterprise) e reportistica avanzata.\n\n"
            f"Fornisci questi elementi in breve: una rassicurazione, una brevissima analisi sul suo competitors e in breve come riuscirà a raggiungerlo sfruttando LinkBay CMS "
            f"fornisci poi l'ultima tendenza e un prodotto di punta del settore, concludi dicendo di continuare la configurazione e dicendo che sei qui per aiutarlo."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Sei un esperto di e-commerce e un consulente strategico per l'ottimizzazione dei negozi online, con una profonda conoscenza "
                        "del CMS LinkBay e delle sue funzionalità. Fornisci consigli pratici e mirati per migliorare le performance e l'efficacia del business."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )

        suggestion = response['choices'][0]['message']['content']

        return jsonify({'suggestion': suggestion}), 200

    except Exception as e:
        logging.error(f"Errore nell'analisi AI dello store '{shop_name}': {e}")
        return jsonify({'error': 'Errore interno al server.'}), 500
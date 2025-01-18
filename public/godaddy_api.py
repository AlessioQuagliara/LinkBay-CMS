import requests
from config import Config
import logging
logging.basicConfig(level=logging.INFO)

class GoDaddyAPI:
    def __init__(self):
        self.api_url = Config.GODADDY_API_URL
        self.api_key = Config.GODADDY_API_KEY
        self.api_secret = Config.GODADDY_API_SECRET
        self.headers = {
            "Authorization": f"sso-key {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json"
        }

    def search_domain(self, domain_name):
        """
        Cerca la disponibilità di un dominio su GoDaddy.
        """
        try:
            search_url = f"{self.api_url}/domains/available"
            params = {"domain": domain_name}
            logging.info(f"Requesting URL: {search_url} with params: {params}")

            response = requests.get(search_url, headers=self.headers, params=params)
            logging.info(f"Response Status: {response.status_code}, Body: {response.text}")

            if response.status_code == 200:
                return response.json()  # Restituisce i dettagli dei domini
            elif response.status_code == 404:
                return {"domains": []}  # Nessun dominio trovato
            else:
                response.raise_for_status()  # Lancia un'eccezione per altri errori

        except requests.exceptions.RequestException as e:
            logging.info(f"Error in search_domain: {e}")
            return {"error": "Failed to search domain"}
        
    def purchase_domain(self, domain_name, customer_data):
        """
        Acquista un dominio su GoDaddy.
        """
        try:
            purchase_url = f"{self.api_url}/domains/purchase"
            logging.info(f"Requesting purchase for domain: {domain_name}")

            # Verifica che tutti i dati richiesti siano presenti
            required_fields = ["consent", "contactAdmin", "contactRegistrant", "contactTech"]
            for field in required_fields:
                if field not in customer_data:
                    raise ValueError(f"Missing required customer data: {field}")

            # Aggiungi il nome del dominio ai dati del cliente
            customer_data['domain'] = domain_name

            response = requests.post(
                purchase_url,
                headers=self.headers,
                json=customer_data
            )

            logging.info(f"Response Status: {response.status_code}, Body: {response.text}")

            if response.status_code == 200:
                return response.json()  # Restituisce i dettagli dell'acquisto
            else:
                response.raise_for_status()  # Lancia un'eccezione per altri errori

        except ValueError as ve:
            logging.info(f"Validation Error: {ve}")
            return {"error": str(ve)}

        except requests.exceptions.RequestException as e:
            logging.info(f"Error in purchase_domain: {e}")
            return {"error": "Failed to purchase domain"}
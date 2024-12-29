from flask import Flask, g, session, jsonify, request
from config import Config
from db_helpers import DatabaseHelper

# Configurazione dell'app Flask
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Inizializza il gestore del database
db_helper = DatabaseHelper()

# Registrazione Blueprint
from blueprints.admin import register_admin_blueprints
from blueprints.shop import register_user_blueprints
from blueprints.main import main_bp

app.register_blueprint(main_bp)
register_admin_blueprints(app)
register_user_blueprints(app)


# Gestione della connessione al database globale
@app.teardown_appcontext
def teardown_connections(exception):
    """
    Chiude le connessioni al database quando termina il contesto dell'applicazione.
    """
    db_helper.close()

# Rotta per cambiare la lingua
@app.route('/set-language', methods=['GET'])
def set_language():
    """
    Cambia la lingua corrente.
    """
    lang = request.args.get('lang', 'en')
    if lang in app.config['LANGUAGES']:
        session['language'] = lang
        return jsonify({"success": True, "message": f"Language set to {lang}"})
    return jsonify({"success": False, "message": "Invalid language"}), 400


# Avvio dell'applicazione
if __name__ == '__main__':
    app.run(debug=True)
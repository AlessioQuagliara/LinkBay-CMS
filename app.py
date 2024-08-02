from flask import Flask, render_template, redirect, url_for, request
from flask_babel import Babel, _
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

babel = Babel(app)

# Configura il selettore di localizzazione usando locale_selector_func
def get_locale():
    print("Calling get_locale")
    selected_locale = request.accept_languages.best_match(app.config['LANGUAGES'])
    print(f"Selected locale: {selected_locale}")
    return selected_locale

babel.locale_selector_func = get_locale

# Includi le rotte
from routes import *

if __name__ == '__main__':
    app.run(debug=True)
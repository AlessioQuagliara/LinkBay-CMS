from flask import Flask

from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme

app = Flask(__name__)

admin = Admin(app, name='LinkBayCMS', theme=Bootstrap4Theme(swatch='cerulean'))
# Viste amministrative qui sotto


@app.route("/")
def hello_world():
    return "response: Ciao"

if __name__ == "__main__":
    app.run(debug=True)
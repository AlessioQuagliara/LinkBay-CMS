from flask import Flask
from landing import landing_bp

app = Flask(__name__, template_folder="landing/templates", static_folder="landing/static")
app.register_blueprint(landing_bp)

if __name__ == "__main__":
    app.run(port=5001)
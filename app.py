from flask import Flask, render_template, redirect, url_for
app = Flask(__name__)

from routes import *

if __name__ == '__main__':
    app.run(debug=True)
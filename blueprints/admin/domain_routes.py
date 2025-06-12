from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from models.database import db
from models.domain import Domain  # Importa il modello SQLAlchemy per i domini
from models.shoplist import ShopList  # Importa il modello SQLAlchemy per i negozi
from config import Config
from datetime import datetime
from public.godaddy_api import GoDaddyAPI
from helpers import check_user_authentication
import logging
import re

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione dei domini
domain_bp = Blueprint('domain', __name__)


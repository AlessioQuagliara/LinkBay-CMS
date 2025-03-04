from sqlalchemy import create_engine
from config import Config

DATABASE_URL = f"postgresql+psycopg2://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}"

engine = create_engine(DATABASE_URL)
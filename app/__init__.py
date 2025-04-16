# Flask libraries
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

# App
from config import config_by_name
from utils.utils import get_secret

# Aux libraries
from urllib.parse import quote_plus

# SQL Database
db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    DB_HOST = get_secret( app.config.get("DB_HOST") )
    DB_PORT = get_secret( app.config.get("DB_PORT") )
    DB_USER = get_secret( app.config.get("DB_USER") )
    DB_PASSWORD = get_secret( app.config.get("DB_PASSWORD") )
    DB_NAME = get_secret( app.config.get("DB_NAME") )

    encoded_password = quote_plus(DB_PASSWORD)

    # Configura la URI
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Link SQLAlchemy with the Flask app 
    db.init_app(app)

    # Init the app routes
    from routes import init_app_routes
    init_app_routes(app)

    return app

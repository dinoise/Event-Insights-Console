# Flask libraries
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

# App
from config import config_by_name
from utils.utils import get_secret
from llm_orchestrator.llm_orchestrator import LLMOrchestrator

# Aux libraries
from urllib.parse import quote_plus
from os import environ

# LangChaing libraries
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.cache import InMemoryCache
from langchain.globals import set_llm_cache

# Solo una instancia de SQLAlchemy
db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Configuración para MySQL
    DB_HOST = get_secret(app.config.get("DB_HOST"))
    DB_PORT = get_secret(app.config.get("DB_PORT"))
    DB_USER = get_secret(app.config.get("DB_USER"))
    DB_PASSWORD = get_secret(app.config.get("DB_PASSWORD"))
    DB_NAME = get_secret(app.config.get("DB_NAME"))

    encoded_password = quote_plus(DB_PASSWORD)
    
    # Configuración para PostgreSQL
    PG_HOST = get_secret(app.config.get("PG_HOST"))
    PG_PORT = get_secret(app.config.get("PG_PORT"))
    PG_USER = get_secret(app.config.get("PG_USER"))
    PG_PASSWORD = get_secret(app.config.get("PG_PASSWORD"))
    PG_NAME = get_secret(app.config.get("PG_NAME"))

    encoded_pg_password = quote_plus(PG_PASSWORD)

    # Configuración de SQLAlchemy con binds
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    

    app.config['SQLALCHEMY_BINDS'] = {
        'postgres': f'postgresql+psycopg2://{PG_USER}:{encoded_pg_password}@{PG_HOST}:{PG_PORT}/{PG_NAME}'
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa la única instancia de SQLAlchemy
    db.init_app(app)

    # Init the app routes
    from routes import init_app_routes
    init_app_routes(app)

    # Init the orchestrator for the LLM
    app.secret_key = environ.get('SECRET_KEY', None)
    app.orchestrator = LLMOrchestrator(resource_id=app.config.get("AGENT_ENGINE_ID"))

    # Init embed service
    set_llm_cache(InMemoryCache())
    app.embed_service = VertexAIEmbeddings(
        model_name=app.config.get("EMBEDDING_MODEL_NAME")
    )

    return app
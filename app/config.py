# config.py
from os import getenv
from dotenv import load_dotenv

load_dotenv()  # take environment variables

class Config:
    """Configuraciones comunes"""
    FLASK_ENV = getenv("FLASK_ENV", "dev")
    PROJECT_ID = getenv("GOOGLE_CLOUD_PROJECT")

    MODEL_NAME = getenv("MODEL_NAME")
    EMBEDDING_MODEL_NAME = getenv("EMBEDDING_MODEL_NAME")
    AGENT_ENGINE_ID = getenv("AGENT_ENGINE_ID")
    
class DevelopmentConfig(Config):
    """Configurations for development"""

    # Dectect if we are in local (CLOUD_VAR is a variable defined in Cloud Run)
    IS_NOT_LOCAL = getenv("CLOUD_VAR") is not None
    
    # Configuration for MySQL
    DB_HOST = "MYSQL_IP_PRIVATE" if IS_NOT_LOCAL else "MYSQL_IP_PUBLIC"
    DB_PORT = "MYSQL_PORT"
    DB_USER = "MYSQL_USR_DELIVERNOW_DEV"
    DB_PASSWORD = "MYSQL_PASS_DELIVERNOW_DEV"
    DB_NAME = "MYSQL_DB_DELIVERNOW_DEV"

    # Configuration for PostgreSQL
    PG_HOST = "POSTGRE_IP_PRIVATE" if IS_NOT_LOCAL else "POSTGRE_IP_PUBLIC"
    PG_PORT = "POSTGRE_PORT"
    PG_USER = "POSTGRE_USR_RAG_REPO_DEV"
    PG_PASSWORD = "POSTGRE_PASS_RAG_REPO_DEV"
    PG_NAME = "POSTGRE_DB_RAG_REPO"

    BIGQUERY_DATASET_DELIVERNOW_EVENTS = "BQ_DS_RAW_DELIVERNOW_DEV"
    BIGQUERY_TBL_INGESTION_EVENT = "BQ_TB_INGESTION_EVENT"
    
    BIGQUERY_DATASET = "BQ_DS_SILVER_DELIVERNOW"
    BIGQUERY_TBL_CLIENTES = "BQ_TB_DELIVER_CLIENTES"
    BIGQUERY_TBL_ENVIOS = "BQ_TB_DELIVER_ENVIOS"
    BIGQUERY_TBL_PEDIDOS = "BQ_TB_DELIVER_PEDIDOS"

class ProductionConfig(Config):
    """Configurations for production"""

    # Configuration for MySQL
    DB_HOST = "MYSQL_IP_PRIVATE"
    DB_PASSWORD = "MYSQL_PASS_DELIVERNOW_DEV"
    DB_NAME = "MYSQL_DB_DELIVERNOW_DEV"

# Dictionary to select the environment
config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig
}
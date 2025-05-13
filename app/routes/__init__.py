from routes.web_routes import bp as web_bp
from routes.llm_routes import bp as llm_bp
from routes.event_data import bp as event_data_bp
from routes.source_routes import bp as sources_bp
from routes.event_type_routes import bp as event_types_bp
from routes.event_embeddings_routes import bp as embeddings_bp
from routes.event_mapping_routes import bp as event_mapping_bp
from routes.ingestion_event_routes import bp as ingestion_events_bp
from routes.event_mapping_columns_routes import bp as mappings_columns_bp

def init_app_routes(app):
    app.register_blueprint(web_bp)
    app.register_blueprint(llm_bp)
    app.register_blueprint(sources_bp)
    app.register_blueprint(event_data_bp)
    app.register_blueprint(embeddings_bp)
    app.register_blueprint(event_types_bp)
    app.register_blueprint(event_mapping_bp)
    app.register_blueprint(ingestion_events_bp)
    app.register_blueprint(mappings_columns_bp)
    
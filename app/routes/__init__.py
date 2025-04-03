from routes.source_routes import bp as sources_bq
from routes.event_type_routes import bp as event_types_bq

def init_app_routes(app):
    app.register_blueprint(sources_bq)
    app.register_blueprint(event_types_bq)

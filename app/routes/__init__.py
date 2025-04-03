from routes.source_routes import bp as sources_bq

def init_app_routes(app):
    app.register_blueprint(sources_bq)

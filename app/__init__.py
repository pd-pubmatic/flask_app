from flask import Flask
from config import Config
import logging_config
from app.routes.healthcheck import healthcheck

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize logging
    logging_config.setup_logging()

    # Register blueprints
    from app.routes.creative_tagging_routes import creative_tagging
    app.register_blueprint(creative_tagging)
    app.register_blueprint(healthcheck)

    return app

import os
from flask import Flask
from app.config import config_by_name
from app.utils.logging import configure_logging


def create_app(config_name: str | None = None) -> Flask:
    """Application factory pattern"""

    # Configure structured logging
    configure_logging()

    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app.config.from_object(config_by_name[config_name])

    # Register Blueprints
    from app.api.health import health_bp
    app.register_blueprint(health_bp)

    return app
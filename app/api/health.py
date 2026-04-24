import structlog
from flask import Blueprint, current_app, jsonify

logger = structlog.get_logger(__name__)
health_bp = Blueprint("health", __name__)


@health_bp.route("/healthz", methods=["GET"])
def health_check():
    logger.info("Health check requested")
    return (
        jsonify(
            {
                "status": "ok",
                "environment": current_app.config.get("FLASK_ENV", "unknown"),
            }
        ),
        200,
    )

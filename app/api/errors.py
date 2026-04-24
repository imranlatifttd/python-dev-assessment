from flask import jsonify
from werkzeug.exceptions import HTTPException
import structlog

logger = structlog.get_logger(__name__)

def register_error_handlers(app):
    @app.errorhandler(429)
    def ratelimit_handler(e):
        logger.warning("Rate limit exceeded", description=e.description)
        return jsonify({
            "error": "Too Many Requests",
            "details": [{"msg": f"Rate limit exceeded: {e.description}", "type": "rate_limit_exceeded"}]
        }), 429

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            "error": e.name,
            "details": [{"msg": e.description, "type": "http_error"}]
        }), e.code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        logger.exception("Unhandled exception", exc_info=e)
        return jsonify({
            "error": "Internal Server Error",
            "details": [{"msg": "An unexpected error occurred", "type": "internal_error"}]
        }), 500
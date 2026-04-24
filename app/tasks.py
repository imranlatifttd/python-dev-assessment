import uuid

import structlog

from app.celery_app import celery
from app.services.pipeline import run_visibility_pipeline

logger = structlog.get_logger(__name__)

flask_app = None


@celery.task(name="execute_pipeline_task")
def execute_pipeline_task(run_uuid_str: str, correlation_id: str = None):
    """Background task to execute the visibility pipeline."""
    global flask_app

    # bind the correlation ID and the run UUID to all worker logs
    structlog.contextvars.clear_contextvars()
    if correlation_id:
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    structlog.contextvars.bind_contextvars(run_uuid=run_uuid_str)

    if flask_app is None:
        from app import create_app

        flask_app = create_app()

    with flask_app.app_context():
        logger.info("Starting background pipeline task", run_uuid=run_uuid_str)
        run_visibility_pipeline(uuid.UUID(run_uuid_str))

import logging

import structlog


def configure_logging():
    """Configures structured JSON logging with context variable support"""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,  # injects correlation ID
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

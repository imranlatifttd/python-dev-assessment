from celery import Celery

celery = Celery("app", include=["app.tasks"])


def init_celery(app):
    """Configures celery to run within the flask app context"""
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_ignore_result=True,
    )
    return celery

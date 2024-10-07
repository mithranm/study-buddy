from celery import Celery
from flask import Flask

def make_celery(app: Flask) -> Celery:
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY']['broker_url'],
        backend=app.config['CELERY']['result_backend']
    )
    celery.conf.update(app.config['CELERY'])
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        """Ensures each Celery task runs within the Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
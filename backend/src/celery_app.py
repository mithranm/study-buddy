from . import create_app
from .make_celery import make_celery

flask_app = create_app()
celery_app = make_celery(flask_app)

# Import tasks to register them with Celery
from . import tasks
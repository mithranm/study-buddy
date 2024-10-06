from . main import create_app
from .tasks import process_file

flask_app = create_app()
celery_app = flask_app.extensions['celery']
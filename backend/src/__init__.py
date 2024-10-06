# src/__init__.py

import os
from flask import Flask
from flask_cors import CORS
from celery import Celery
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND'],
    )
    celery.conf.update(app.config)
    celery.autodiscover_tasks(['src'])  # Auto-discover tasks in 'src' package

    class ContextTask(celery.Task):
        """Ensures each task runs within the Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Load configurations
    app.config.from_mapping(
        CHROMA_HOST=os.getenv("CHROMA_HOST", "localhost"),
        CHROMA_PORT=os.getenv("CHROMA_PORT", "9092"),
        CELERY_BROKER_URL=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        CELERY_RESULT_BACKEND=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER", "uploads"),
        TEXTRACTED_PATH=os.getenv("TEXTRACTED_PATH", "textracted"),
        # Other configurations...
    )

    # Initialize Celery
    celery = make_celery(app)
    app.celery = celery  # Store celery instance in app

    # Set base_path to the project root directory
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Set default configurations
    app.config.setdefault('CHROMA_DB_PATH', os.path.join(base_path, 'chroma_db'))
    app.config.setdefault('UPLOAD_FOLDER', os.path.join(base_path, 'uploads'))
    app.config.setdefault('TEXTRACTED_PATH', os.path.join(base_path, 'textracted'))

    # Ensure the required directories exist
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['CHROMA_DB_PATH'], exist_ok=True)
        os.makedirs(app.config['TEXTRACTED_PATH'], exist_ok=True)
        app.logger.info("Created necessary directories")
    except Exception as e:
        app.logger.error(f"Error creating directories: {str(e)}")

    # Global variables to track initialization status
    app.nltk_ready = False
    app.chroma_ready = False
    app.initialization_error = None

    with app.app_context():
        try:
            # Initialize NLTK
            import nltk
            nltk.download('punkt', quiet=True)
            app.nltk_ready = True

            # Initialize Chroma collection
            from . import vector_db
            vector_db.initialize_chroma()
            app.chroma_ready = True
        except LookupError as le:
            app.initialization_error = f"NLTK LookupError: {str(le)}"
            app.logger.error(f"Initialization error: {str(le)}")
        except Exception as e:
            app.initialization_error = f"General Initialization Error: {str(e)}"
            app.logger.error(f"Initialization error: {str(e)}")

    # Register blueprints or routes
    from .main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/api/')

    return app

# Expose the celery app instance at the module level
celery = make_celery(create_app())

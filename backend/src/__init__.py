# src/__init__.py

from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    # Load configurations
    app.config.from_mapping(
        CHROMA_HOST=os.getenv("CHROMA_HOST", "localhost"),
        CHROMA_PORT=os.getenv("CHROMA_PORT", "9092"),
        CELERY=dict(
            broker_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            result_backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            task_ignore_result=False,
        ),
        UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER", "uploads"),
        TEXTRACTED_PATH=os.getenv("TEXTRACTED_PATH", "textracted"),
        # Other configurations...
    )

    # Register blueprints or routes
    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    return app

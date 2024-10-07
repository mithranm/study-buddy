# backend/src/extensions.py

from flask_socketio import SocketIO
from celery import Celery

# Initialize SocketIO without an app initially
socketio = SocketIO(cors_allowed_origins="*", async_mode='gevent')

# Initialize Celery without an app initially
celery = Celery()

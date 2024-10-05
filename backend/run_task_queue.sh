#!/bin/bash

# Start Gunicorn in the background
poetry run gunicorn --bind 0.0.0.0:9090 src.wsgi:app &
GUNICORN_PID=$!
echo "Started Gunicorn with PID $GUNICORN_PID"

# Start Celery Worker in the background
poetry run celery -A src.make_celery.celery_app worker --pool=solo --loglevel=INFO &
CELERY_PID=$!
echo "Started Celery with PID $CELERY_PID"

# Function to handle termination
terminate() {
    echo "Terminating processes..."
    kill $CHROMADB_PID $GUNICORN_PID $CELERY_PID
    exit 0
}

# Trap CTRL+C and other termination signals
trap terminate SIGINT SIGTERM

# Wait for all processes to finish
wait $CHROMADB_PID $GUNICORN_PID $CELERY_PID
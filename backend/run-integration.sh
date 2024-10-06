#!/bin/bash

# Kill existing processes
pkill -f 'chroma run' 2>/dev/null
pkill -f 'gunicorn' 2>/dev/null
pkill -f 'celery' 2>/dev/null

sleep 1

# Function to handle clean start
clean_backend() {
    echo "Cleaning backend files..."
    rm -rf ./chroma_data/*
    rm -rf ./chroma_db/*
    rm -rf ./textracted/* ./uploads/* ./extracted_images/*
}

# Check for the --clean argument
if [ "$1" == "--clean" ]; then
    clean_backend
fi

CHROMA_PORT=9092

poetry run chroma run --host localhost --port $CHROMA_PORT --path ./chroma_db &
CHROMA_PID=$!
echo "Started Chroma with PID $CHROMA_PID"

# Function to check if Chroma is running
check_chroma() {
    curl -s http://localhost:$CHROMA_PORT/api/v1/heartbeat > /dev/null
    return $?
}

# Wait for Chroma to be ready
echo "Waiting for Chroma to be ready..."
while ! check_chroma; do
    sleep 1
done
echo "Chroma is ready!"

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
    kill $CHROMA_PID $GUNICORN_PID $CELERY_PID
    exit 0
}

# Trap CTRL+C and other termination signals
trap terminate SIGINT SIGTERM

# Wait for all processes to finish
wait $CHROMA_PID $GUNICORN_PID $CELERY_PID
#!/bin/bash

# Start Redis server
redis-server &

# Wait for Redis to start
sleep 2

# Start Celery worker
poetry run celery -A src.make_celery worker --loglevel INFO

# This will keep the script running
wait

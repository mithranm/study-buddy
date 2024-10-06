#!/bin/bash
   rm -rf ./chroma_data/* 
   rm -rf ./chroma_db/*

   poetry run chroma run --host localhost --port 8000 --path ./chroma_db &
   CHROMA_PID=$!
   echo "Started Chroma with PID $CHROMA_PID"

   # Function to check if Chroma is running
   check_chroma() {
       curl -s http://localhost:8000/api/v1/heartbeat > /dev/null
       return $?
   }

   # Wait for Chroma to be ready
   echo "Waiting for Chroma to be ready..."
   while ! check_chroma; do
       sleep 1
   done
   echo "Chroma is ready!"

   rm -rf ./textracted/* ./uploads/* ./extracted_images/*

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
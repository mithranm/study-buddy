from celery import shared_task
import logging
from . import vector_db
from . import document_chunker as chunker
from . import socketio_app

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_file(self, file_path, textracted_path):
    """
    Processes the file and embeds it into the database.
    """
    try:
        logger.info(f"Starting to process file: {file_path}")

        # Update task state
        self.update_state(state='STARTED', meta={'status': 'Processing started'})

        # Emit an event to notify the frontend
        socketio_app.emit('task_update', {'task_id': self.request.id, 'status': 'Processing started'}, namespace='/tasks')

        collection = vector_db.get_collection()
        chunker.embed_documents([file_path], collection, textracted_path)

        logger.info(f"Successfully processed file: {file_path}")

        # Emit an event to notify completion
        socketio_app.emit('task_update', {'task_id': self.request.id, 'status': 'Task completed'}, namespace='/tasks')

        return {'status': 'Task completed'}

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")

        # Emit an event to notify error
        socketio_app.emit('task_update', {'task_id': self.request.id, 'status': f'Error: {str(e)}'}, namespace='/tasks')

        raise e

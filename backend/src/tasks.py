from celery import shared_task
import logging
from . import vector_db
from . import document_chunker as chunker

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_file(self, file_path, textracted_path):
    """
    Processes the file and embeds it into the database.

    Args:
        self: The task instance.
        file_path: Path to the uploaded file.
        textracted_path: Path to the textracted directory.
    """
    try:
        logger.info(f"Starting to process file: {file_path}")

        # Update task state
        self.update_state(state='STARTED', meta={'status': 'Processing started'})

        collection = vector_db.get_collection()
        chunker.embed_documents([file_path], collection, textracted_path)

        self.update_state(state='SUCCESS', meta={'status': 'Processing started'})

        logger.info(f"Successfully processed file: {file_path}")

        return {'status': 'Task completed'}

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        self.update_state(state='FAILURE', meta={'status': 'Processing started'})
        raise e
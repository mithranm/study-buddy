from celery import shared_task
import logging
from . import vector_db
from . import document_chunker as chunker

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_file(self, file_path, textracted_path):
    """
    Processes the file and embeds it into the database.

    Args:
        self: The task instance.
        file_path: String containing the path of the file.
        textracted_path: String containing the path to the textracted directory.

    Returns:
        None
    """
    try:
        # Log the start of the processing
        logger.info(f"Starting to process file: {file_path}")

        # Update task state
        self.update_state(state='STARTED', meta={'status': 'Processing started'})

        collection = vector_db.get_collection()
        chunker.embed_documents([file_path], collection, textracted_path)

        # Log successful processing
        logger.info(f"Successfully processed file: {file_path}")

        return {'status': 'Task completed'}

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        raise e

from celery import shared_task, current_task
import logging
# Python file imports
from . import vector_db
from . import document_chunker as chunker


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
#ASYNC METHODS
@shared_task(bind=True)
def process_file(self, file_path, textracted_path):
    """
    Where threads start to process files and embed them into the data base.

    Args:
        self: String contains filename.
        file_path: String contains the path of the file.
        textracted_path: String contains the path to the textracted directory.

    Returns:
        None
    """

    try:
        # Log the start of the processing
        logger.info(f"Starting to process file: {self}")

        self.update_state()

        collection = vector_db.get_collection()

        chunker.embed_documents([file_path], collection, textracted_path)

        # Log successful processing
        logger.info(f"Successfully processed file: {self}")

    except Exception as e:
        logger.error(f"Error processing file {self}: {str(e)}")
        # Optionally, you can raise the exception to retry the task if needed
        # raise e

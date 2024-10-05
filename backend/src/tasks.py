from celery import shared_task
import logging
# Python file imports
from . import vector_db
from . import document_chunker as chunker


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
#ASYNC METHODS
@shared_task
def process_file(filename, file_path, textracted_path):
    """
    Where threads start to process files and embed them into the data base.

    Args:
        filename: String
        collection: Database
        textracted_path: String if the file is pdf it will need this parameter.

    Returns:
        None
    """

    try:
        # Log the start of the processing
        logger.info(f"Starting to process file: {filename}")

        collection = vector_db.get_collection()

        chunker.embed_documents([file_path], collection, textracted_path)

        # Log successful processing
        logger.info(f"Successfully processed file: {filename}")

    except Exception as e:
        logger.error(f"Error processing file {filename}: {str(e)}")
        # Optionally, you can raise the exception to retry the task if needed
        # raise e

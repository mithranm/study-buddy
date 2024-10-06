# Backend

* [X] MiniLM loads for each document in uploads rather than once for all uploads.
* [X] ollama is not pulling and is trigger the exception block in initialization
* [ ] File upload validation fails to reject invalid file types, allowing them into uploads instead of returning HTTP 400.
* [ ] After deleting an invalid file and uploading a valid one, the system failed to generate embeddings for the new file and lost the embeddings of the previously deleted file.
* [ ] ChromaDB can't be on port 9092 in the Docker container for some unknown reason, it has to be in port 8000 in docker. Maybe we're not port forwarding correctly. This is not really a problem as chromadb has its own container in docker.

# Frontend

* [ ] Invalid file types should not be allowed to be selected

# Testing

* [ ] test_integration.log doesn't contain debug level logs.

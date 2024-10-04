# Backend

* [X] MiniLM loads for each document in uploads rather than once for all uploads.
* [X] ollama is not pulling and is trigger the exception block in initialization
* [ ] standalone execution of the backend will save documents in backend/src/uploads but it should be backend/uploads
* [ ] when deleting a document it doesn't actually delete it. The file is still present in system. User can delete document but search function will still use that deleted document.
* [ ] The model select dropdown doesn't actually do anything

# Frontend

# Testing

* [ ] test_integration.log doesn't contain debug level logs.

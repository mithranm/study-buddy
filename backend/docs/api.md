<a id="document_chunker"></a>

# Module document\_chunker

<a id="document_textractor"></a>

# Module document\_textractor

<a id="main"></a>

# Module main

<a id="main.upload_file"></a>

#### upload\_file

```python
@app.route('/upload', methods=['POST'])
def upload_file()
```

Uploads a file that is chosen by the user.

This function handles all POST request to the '/upload' endpoint.

**Arguments**:

  None

**Returns**:

  tuple - a json of the message and the http code
  if successful: ({'message': 'File uploaded and embedded sucessfully'}, 200)
  if backend not ready: ({'error': 'Backend is not fully initialized yet'}, 503)
  if theres no file to upload: ({'error': 'No file part'}, 400)
  if filename is empty: ({'error': 'No selected file'}, 400)

<a id="main.search_documents"></a>

#### search\_documents

```python
@app.route('/search', methods=['POST'])
def search_documents()
```

Search through submitted files to find the best matches for the given query. WE MIGHT GET RID OF THIS ENDPOINT LATER.

This function handles all POST requests to the '/search' endpoint.

**Arguments**:

  None

**Returns**:

  tuple - a json of the data and the http code
  if successful: returns the results of the prompt it was given with a status code of 200

<a id="main.list_documents"></a>

#### list\_documents

```python
@app.route('/documents', methods=['GET'])
def list_documents()
```

Retrieve all documents and return it back to the frontend in json format to be displayed on the screen.

This function handles all GET requests to '/documents' endpoint.

**Arguments**:

  None

**Returns**:

- `tuple` - a json file that contains data and http code
  if successful: sends a json of the files submitted with the http code 200.
  if backend not ready: ({error: Backend is not fully initialized yet}, 503).
  

**Raises**:

  None

<a id="main.delete_document"></a>

#### delete\_document

```python
@app.route('/documents/<filename>', methods=['DELETE'])
def delete_document(filename)
```

Delete a document and its associated chunks from the system.

This function handles HTTP DELETE requests to remove a specific document
identified by its filename. It also removes the corresponding document
chunks from the Chroma vector store.

**Arguments**:

- `filename` _str_ - The name of the file to be deleted.
  

**Returns**:

- `tuple` - A tuple containing a JSON response and an HTTP status code.
  - If successful: ({'message': 'Document deleted successfully'}, 200)
  - If backend not ready: ({'error': 'Backend is not fully initialized yet'}, 503)
  - If file not found: ({'error': 'Document not found'}, 404)
  

**Raises**:

  None


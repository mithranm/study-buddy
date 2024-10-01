<a id="document_chunker"></a>

# Module document\_chunker

<a id="document_textractor"></a>

# Module document\_textractor

<a id="main"></a>

# Module main

<a id="main.list_documents"></a>

#### list\_documents

```python
@app.route('/documents', methods=['GET'])
def list_documents()
```

Retrieve all documents and return it back to the frontend in json format to be displayed on the screen.

**Arguments**:

  None
  

**Returns**:

- `tuple` - a json file that contains data and http code
  if sucessful: sends a json of the files.
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


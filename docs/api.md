<a id="document_chunker"></a>

# Module document\_chunker

<a id="__init__"></a>

# Module \_\_init\_\_

<a id="document_textractor"></a>

# Module document\_textractor

<a id="vector_db"></a>

# Module vector\_db

<a id="vector_db.get_collection"></a>

#### get\_collection

```python
def get_collection()
```

Getter method to get the collection from the database this API is using.

**Arguments**:

  None
  

**Returns**:

  the collection of the database.

<a id="vector_db.search_documents"></a>

#### search\_documents

```python
def search_documents(query)
```

Search through submitted files to find the best matches for the given query.

This function handles all POST requests to the '/search' endpoint.

**Arguments**:

  None

**Returns**:

  tuple - a dictionary of the data and the http code
  if successful: returns the results of the prompt it was given with a status code of 200

<a id="vector_db.chat"></a>

#### chat

```python
def chat(search_results, prompt)
```

Calls Ollama endpoint api/chat with text chunk + prompt given by user.

**Arguments**:

- `search_results` - dictionary
- `prompt` - string
  

**Returns**:

  tuple - contains a json and a http code.
  if successful: return a json filled with Ollama results with the http code 200
  if ollama timeout: return ({'error': 'Ollama request timed out. The model might be taking too long to chat a response.'}), 504)
  if HTTPerror: return ({'error': 'Ollama request timed out. The model might be taking too long to chat a response.'}), 400 (maybe?))
  if RequestException: return ({'error': 'Ollama request timed out. The model might be taking too long to chat a response.'}), 500)

<a id="main"></a>

# Module main

<a id="main.is_ready"></a>

#### is\_ready

```python
def is_ready()
```

This function checks to see if the services of the system are ready.

**Arguments**:

  None
  

**Returns**:

  bool - checks if nltk AND chroma are ready.

<a id="main.get_status"></a>

#### get\_status

```python
@bp.route('/status', methods=['GET'])
def get_status()
```

Getter method for status of backend to let any application using this interface know when its ready.

**Arguments**:

  None
  

**Returns**:

  None

<a id="main.upload_file"></a>

#### upload\_file

```python
@bp.route('/upload', methods=['POST'])
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

<a id="main.search_wrapper"></a>

#### search\_wrapper

```python
@bp.route('/search', methods=['POST'])
def search_wrapper()
```

Search through submitted files to find the best matches for the given query. This is a wrapper to vector_db.search_documents()

This function handles all POST requests to the '/search' endpoint.

**Arguments**:

  None

**Returns**:

  tuple - a json of the data and the http code
  if backend not ready: returns ({'error': 'Backend is not fully initialized yet'}), 503)

<a id="main.list_documents"></a>

#### list\_documents

```python
@bp.route('/documents', methods=['GET'])
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
@bp.route('/documents/<filename>', methods=['DELETE'])
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

<a id="main.chat_wrapper"></a>

#### chat\_wrapper

```python
@bp.route('/chat', methods=['POST'])
def chat_wrapper()
```

chat an LLM response from the prompt in the request body and chunks from documents already uploaded.

**Arguments**:

  None
  

**Returns**:

- `tuple` - A tuple containing a JSON response and an HTTP status code.

**Raises**:

  None

<a id="main.create_app"></a>

#### create\_app

```python
def create_app(test_config=None)
```

Creates the app.


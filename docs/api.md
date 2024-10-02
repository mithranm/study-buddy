<a id="document_chunker"></a>

# Module document\_chunker

<a id="__init__"></a>

# Module \_\_init\_\_

<a id="document_textractor"></a>

# Module document\_textractor

<a id="vector_db"></a>

# Module vector\_db

<a id="vector_db.search_documents"></a>

#### search\_documents

```python
def search_documents()
```

Search through submitted files to find the best matches for the given query.

This function handles all POST requests to the '/search' endpoint.

**Arguments**:

  None

**Returns**:

  tuple - a json of the data and the http code
  if successful: returns the results of the prompt it was given with a status code of 200

<a id="vector_db.generate"></a>

#### generate

```python
def generate(search_results, prompt)
```

Calls ollama endpoint api/generate with text chunk + prompt given by user.

**Arguments**:

- `search_results` - json
- `prompt` - string
  

**Returns**:

  tuple - contains a json and a http code.
  if successful: pass a json filled with ollama results with the http code 200

<a id="main"></a>

# Module main


# TODO

## App

### Frontend

* [ ] Add a dropdown menu containing all available ollama models the API endpoint will be /get_models.

### Backend

#### main.py

* [ ] Work on preventing dupes from entering the system (Filename can not be the same even with different extension).
  * [ ] For now just look for the same filename if that filename exists in the chromaDB then reject upload and let the user know.
* [ ] Add a new API endpoint with the url /get_models that will return the available models.
  * [ ] This feature MUST call ollama_health_check before performing any requests to ollama server.

## Testing

* [ ] Make deletes work, right now they delete the file from uploads but they don't seem to remove the embeddings from chromadb.
* [ ] Ollama.pull currently does not work in main.py figure out how to use this function correctly.
* [X] Unit testing search function to see what it the json is. look at /backend/tests/test_main.py line 144
* [ ] Communication from backend to frontend let the frontend know when the backend is working (nltk, chromaDB)

## Documentation

* [ ] More pydocs also find a way to config pydocs to correctly document main.py with nested methods.

## Overall Design

* [ ] be able to select documents like in notebooklm. Because if user puts in some irrelavent file that they don't want ollama to use, they can deselect it
* [ ] sourcing where it found the information so look into better designing how we send payload to ollama with sources. Something like adding filename in the payload.

# TODO - Please Be Mindful Of The Differences Between Main and Develop's Version

## App

### main.py

* [ ] Work on preventing dupes from entering the system (Filename can not be the same even with different extension).
  * [ ] For now just look for the same filename if that filename exists in the chromaDB then reject upload and let the user know.

## Testing

* [X] Make deletes work, right now they delete the file from uploads but they don't seem to remove the embeddings from chromadb.
* [X] Unit testing search function to see what it the json is. look at /backend/tests/test_main.py line 144
* [ ] Communication from backend to frontend let the frontend know when the backend is working (nltk, chromaDB)

## Documentation

* [ ] More pydocs also find a way to config pydocs to correctly document main.py with nested methods.

## Overall Design

* [ ] Be able to select documents like in notebooklm. Because if user puts in some irrelavent file that they don't want ollama to use, they can deselect it
* [ ] Sourcing where it found the information so look into better designing how we send payload to ollama with sources. Something like adding filename in the payload.

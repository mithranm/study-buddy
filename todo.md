# TODO

* [ ] Work on preventing dupes from entering the system (Filename can not be the same even with different extension).

  * [ ] For now just look for the same filename if that filename exists in the chromaDB then reject upload and let the user know.
* [ ] Ollama.pull currently does not work in main.py figure out how to use this function correctly.
* [X] Unit testing search function to see what it the json is. look at /backend/tests/test_main.py line 144
* [ ] More pydocs also find a way to config pydocs to correctly document main.py with nested methods.
* [ ] Design concepts to consider:

  * [ ] be able to select documents like in notebooklm. Because if user puts in some irrelavent file that they don't want ollama to use, they can deselect it
  * [ ] sourcing where it found the information so look into better designing how we send payload to ollama with sources. Something like adding filename in the payload.

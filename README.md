# Study Buddy - Your AI Tutor

This project is in pre-release, we are looking for help on getting this into a first release ready state!

Our plans for this project is to make a fully offline and easily customizable RAG system to aid in research/studying.
## Requirements
### Hardware

* This was developed on a M1 Macbook Pro with 16gb RAM. YMMV with different hardware, we tried to keep cross-platform support in mind. We're going to expose the model choices in the frontend very soon, so you can run a model suitable for your hardware.

### Software

* Ollama (running somewhere you can access)
* Docker
* Pyenv and Poetry

## Usage

1. Clone this repo with ``git clone https://github.com/mithranm/study-buddy``
2. Rename example.env in /frontend and /backend to .env and set the OLLAMA_HOST to a valid Ollama instance.
3. Run ``docker-compose up --build `` in the project root.
4. Navigate to localhost:9091 in your browser and begin!

## Testing
### Backend
1. Navigate to /backend
2. Run ``poetry run pytest``

### Frontend
**WIP - We are looking into selenium for testing the frontend (we also need to make a good frontend)**

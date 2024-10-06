# Study Buddy - Your AI Tutor

![Screenshot of the application running.](pictures/Demo.png)

This project is in pre-release, we are looking for help on getting this into a first release ready state!

Our plans for this project is to make a fully offline and easily customizable RAG system to aid in research/studying. You control your data. Make use of your hardware.

## Requirements

### Cloud

Yes, this contradicts what we said earlier about a fully offline RAG system. But hear us out, Google is offering llama3.2vision-90b for free. You probably can't run such a model locally, so why not make use of it?

In /backend/secrets, you need to place a service-account-key.json with access to Vertex AI and set the GCP_SECRET_PATH in /backend/.env to the name of the file.

This is required for uploading .pdf. We only support .txt and .pdf currently.

### Hardware

This was developed on a M1 Macbook Pro with 16gb RAM. Your mileage shouldn't vary much with different hardware as we kept cross-platform support in mind and running ollama is your responsibility.

### Software

Running ollama is your responsibility, you can set the OLLAMA_HOST in the docker-compose.yml file. It defaults to 11434 as usual. We haven't created any executables yet, so you'll need to run the project as a Docker application.

## Docker Usage

1. Clone this repo with ``git clone https://github.com/mithranm/study-buddy``
2. Set the OLLAMA_HOST in docker-compose.yml to a valid Ollama instance (we really should have named it OLLAMA_URL, will be fixed in a future update). You have to do this for the backend service and celery_worker service.
3. Rename /backend/example.env to .env, making sure you set all the required variables.
4. Run ``docker-compose up --build `` in the project root to build for the first time.
5. Navigate to localhost:9091 in your browser and begin!
6. Press Ctrl+C to stop application
7. Run ``docker-compose down `` without our with ``-v`` to either keep your documents or delete them.

## Development

### Requirements

#### Software

* Ollama (serving on the port you configure, default is 11434)
* Redis (serving on port 6379)
* Poetry (Pyenv recommended)
* NodeJS
* Tesseract

#### Hardware/OS

Again, this was developed on an M1 Macbook Pro. Having a powerful computer is required. We aren't even sure Windows users can help develop this project. Linux should be fine.

### Instructions

We use Git Flow for development. Switch to the development branch create a feature branch off of it to start developing.

```
git switch develop
git flow feature start feature-name
# After doing your changes, commit
git flow feature finish feature-name
```

Please check if we have any feature branches in the repository already, and refrain from naming your feature that.

### Running While Developing

#### Backend

0. Have python 3.11.10 installed through pyenv
1. Navigate to /backend
2. Run ``poetry install``
3. run ``sh run-integration.sh``
    - If you have a Windows machine, we aren't even sure you can develop this project. Please contact us.
4. Congrats, the gunicorn server is running on port 9090.

#### Frontend

0. Have NodeJS v20 LTS installed
1. Navigate to /frontend
2. Run ``npm install``
3. Run ``npm start``
4. Congrats, the react app is running on port 9091.

### Unit Testing

#### Backend

1. Navigate to /backend
2. Make sure you have run ``poetry install`` before, run it if not.
3. Run ``poetry run pytest``

#### Frontend

**WIP - We are looking into selenium for testing the frontend (we also need to make a good frontend)**

# Future Updates

* We plan to fully support CUDA once we get our hands on some NVIDIA hardware. This should allow stronger embedding models to be ran using CUDAExecutionProvider
* We want to allow OpenAI generic apis to be configured as the model provider to avoid reliance on Ollama. Should allow usage of frameworks like vLLM and the OpenAI api itself.

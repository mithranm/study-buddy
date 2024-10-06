FROM python:3.11.10-slim

# Set the working directory
WORKDIR /app

# Install tesseract and clean up in the same layer
ENV PYTHONUNBUFFERED=1
RUN apt-get update \
    && apt-get -y install tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only dependency files first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Configure Poetry to create virtual environment inside the project directory
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true

# Install dependencies with cache mount
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-interaction --no-ansi

# Copy the application source code and secrets
COPY src/ ./src/
COPY secrets/ ./secrets/

# Update PATH to include the virtual environment binaries
ENV PATH="/app/.venv/bin:$PATH"

# Set PYTHONPATH
ENV PYTHONPATH=/app/src

# Expose the port the app runs on
EXPOSE 9090

# Run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:9090", "src.wsgi:app"]

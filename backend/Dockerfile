FROM python:3.11.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies and clean up in the same layer
ENV PYTHONUNBUFFERED=1
RUN apt-get update \
    && apt-get -y install tesseract-ocr supervisor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry globally
RUN pip install poetry

# Create a non-root user 'appuser' with UID and GID 1000
RUN useradd -m -u 1000 appuser

# Set ownership of the working directory to 'appuser'
RUN chown -R appuser:appuser /app

# Set HOME environment variable for 'appuser'
ENV HOME=/home/appuser

# Switch to 'appuser' to perform Poetry configuration and installation
USER appuser

# Ensure Poetry cache directory exists and is writable
RUN mkdir -p /home/appuser/.cache

# Copy only dependency files first to leverage Docker cache
COPY --chown=appuser:appuser pyproject.toml ./

# Configure Poetry to create virtual environments inside the project directory
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true

# Install dependencies with Poetry using a cache mount for efficiency
RUN --mount=type=cache,target=/home/appuser/.cache/pypoetry,uid=1000,gid=1000 \
    poetry install --no-interaction --no-ansi

# Set the NLTK data directory environment variable
ENV NLTK_DATA=/home/appuser/nltk_data

# Create the NLTK data directory
RUN mkdir -p $NLTK_DATA

# Download NLTK data as 'appuser' to the user-owned directory
RUN poetry run python -c "import nltk; nltk.download('punkt', download_dir='$NLTK_DATA')"

# Copy the application source code and secrets with proper ownership
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser secrets/ ./secrets/

# Create the upload directory and set ownership to 'appuser'
RUN mkdir -p /app/uploads && chown -R appuser:appuser /app/uploads

# Switch back to root to run Supervisord
USER root

# Copy Supervisord configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set PYTHONPATH environment variable
ENV PYTHONPATH=/app/src

# Expose the port the app runs on
EXPOSE 9090

# Use Supervisord as the entrypoint
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

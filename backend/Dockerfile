FROM python:3.11.10

# Set the working directory
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only requirements files first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the source code and necessary configuration files
COPY src/ src/

# Expose the port the app runs on
EXPOSE 9090

# Run the application as a module
CMD ["python", "-m", "src.main"]

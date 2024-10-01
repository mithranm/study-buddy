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

# Copy the rest of the application
COPY . .

# Add the src directory to PYTHONPATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Setting up write permissions for /app
RUN chmod -R 777 /app

# Install pydoc
RUN pip install pydoc-markdown

# Make app/docs
RUN mkdir -p /app/docs

# Generate docs
RUN pydoc-markdown -I /app/src > /app/docs/api.md

# Run the application
CMD ["python", "src/main.py"]
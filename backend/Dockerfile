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
# Run the application
CMD ["python", "src/main.py"]
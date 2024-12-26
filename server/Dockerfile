# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy only pyproject.toml first (not poetry.lock)
COPY pyproject.toml .

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-cache

# Copy the entire project
COPY ./app /app

# Set environment variable for GROQ API key that will be injected by docker-compose
ENV GROQ_API_KEY=${GROQ_API_KEY}

# Expose the port that the application will run on
EXPOSE 8000

# Command to run the application
CMD gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

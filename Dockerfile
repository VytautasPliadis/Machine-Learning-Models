FROM python:3.8.10-slim

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set the working directory in the container
WORKDIR /app

# Copy only pyproject.toml and (optionally) poetry.lock files
COPY pyproject.toml poetry.lock* /app/

# Install dependencies from pyproject.toml
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy the current directory contents into the container at /app
COPY . .

# Run collect_data.py when the container launches
CMD ["python", "main.py"]
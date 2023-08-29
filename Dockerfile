FROM python:3.10-slim-bullseye

WORKDIR /app

ENV POETRY_VERSION=1.4.1

RUN pip install "poetry==$POETRY_VERSION"

# Copy the dependency requirements to cache them in the docker container:
WORKDIR /app
COPY pyproject.toml /app/

# Initialize the project:
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi --without dev

RUN addgroup --system app && adduser --system --group app
USER app

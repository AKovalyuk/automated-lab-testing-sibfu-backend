FROM python:3.11-slim-buster
LABEL AUTHOR="Alex Kovalyuk"

RUN apt-get update && \
    apt-get install --no-install-recommends -y libpq-dev build-essential

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

COPY . /app
WORKDIR /app

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry config installer.max-workers 10 && \
    poetry install --no-interaction --no-ansi --no-root && \
    whoami && \
    poetry version \



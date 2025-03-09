FROM python:3.11.1-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /opt/benchmark/

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install sqlalchemy python-dotenv pydantic faker pymongo

COPY . .

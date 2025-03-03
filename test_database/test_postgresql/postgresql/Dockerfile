FROM python:3.11.1-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /opt/benchmark/

RUN apt-get update && apt-get install -y --no-install-recommends

RUN pip install psycopg2-binary sqlalchemy dotenv pydantic faker

COPY . .

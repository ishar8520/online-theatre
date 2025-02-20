FROM python:3.13.1-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /opt/benchmark

RUN apt-get update && apt-get install -y --no-install-recommends

RUN pip install dynamodb-python

COPY . .

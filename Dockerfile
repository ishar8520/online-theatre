FROM python:3.10-slim

WORKDIR /opt/app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y netcat-traditional \
    curl

COPY ./requirements.txt .
COPY ./src/ .

RUN pip3 install -r requirements.txt
ENTRYPOINT [ "fastapi", "dev", "./main.py" ] 

# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13.1

FROM python:${PYTHON_VERSION} AS venv

ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv "$VIRTUAL_ENV"
RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

FROM python:${PYTHON_VERSION}-slim

WORKDIR /opt/app

ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=venv "$VIRTUAL_ENV" "$VIRTUAL_ENV"
COPY ./movies/ ./movies

ENTRYPOINT [ "fastapi", "run", "./movies/main.py" ]

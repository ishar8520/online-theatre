# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

FROM base AS venv

ENV PATH="/root/.local/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user pipx==1.7.1
RUN pipx install poetry==1.8.5

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv "$VIRTUAL_ENV"
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=poetry.lock,target=poetry.lock \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-ansi --no-interaction

FROM base

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=venv "$VIRTUAL_ENV" "$VIRTUAL_ENV"
COPY ./etl/ ./etl/

ENTRYPOINT ["python", "./etl/app.py"]

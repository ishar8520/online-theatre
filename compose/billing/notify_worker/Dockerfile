# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONUNBUFFERED=1

WORKDIR /opt/app

FROM base AS venv

ENV PATH="/root/.local/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user pipx==1.7.1
RUN pipx install poetry==2.1.1

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv "$VIRTUAL_ENV"
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=poetry.lock,target=poetry.lock \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-ansi --no-interaction

FROM base AS common

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

FROM common

COPY --from=venv "$VIRTUAL_ENV" "$VIRTUAL_ENV"
COPY ./pyproject.toml .
COPY ./worker/ ./worker/

COPY ./docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["/opt/app/docker-entrypoint.sh"]
CMD ["python", "/opt/app/worker/main.py"]

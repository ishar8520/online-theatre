# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13.1

FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONUNBUFFERED=1

WORKDIR /opt/app

FROM base AS venv

ENV PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*


RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user pipx==1.7.1
RUN pipx install poetry==2.0.1

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv "$VIRTUAL_ENV"
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=poetry.lock,target=poetry.lock \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-ansi --no-interaction

FROM base AS common

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

FROM common AS lint

COPY --from=venv "$VIRTUAL_ENV" "$VIRTUAL_ENV"
COPY poetry.lock pyproject.toml ./
COPY ./ugc/ ./ugc/

COPY ./commands/ ./commands/
RUN chmod +x ./commands/*.sh

EXPOSE 5002

CMD ["/opt/app/commands/hypercorn.sh"]

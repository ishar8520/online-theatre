# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13.1

FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONUNBUFFERED=1

WORKDIR /opt/app

FROM base AS venv

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv "$VIRTUAL_ENV"
RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

FROM base

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=venv "$VIRTUAL_ENV" "$VIRTUAL_ENV"
COPY ./ ./

ENTRYPOINT [ "python3", "./main.py" ]

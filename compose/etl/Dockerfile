# syntax=docker/dockerfile:1

FROM python:3.12.7-bookworm as base

ENV PYTHONUNBUFFERED=1

WORKDIR /opt/app

FROM base as venv

ENV PATH="/root/.local/bin:$PATH"

RUN pip install --user pipx==1.7.1
RUN pipx install poetry==1.8.4

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m venv "$VIRTUAL_ENV"

COPY ./pyproject.toml .
COPY ./poetry.lock .
RUN poetry install --no-ansi --no-interaction

FROM base

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY --from=venv "$VIRTUAL_ENV" "$VIRTUAL_ENV"

COPY ./schema/ ./schema/
COPY ./etl/ ./etl/

VOLUME /opt/app/data
VOLUME /opt/app/logs

ENTRYPOINT ["python", "./etl/commands/transfer_data.py"]

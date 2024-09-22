# syntax=docker/dockerfile:1
FROM python:3.12-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir /opt/alafi
WORKDIR /opt/alafi/

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -qy gettext wget git curl && \
    apt-get autoremove -qy && \
    apt-get autoclean -qy

COPY pyproject.toml pdm.lock .

RUN --mount=type=cache,target=/root/.cache \
    --mount=type=cache,target=/root/.cache/pip \
    --mount=type=secret,id=gitlab-token \
    --mount=type=secret,id=gitlab-user \
    pip install "pdm<3" && \
    pdm sync --global --project . --production -G:all --no-self --fail-fast

ENTRYPOINT ["python", "manage.py"]

FROM base as prod
COPY . .

FROM base as dev

RUN --mount=type=cache,target=/root/.cache \
    --mount=type=cache,target=/root/.cache/pip \
    pdm install --global --project . --dev --fail-fast --no-lock --no-default

RUN pdm config python.use_venv false

COPY . .

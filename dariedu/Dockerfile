FROM python:3.10.5-slim-bullseye

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libc6-dev \
    libffi-dev \
    libpq-dev \
    postgresql-client \
    redis-tools
RUN pip install gunicorn
RUN pip install psycopg2-binary
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y postgresql-client redis-tools


ENV DJANGO_SETTINGS_MODULE=dariedu.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/src/app

ARG HOST_UID
ARG HOST_GID
RUN groupadd -g ${HOST_GID} celeryuser && useradd -u ${HOST_UID} -g celeryuser -ms /bin/bash celeryuser

RUN mkdir -p /usr/src/app/media /usr/src/app/staticfiles && \
    chmod -R 755 /usr/src/app && \
    chmod g+s /usr/src/app /usr/src/app/media /usr/src/app/staticfiles && \
    chown -R celeryuser:celeryuser /usr/src/app


USER celeryuser

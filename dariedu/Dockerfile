FROM python:3.10.5

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY credentials.json ./
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

COPY . .

ENV DJANGO_SETTINGS_MODULE=dariedu.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN useradd -ms /bin/bash celeryuser
RUN chown -R celeryuser:celeryuser /usr/src/app
RUN chown -R celeryuser:celeryuser /usr/src/app/media/
RUN chown -R celeryuser:celeryuser /usr/src/app/media

USER celeryuser

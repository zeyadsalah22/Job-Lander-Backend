ARG PYTHON_VERSION=3.12-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt

RUN apt-get update && apt-get install -y \
    libmariadb-dev-compat \
    libmariadb-dev \
    pkg-config \
    gcc \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

COPY . /code

ENV SECRET_KEY "JcyznjNf7zAlSma1o5V9XdUV2bblZUx8cFmdumUNzpJJQ0Avz2"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "joblander.wsgi"]

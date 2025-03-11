FROM python:3.11.10-slim-bullseye

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY ./poetry.lock /opt/app
COPY ./pyproject.toml /opt/app

RUN python -m pip install --no-cache-dir poetry==1.8.5 \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi \ 
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY ./src /opt/app

ENTRYPOINT ["python3", "/opt/app/main.py"]

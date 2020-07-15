FROM python:3.7.8

ENV PYTHONUNBUFFERED 1
EXPOSE 8000

COPY poetry.lock pyproject.toml /
RUN pip install poetry \
  && poetry config virtualenvs.create false \
  && poetry install --no-dev --no-root

COPY app /app
WORKDIR /app

COPY docker-entrypoint.sh /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]

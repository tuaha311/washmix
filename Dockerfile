FROM python:3.7.8

ENV PYTHONUNBUFFERED 1
EXPOSE 8000

COPY docker-entrypoint.sh /docker-entrypoint.sh

COPY poetry.lock pyproject.toml /
RUN pip install poetry \
  && poetry config virtualenvs.create false \
  && poetry install --no-dev --no-root \
  # temporary solution (legacy package)
  && pip install djangorestframework-expiring-authtoken==0.1.4

COPY app /app
WORKDIR /app

CMD ["/bin/bash", "/docker-entrypoint.sh"]
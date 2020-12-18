FROM python:3.7.9

# Requirements for Weasyprint
RUN sudo apt-get install build-essential /
                         python3-wheel /
                         python3-cffi /
                         libcairo2 /
                         libpango-1.0-0 /
                         libpangocairo-1.0-0 /
                         libgdk-pixbuf2.0-0 /
                         libffi-dev /
                         shared-mime-info

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

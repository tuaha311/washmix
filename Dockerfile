FROM python:3.7.9

### Requirements for Weasyprint
RUN apt-get update && apt-get install -y libcairo2 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 \
  libffi-dev \
  shared-mime-info \
  ### Added for use exec command (open container console) in Heroku
  openssh-server \
  ###
  && rm -rf /var/lib/apt/lists/*

### Added for use exec command (open container console) in Heroku
RUN rm /bin/sh \
 && ln -s /bin/bash /bin/sh \
 && mkdir -p /app/.profile.d/ \
 && printf '#!/usr/bin/env bash\n\nset +o posix\n\n[ -z "$SSH_CLIENT" ] && source <(curl --fail --retry 7 -sSL "$HEROKU_EXEC_URL")\n' > /app/.profile.d/heroku-exec.sh \
 && chmod +x /app/.profile.d/heroku-exec.sh
###

ENV PYTHONUNBUFFERED 1

COPY poetry.lock pyproject.toml /
RUN pip install poetry \
  && poetry config virtualenvs.create false \
  && poetry install --no-dev --no-root

COPY app /app
WORKDIR /app

COPY docker-entrypoint.sh /docker-entrypoint.sh

CMD ["/docker-entrypoint.sh"]

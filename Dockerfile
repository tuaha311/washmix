FROM python:3.6
ENV PYTHONUNBUFFERED 1

# Add code directory to house application code
RUN mkdir /code
WORKDIR /code
ADD . /code/

# Copy in requirements.txt
COPY requirements.txt /code

# Install necessary packages/libraries
RUN pip install -r /code/requirements.txt

# uWSGI will listen on this port
EXPOSE 8000

# Start uWSGI
CMD ["/venv/bin/uwsgi", "--http-auto-chunked", "--http-keepalive"]
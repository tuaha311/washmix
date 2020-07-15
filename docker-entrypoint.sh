#!/bin/bash

set -e

sleep 5

python manage.py migrate --settings settings.dev

gunicorn --bind 0.0.0.0:8000 --workers 2 settings.wsgi:application

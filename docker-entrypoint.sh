#!/bin/bash

set -e

sleep 5

python manage.py migrate --settings settings.dev
python manage.py collectstatic --settings settings.dev --noinput
python manage.py fill_packages --settings settings.dev
python manage.py fill_cities --settings settings.dev --noinput

gunicorn --bind 0.0.0.0:8000 --workers 2 settings.wsgi:application

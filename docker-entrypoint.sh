#!/bin/bash

set -e

action=$1

cd app

if [ "$action" = "worker" ]
then
  echo "Running dramatiq worker"
  dramatiq --threads 1 --processes 1 -v settings.dramatiq

elif [ "$action" = "migrations" ]
then
  echo "Running migrations"
  python manage.py migrate --noinput

elif [ "$action" = "scheduler" ]
then
  echo "Running periodiq scheduler"
  periodiq -v settings.dramatiq

else
  echo "Running django application"
  python manage.py collectstatic --noinput
  ###Added for use in Heroku
  if [ -n "$PORT" ]
  then
    gunicorn --bind 0.0.0.0:${PORT} --workers 3 settings.wsgi:application
  else
    gunicorn --bind 0.0.0.0:8000 --workers 3 settings.wsgi:application
  fi
fi

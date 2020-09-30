#!/bin/bash

set -e

action=$1

if [ "$action" = "worker" ]
then
  echo "Running dramatiq worker"
  dramatiq -v settings.dramatiq

elif [ "$action" = "migrations" ]
then
  echo "Running migrations"
  python manage.py migrate --settings settings.staging --noinput

elif [ "$action" = "scheduler" ]
then
  echo "Running periodiq scheduler"
  periodiq -v settings.dramatiq

else
  echo "Running django application"
  python manage.py collectstatic --settings settings.staging --noinput
  python manage.py fill --settings settings.staging
  gunicorn --bind 0.0.0.0:8000 --workers 2 settings.wsgi:application
fi

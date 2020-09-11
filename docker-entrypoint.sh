#!/bin/bash

set -e

action=$1

if [ "$action" = "worker" ]
then
  echo "Running dramatiq worker"
  python manage.py rundramatiq --reload -p 2 --settings settings.dev

elif [ "$action" = "migrations" ]
then
  echo "Running migrations and initial scripts"
  python manage.py migrate --settings settings.staging
  python manage.py collectstatic --settings settings.staging
  python manage.py fill --settings settings.staging

else
  echo "Running django application"
  gunicorn --bind 0.0.0.0:8000 --workers 2 settings.wsgi:application
fi

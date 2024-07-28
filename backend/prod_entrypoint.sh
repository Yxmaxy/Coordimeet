#!/bin/sh

python manage.py migrate --no-input
python manage.py collectstatic --noinput

gunicorn coordimeet.wsgi:application --bind 0.0.0.0:8000

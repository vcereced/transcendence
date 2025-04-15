#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! nc -z game_db 5432; do
  sleep 1
done
echo "PostgreSQL is available."


echo "Making migrations..."
python manage.py makemigrations game_app


echo "Migrating database..."
python manage.py migrate


echo "Starting drf server..."
# exec python manage.py runserver 0.0.0.0:8004 COMMENTED BY GARYDD1
exec gunicorn game_.wsgi:application --bind 0.0.0:8004
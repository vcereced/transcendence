#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! nc -z tournaments_db 5432; do
  sleep 1
done
echo "PostgreSQL is available."


echo "Making migrations..."
python manage.py makemigrations tournaments_app


echo "Migrating database..."
python manage.py migrate


echo "Starting drf server..."
exec gunicorn tournaments_project.wsgi:application --bind 0.0.0.0:8003
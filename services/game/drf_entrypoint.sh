#!/bin/sh

# echo "Waiting for Postgres..."
# while ! nc -z order-db 5432; do
#   sleep 1
# done
# echo "Postgres is available."


echo "Making migrations..."
python manage.py makemigrations game_app


echo "Migrating database..."
python manage.py migrate


echo "Starting drf server..."
exec python manage.py runserver 0.0.0.0:8004
#!/bin/sh

echo "Waiting for RabbitMQ..."
while ! nc -z message-broker 5672; do
  sleep 1
done
echo "RabbitMQ is available."


echo "Waiting for Postgres..."
while ! nc -z tournament-db 5432; do
  sleep 1
done
echo "Postgres is available."


echo "Making migrations..."
python manage.py makemigrations tournament_app


echo "Migrating database..."
python manage.py migrate


echo "Starting drf server..."
exec python manage.py runserver 0.0.0.0:8000
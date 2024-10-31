#!/bin/sh

echo "Waiting for RabbitMQ..."
while ! nc -z message-broker 5672; do
  sleep 1
done
echo "RabbitMQ is available."


echo "Waiting for Postgres..."
while ! nc -z user-db 5432; do
  sleep 1
done
echo "Postgres is available."


echo "Starting Celery worker..."
exec celery -A user_service worker --loglevel=info --concurrency=4 -Q tournament_events

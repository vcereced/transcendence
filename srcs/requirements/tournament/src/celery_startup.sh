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


echo "Starting Celery worker..."
celery -A tournament_service worker --loglevel=info --concurrency=4 -Q user_events

#!/bin/sh

echo "Waiting for RabbitMQ..."
while ! nc -z message-broker 5672; do
  sleep 1
done
echo "RabbitMQ is available."


echo "Waiting for PostgreSQL..."
while ! nc -z tournaments_db 5432; do
  sleep 1
done
echo "PostgreSQL is available."


echo "Starting Matchmaking Celery worker..."
exec celery -A tournaments_project worker --loglevel=info  -Q matchmaking_tasks
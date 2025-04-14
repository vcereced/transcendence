#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! nc -z game_db 5432; do
  sleep 1
done
echo "PostgreSQL is available."


echo "Starting daphne server..."
daphne -b 0.0.0.0 -p 8005 game.asgi:application
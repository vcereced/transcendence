#!/bin/sh

# echo "Waiting for Postgres..."
# while ! nc -z order-db 5432; do
#   sleep 1
# done
# echo "Postgres is available."


echo "Starting daphne server..."
daphne -b 0.0.0.0 -p 8005 game.asgi:application
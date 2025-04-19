#!/bin/sh

echo "Waiting for RabbitMQ..."
while ! nc -z message-broker 5672; do
  sleep 1
done
echo "RabbitMQ is available."


echo "Waiting for PostgreSQL..."
while ! nc -z game_db 5432; do
  sleep 1
done
echo "PostgreSQL is available."


echo "Starting Celery worker..."
exec celery -A game worker --loglevel=info --concurrency=4 -Q game_tasks

# #!/bin/bash

# # Crear un usuario no root (si no existe)
# USER_NAME="celeryuser"
# if ! id "$USER_NAME" &>/dev/null; then
#   echo "Creating user $USER_NAME..."
#   useradd -m -s /bin/bash "$USER_NAME" || true
# fi

# # Esperar a que RabbitMQ esté disponible
# echo "Waiting for RabbitMQ..."
# while ! nc -z message-broker 5672; do
#   sleep 1
# done
# echo "RabbitMQ is available."

# # Esperar a que PostgreSQL esté disponible
# echo "Waiting for PostgreSQL..."
# while ! nc -z game_db 5432; do
#   sleep 1
# done
# echo "PostgreSQL is available."

# # Cambiar al usuario no root
# echo "Switching to user $USER_NAME..."
# exec su - "$USER_NAME" -c "celery -A game worker --loglevel=info --concurrency=4 -Q game_tasks"

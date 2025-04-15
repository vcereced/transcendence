#!/bin/bash

# Esperar a que la base de datos esté lista (solo si usas PostgreSQL o MySQL)
echo "Waiting for PostgreSQL..."
while ! nc -z auth_db 5432; do
  sleep 1
done
echo "PostgreSQL is available."

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Ejecutar el servidor
exec python manage.py runserver 0.0.0.0:8001
#exec gunicorn auth_project.wsgi:application --bind 0.0.0:8001
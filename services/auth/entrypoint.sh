#!/bin/bash

# Esperar a que la base de datos esté lista (solo si usas PostgreSQL o MySQL)
sleep 5

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Ejecutar el servidor
exec python manage.py runserver 0.0.0.0:8001
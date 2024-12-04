# Usa una imagen base de Python (versión específica para estabilidad)
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos al contenedor
COPY requirements.txt /app/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala las dependencias necesarias
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de la aplicación en el contenedor
COPY . /app/

# Expone el puerto de la aplicación
EXPOSE 8002

# Comando de inicio para el servidor ASGI
CMD ["daphne", "-b", "0.0.0.0", "-p", "8002", "websocket_project.asgi:application"]

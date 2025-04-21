FROM python:3.10-slim

# Evita mensajes interactivos durante la instalación de paquetes
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los requirements
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación
COPY . .

# Agrega permisos de ejecución al entrypoint
RUN chmod +x drf_entrypoint.sh

CMD ["/bin/sh", "drf_entrypoint.sh"]

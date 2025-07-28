FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY sistema_gestion_agricola/requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY sistema_gestion_agricola/ .

# Crear directorio para assets estáticos
RUN mkdir -p static/dist

# Exponer puerto
EXPOSE 5000

# Variables de entorno
ENV FLASK_APP=run.py
ENV PYTHONPATH=/app

# Comando de inicio
CMD ["python", "run.py"]
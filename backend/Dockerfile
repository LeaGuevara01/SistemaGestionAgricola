# 🐍 Backend Dockerfile - Multi-stage para optimización
FROM python:3.11-slim as base

# Metadatos
LABEL maintainer="Sistema Gestión Agrícola"
LABEL version="1.0.0"
LABEL description="Backend Flask para Sistema de Gestión Agrícola"

# Variables de entorno Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ===== STAGE: Development =====
FROM base as development

WORKDIR /app

# Copiar requirements primero (cache layer)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar código de aplicación
COPY --chown=appuser:appuser . .

# Crear directorios necesarios
RUN mkdir -p static/fotos/componentes static/fotos/maquinas static/uploads static/dist && \
    chown -R appuser:appuser static/

USER appuser

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "run.py"]

# ===== STAGE: Production =====
FROM base as production

WORKDIR /app

# Instalar dependencias de producción
COPY requirements.txt .
RUN pip install --no-dev -r requirements.txt

# Copiar solo archivos necesarios
COPY --chown=appuser:appuser config.py run.py ./
COPY --chown=appuser:appuser backend/ backend/
COPY --chown=appuser:appuser static/ static/

# Crear directorios con permisos
RUN mkdir -p static/fotos/componentes static/fotos/maquinas static/uploads static/dist && \
    chown -R appuser:appuser static/

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "run.py"]

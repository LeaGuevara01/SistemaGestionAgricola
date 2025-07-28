# ⚛️ Frontend Dockerfile - Multi-stage para desarrollo y producción
FROM node:18-alpine as base

# Metadatos
LABEL maintainer="Sistema Gestión Agrícola"
LABEL version="1.0.0"
LABEL description="Frontend React para Sistema de Gestión Agrícola"

# Instalar dependencias del sistema
RUN apk add --no-cache curl dumb-init

WORKDIR /app

# ===== STAGE: Dependencies =====
FROM base as dependencies

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci && npm cache clean --force

# ===== STAGE: Development =====
FROM base as development

# Copiar dependencias desde stage anterior
COPY --from=dependencies /app/node_modules ./node_modules

# Copiar código fuente
COPY . .

# Crear usuario no-root
RUN addgroup -g 1001 -S nodejs && \
    adduser -S reactjs -u 1001

# Cambiar permisos
RUN chown -R reactjs:nodejs /app
USER reactjs

EXPOSE 5173

# Health check para desarrollo
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5173 || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

# ===== STAGE: Builder =====
FROM base as builder

# Copiar dependencias
COPY --from=dependencies /app/node_modules ./node_modules

# Copiar código fuente
COPY . .

# Build para producción
ENV NODE_ENV=production
RUN npm run build

# ===== STAGE: Production =====
FROM nginx:alpine as production

# Copiar archivos built desde builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuración de nginx personalizada
RUN echo 'server { \
    listen 3000; \
    server_name localhost; \
    location / { \
    root /usr/share/nginx/html; \
    index index.html index.htm; \
    try_files $uri $uri/ /index.html; \
    } \
    location /api { \
    proxy_pass http://backend:5000; \
    proxy_set_header Host $host; \
    proxy_set_header X-Real-IP $remote_addr; \
    } \
    }' > /etc/nginx/conf.d/default.conf

# Health check para producción
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
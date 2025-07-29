# 🚀 Guía de Deployment en Render.com

## 📋 Pre-requisitos

1. Cuenta en [Render.com](https://render.com)
2. Código en GitHub/GitLab
3. Variables de entorno configuradas

## 🛠️ Configuración en Render

### 1. Crear PostgreSQL Database

1. En Render Dashboard → "New" → "PostgreSQL"
2. Configurar:
   - **Name**: `elorza-db`
   - **Database**: `sistema_gestion_agricola`
   - **User**: `elorza`

### 2. Crear Web Service

1. En Render Dashboard → "New" → "Web Service"
2. Conectar repository de GitHub
3. Configurar:
   - **Name**: `elorza-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`

### 3. Variables de Entorno en Render

Agregar en "Environment Variables":

```bash
# Obligatorias
DATABASE_URL=<URL_AUTOMATICA_DE_RENDER_POSTGRESQL>
SECRET_KEY=<GENERAR_CLAVE_SEGURA_32_CARACTERES>
FLASK_ENV=production

# Opcionales
WEATHER_API_KEY=<TU_API_KEY_OPENWEATHERMAP>
PORT=5000
```

### 4. Configurar Frontend (Opcional)

Para servir React desde Render:

1. Crear otro Web Service para frontend
2. **Build Command**: `cd frontend && npm install && npm run build`
3. **Start Command**: `cd frontend && npx serve -s dist -l 3000`

## 🔄 Auto-deployment

- Render detecta cambios en `main` branch automáticamente
- Se ejecuta build y deployment automático
- Logs disponibles en Dashboard

## 🧪 Verificar Deployment

1. Visitar URL de Render
2. Probar endpoints:
   - `https://tu-app.onrender.com/health`
   - `https://tu-app.onrender.com/test`
   - `https://tu-app.onrender.com/api/v1/componentes/test`

## ⚠️ Consideraciones

- **Free tier**: App duerme tras 15 min inactividad
- **Cold start**: Primera request puede tardar 30+ segundos
- **Database**: 90 días de retención en plan gratuito
- **SSL**: Automático con certificado gratuito

## 🏗️ Estructura de Archivos para Render

```
elorza/
├── requirements.txt     ← Dependencias Python
├── run.py              ← Punto de entrada
├── config.py           ← Configuración centralizada
├── render.yaml         ← Configuración Render (opcional)
├── .env.example        ← Template variables entorno
└── backend/
    └── app/            ← Aplicación Flask
```

## 🔍 Troubleshooting

- **Error 503**: App durmiendo, esperar cold start
- **Database connection**: Verificar DATABASE_URL
- **Secret key**: Asegurar SECRET_KEY ≥ 32 caracteres
- **Static files**: Configurar rutas estáticas correctamente

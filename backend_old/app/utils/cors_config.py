"""
Configuración de CORS profesional por ambiente
"""
import os
from flask_cors import CORS
from typing import List, Dict, Any


class CORSConfig:
    """Configuración de CORS según el ambiente"""
    
    # Orígenes permitidos por ambiente
    DEVELOPMENT_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5173',  # Vite default
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
        'http://localhost:8080',  # Vue CLI default
        'http://127.0.0.1:8080'
    ]
    
    PRODUCTION_ORIGINS = [
        'https://elorza-frontend.onrender.com',  # Render frontend
        'https://sistema-gestion-agricola.com',  # Dominio personalizado
        # Agregar otros dominios de producción aquí
    ]
    
    # Headers permitidos
    ALLOWED_HEADERS = [
        'Content-Type',
        'Authorization',
        'X-Requested-With',
        'Accept',
        'Origin',
        'Cache-Control',
        'X-File-Name'
    ]
    
    # Métodos HTTP permitidos
    ALLOWED_METHODS = [
        'GET',
        'POST',
        'PUT',
        'PATCH',
        'DELETE',
        'OPTIONS'
    ]
    
    # Headers expuestos al cliente
    EXPOSED_HEADERS = [
        'Content-Range',
        'X-Content-Range',
        'X-Total-Count'
    ]

def get_cors_origins() -> List[str]:
    """Obtener orígenes permitidos según el ambiente"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        # En producción, usar variable de entorno si está disponible
        custom_origins = os.getenv('CORS_ORIGINS')
        if custom_origins:
            return custom_origins.split(',')
        return CORSConfig.PRODUCTION_ORIGINS
    else:
        # En desarrollo, permitir orígenes de desarrollo
        return CORSConfig.DEVELOPMENT_ORIGINS

def configure_cors(app) -> CORS:
    """Configurar CORS para la aplicación"""
    
    env = os.getenv('FLASK_ENV', 'development')
    origins = get_cors_origins()
    
    # Configuración base de CORS
    cors_config = {
        'origins': origins,
        'methods': CORSConfig.ALLOWED_METHODS,
        'allow_headers': CORSConfig.ALLOWED_HEADERS,
        'expose_headers': CORSConfig.EXPOSED_HEADERS,
        'supports_credentials': True,  # Para cookies/auth
        'max_age': 86400,  # Cache preflight por 24 horas
    }
    
    # Configuraciones específicas por ambiente
    if env == 'production':
        # En producción, ser más restrictivo
        cors_config.update({
            'send_wildcard': False,  # No enviar Access-Control-Allow-Origin: *
            'vary_header': True,     # Agregar Vary: Origin header
        })
        
        # Log de configuración de producción
        app.logger.info(f"CORS configurado para producción con orígenes: {origins}")
    else:
        # En desarrollo, ser más permisivo para facilitar desarrollo
        cors_config.update({
            'send_wildcard': False,  # Mantener false para seguridad
            'automatic_options': True,  # Manejar preflight automáticamente
        })
        
        app.logger.info(f"CORS configurado para desarrollo con orígenes: {origins}")
    
    # Aplicar configuración CORS
    cors = CORS(app, **cors_config)
    
    # Configuración específica para rutas API
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": origins,
            "methods": CORSConfig.ALLOWED_METHODS,
            "allow_headers": CORSConfig.ALLOWED_HEADERS
        }
    })
    
    return cors

def validate_origin(origin: str) -> bool:
    """Validar si un origen está permitido"""
    allowed_origins = get_cors_origins()
    return origin in allowed_origins

def get_cors_headers(origin: str = None) -> Dict[str, str]:
    """Obtener headers CORS manualmente si es necesario"""
    headers = {}
    
    if origin and validate_origin(origin):
        headers['Access-Control-Allow-Origin'] = origin
        headers['Access-Control-Allow-Methods'] = ', '.join(CORSConfig.ALLOWED_METHODS)
        headers['Access-Control-Allow-Headers'] = ', '.join(CORSConfig.ALLOWED_HEADERS)
        headers['Access-Control-Expose-Headers'] = ', '.join(CORSConfig.EXPOSED_HEADERS)
        headers['Access-Control-Allow-Credentials'] = 'true'
        headers['Access-Control-Max-Age'] = '86400'
    
    return headers

# Decorator para endpoints que necesitan CORS personalizado
def cors_enabled(origins: List[str] = None):
    """Decorator para habilitar CORS en endpoints específicos"""
    def decorator(f):
        def wrapped(*args, **kwargs):
            from flask import request, make_response
            
            # Obtener origen de la request
            origin = request.headers.get('Origin')
            
            # Validar origen
            allowed_origins = origins or get_cors_origins()
            if origin not in allowed_origins:
                return {'error': 'Origen no permitido'}, 403
            
            # Ejecutar función original
            response = make_response(f(*args, **kwargs))
            
            # Agregar headers CORS
            cors_headers = get_cors_headers(origin)
            for header, value in cors_headers.items():
                response.headers[header] = value
            
            return response
        return wrapped
    return decorator

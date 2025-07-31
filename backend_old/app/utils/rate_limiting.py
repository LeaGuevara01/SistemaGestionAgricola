"""
Configuración de Rate Limiting profesional
"""
import os
from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from typing import Callable, Optional
from .exceptions import RateLimitExceededError


class RateLimitConfig:
    """Configuración de límites de velocidad"""
    
    # Límites por ambiente
    DEVELOPMENT_LIMITS = {
        'global': '1000 per hour',
        'api': '500 per hour',
        'auth': '20 per minute',
        'upload': '10 per minute',
        'search': '100 per hour',
        'heavy': '50 per hour'  # Para operaciones pesadas
    }
    
    PRODUCTION_LIMITS = {
        'global': '500 per hour',
        'api': '300 per hour', 
        'auth': '10 per minute',
        'upload': '5 per minute',
        'search': '50 per hour',
        'heavy': '20 per hour'
    }

def get_rate_limits():
    """Obtener límites según el ambiente"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return RateLimitConfig.PRODUCTION_LIMITS
    else:
        return RateLimitConfig.DEVELOPMENT_LIMITS

def get_user_id() -> str:
    """Obtener identificador único del usuario para rate limiting"""
    # Por ahora usar IP, en el futuro se puede usar user_id de sesión
    user_id = request.headers.get('X-User-ID')
    if user_id:
        return f"user:{user_id}"
    
    # Fallback a IP
    ip = get_remote_address()
    return f"ip:{ip}"

def rate_limit_exceeded_handler(error):
    """Handler personalizado para errores de rate limit"""
    
    # Obtener información del límite
    retry_after = getattr(error, 'retry_after', None)
    limit = getattr(error, 'limit', None)
    
    # Log del evento
    from .logging_config import get_logger
    logger = get_logger('rate_limit')
    
    logger.warning(
        "Rate limit exceeded",
        ip=get_remote_address(),
        user_agent=request.headers.get('User-Agent'),
        endpoint=request.endpoint,
        limit=str(limit) if limit else None,
        retry_after=retry_after
    )
    
    # Crear excepción personalizada
    exception = RateLimitExceededError(retry_after=retry_after)
    
    response = jsonify(exception.to_dict())
    response.status_code = 429
    
    # Agregar headers de rate limiting
    if retry_after:
        response.headers['Retry-After'] = str(retry_after)
    if limit:
        response.headers['X-RateLimit-Limit'] = str(limit.limit)
        response.headers['X-RateLimit-Remaining'] = str(limit.remaining)
        response.headers['X-RateLimit-Reset'] = str(limit.reset_at)
    
    return response

def configure_rate_limiting(app) -> Limiter:
    """Configurar rate limiting para la aplicación"""
    
    # Obtener límites según ambiente
    limits = get_rate_limits()
    
    # Configurar Limiter
    limiter = Limiter(
        app=app,
        key_func=get_user_id,
        default_limits=[limits['global']],
        storage_uri=os.getenv('REDIS_URL', 'memory://'),  # Redis en producción, memoria en desarrollo
        strategy='fixed-window',  # Estrategia de ventana fija
        headers_enabled=True,  # Habilitar headers de rate limit
        swallow_errors=True,  # No romper la app si falla el rate limiting
        on_breach=rate_limit_exceeded_handler
    )
    
    # Log de configuración
    env = os.getenv('FLASK_ENV', 'development')
    storage = 'Redis' if os.getenv('REDIS_URL') else 'Memory'
    
    app.logger.info(
        f"Rate limiting configurado para {env}: "
        f"Storage={storage}, Límites={limits}"
    )
    
    return limiter

# Decorators para diferentes tipos de límites
def api_rate_limit(limiter: Limiter):
    """Rate limit para endpoints de API"""
    limits = get_rate_limits()
    return limiter.limit(limits['api'])

def auth_rate_limit(limiter: Limiter):
    """Rate limit para endpoints de autenticación"""
    limits = get_rate_limits()
    return limiter.limit(limits['auth'])

def upload_rate_limit(limiter: Limiter):
    """Rate limit para endpoints de upload"""
    limits = get_rate_limits()
    return limiter.limit(limits['upload'])

def search_rate_limit(limiter: Limiter):
    """Rate limit para endpoints de búsqueda"""
    limits = get_rate_limits()
    return limiter.limit(limits['search'])

def heavy_operation_rate_limit(limiter: Limiter):
    """Rate limit para operaciones pesadas"""
    limits = get_rate_limits()
    return limiter.limit(limits['heavy'])

# Rate limits específicos por IP para endpoints sensibles
def strict_rate_limit(limiter: Limiter, limit: str = "5 per minute"):
    """Rate limit estricto para operaciones sensibles"""
    return limiter.limit(limit, key_func=get_remote_address)

# Decorator personalizado para rate limiting condicional
def conditional_rate_limit(limiter: Limiter, condition_func: Callable = None):
    """Rate limit condicional basado en una función"""
    def decorator(f):
        def wrapped(*args, **kwargs):
            # Aplicar rate limit solo si se cumple la condición
            if condition_func and not condition_func():
                return f(*args, **kwargs)
            
            # Aplicar rate limit normal
            return api_rate_limit(limiter)(f)(*args, **kwargs)
        return wrapped
    return decorator

# Función para verificar si un usuario está en whitelist
def is_whitelisted_user() -> bool:
    """Verificar si el usuario está en whitelist para rate limiting"""
    user_id = request.headers.get('X-User-ID')
    ip = get_remote_address()
    
    # Lista de IPs/usuarios whitelisteados
    whitelist_ips = os.getenv('RATE_LIMIT_WHITELIST_IPS', '').split(',')
    whitelist_users = os.getenv('RATE_LIMIT_WHITELIST_USERS', '').split(',')
    
    return (
        ip in whitelist_ips or 
        user_id in whitelist_users or
        ip.startswith('127.0.0.1') or  # Localhost siempre whitelisteado en desarrollo
        (os.getenv('FLASK_ENV') == 'development' and ip.startswith('192.168.'))
    )

# Clase para manejar rate limiting dinámico
class DynamicRateLimit:
    """Rate limiting dinámico basado en carga del sistema"""
    
    def __init__(self, limiter: Limiter):
        self.limiter = limiter
        self.base_limits = get_rate_limits()
    
    def get_dynamic_limit(self, endpoint_type: str) -> str:
        """Obtener límite dinámico basado en la carga del sistema"""
        base_limit = self.base_limits.get(endpoint_type, self.base_limits['api'])
        
        # En el futuro se puede implementar lógica para ajustar límites
        # basado en métricas del sistema como CPU, memoria, etc.
        
        return base_limit
    
    def apply_limit(self, endpoint_type: str):
        """Aplicar límite dinámico"""
        limit = self.get_dynamic_limit(endpoint_type)
        return self.limiter.limit(limit)

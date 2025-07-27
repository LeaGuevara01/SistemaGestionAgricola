# middleware/rate_limiting.py
from flask import request
import time
from collections import defaultdict, deque

class SimpleRateLimiter:
    """Rate limiter simple en memoria para desarrollo"""
    def __init__(self):
        self.requests = defaultdict(deque)
        self.blocked_ips = {}
    
    def is_allowed(self, identifier, max_requests=500, window=60):
        """
        Verifica si una IP puede hacer la petición
        max_requests: máximo número de peticiones (aumentado a 500)
        window: ventana de tiempo en segundos (reducido a 60 segundos)
        """
        now = time.time()
        
        # Permitir localhost sin límites en desarrollo
        if identifier in ['127.0.0.1', 'localhost', '::1']:
            return True
        
        # Limpiar peticiones antiguas
        while self.requests[identifier] and self.requests[identifier][0] < now - window:
            self.requests[identifier].popleft()
        
        # Verificar si está bloqueado
        if identifier in self.blocked_ips:
            if now < self.blocked_ips[identifier]:
                return False
            else:
                del self.blocked_ips[identifier]
        
        # Verificar límite
        if len(self.requests[identifier]) >= max_requests:
            # Bloquear por 5 minutos (reducido de 1 hora)
            self.blocked_ips[identifier] = now + 300
            return False
        
        # Registrar petición
        self.requests[identifier].append(now)
        return True

# Instancia global
simple_limiter = SimpleRateLimiter()

def get_client_ip():
    """Obtiene la IP real del cliente considerando proxies"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        return request.environ['HTTP_X_REAL_IP']
    else:
        return request.environ.get('REMOTE_ADDR', '127.0.0.1')

def create_limiter(app):
    """Crea el limitador según el entorno"""
    if app.config.get('TESTING'):
        return None
    
    # Por ahora usar solo el limitador simple
    # En el futuro se puede integrar Redis + Flask-Limiter
    app.logger.info("Usando rate limiter simple en memoria")
    return None

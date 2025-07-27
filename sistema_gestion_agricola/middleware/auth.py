# middleware/auth.py
from functools import wraps
from flask import request, jsonify, session, current_app
import hashlib
import secrets
import time

class SimpleAuth:
    """Sistema de autenticación simple basado en sesiones"""
    
    def __init__(self):
        self.sessions = {}  # En producción usar Redis
        self.api_keys = {}  # API keys válidas
        
    def generate_api_key(self, identifier):
        """Genera una API key para un cliente"""
        api_key = secrets.token_urlsafe(32)
        self.api_keys[api_key] = {
            'identifier': identifier,
            'created': time.time(),
            'last_used': time.time()
        }
        return api_key
    
    def validate_api_key(self, api_key):
        """Valida una API key"""
        if api_key in self.api_keys:
            self.api_keys[api_key]['last_used'] = time.time()
            return True
        return False
    
    def create_session(self, user_id):
        """Crea una sesión de usuario"""
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = {
            'user_id': user_id,
            'created': time.time(),
            'last_activity': time.time()
        }
        return session_token
    
    def validate_session(self, session_token):
        """Valida una sesión"""
        if session_token not in self.sessions:
            return False
            
        session_data = self.sessions[session_token]
        
        # Verificar expiración (24 horas)
        if time.time() - session_data['last_activity'] > 86400:
            del self.sessions[session_token]
            return False
        
        # Actualizar última actividad
        session_data['last_activity'] = time.time()
        return True
    
    def revoke_session(self, session_token):
        """Revoca una sesión"""
        if session_token in self.sessions:
            del self.sessions[session_token]

# Instancia global
auth_manager = SimpleAuth()

def require_auth(f):
    """Decorator que requiere autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar API key en headers
        api_key = request.headers.get('X-API-Key')
        if api_key and auth_manager.validate_api_key(api_key):
            return f(*args, **kwargs)
        
        # Verificar sesión
        session_token = request.headers.get('Authorization')
        if session_token and session_token.startswith('Bearer '):
            token = session_token.split(' ')[1]
            if auth_manager.validate_session(token):
                return f(*args, **kwargs)
        
        # Verificar sesión de Flask
        if 'user_session' in session and auth_manager.validate_session(session['user_session']):
            return f(*args, **kwargs)
        
        return jsonify({
            'status': 'error',
            'message': 'Autenticación requerida',
            'error_code': 401
        }), 401
    
    return decorated_function

def require_admin(f):
    """Decorator que requiere permisos de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Por ahora, solo verificar autenticación
        # En el futuro implementar roles
        return require_auth(f)(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """Decorator que permite autenticación opcional"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Añadir información de usuario si está autenticado
        request.is_authenticated = False
        
        api_key = request.headers.get('X-API-Key')
        if api_key and auth_manager.validate_api_key(api_key):
            request.is_authenticated = True
        
        session_token = request.headers.get('Authorization')
        if session_token and session_token.startswith('Bearer '):
            token = session_token.split(' ')[1]
            if auth_manager.validate_session(token):
                request.is_authenticated = True
        
        return f(*args, **kwargs)
    
    return decorated_function
